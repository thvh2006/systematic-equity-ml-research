#!/usr/bin/env python3
"""Build review deliverables from saved results; never refit or overwrite holdout."""
import csv, hashlib, html, importlib.util, json, math, sys, zipfile
from pathlib import Path
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.chart import LineChart, Reference

R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R/'src'))
from equity_research.statistics import metrics
from equity_research.data import load_market
from equity_research.ledger import run_ledger

def read(name): return json.loads((R/name).read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def audit():
    spec=importlib.util.spec_from_file_location('research_runner',R/'scripts/run_research.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    f=read('artifacts/research/freeze.json');p=read('artifacts/research/locked.json')
    checks={
        'frozen_engine':module.codehash()==f['code_sha256']==p['code_sha256'],
        'frozen_config':sha(R/'configs/research.json')==f['config_sha256']==p['config_sha256'],
        'frozen_data':sha(R/'data/private/market_2017_2025.csv')==f['dataset_sha256']==p['dataset_sha256'],
        'frozen_development':sha(R/'artifacts/research/development.json')==f['development_sha256'],
        'freeze_reference':sha(R/'artifacts/research/freeze.json')==p['freeze_sha256'],
        'selection':p['chosen_model']==f['chosen_model'],
    }
    for name,result in p['results'].items():
        recalculated=metrics(result)
        checks['metrics_'+name]=all(abs(recalculated[k]-v)<1e-9 for k,v in p['metrics'][name].items())
        checks['nav_'+name]=all(abs(x['nav']-x['cash']-x['market_value']-x['dividend_receivable'])<1e-7 for x in result['ledger'])
    checks['temporal_fits']=all(x['max_label_end']<x['signal_date']<x['fill_date'] for x in p['fits'])
    v=read('artifacts/research/review_case.json')
    for name,nav,fee,expected in [('base',v['initial_nav'],v['fee_bps'],v['python_ledger']),('fee_plus20',v['initial_nav'],v['fee_bps']+20,v['counterfactuals']['fee_plus20']['ledger']),('nav_double',2*v['initial_nav'],v['fee_bps'],v['counterfactuals']['nav_double']['ledger'])]:
        cash=nav;market=0
        for a in v['assets']:
            px=a['raw_open']*(1+v['slippage_bps']/10000)
            q=min(math.floor(nav*a['target_weight']/a['raw_open']),math.floor(a['volume']*v['participation']),math.floor(max(0,cash)/(px*(1+fee/10000))))
            cash-=q*px*(1+fee/10000);market+=q*a['raw_close']
        checks['independent_rebalance_'+name]=abs(cash-expected['cash'])<1e-7 and abs(cash+market-expected['nav'])<1e-7
    if not all(checks.values()): raise RuntimeError(checks)
    return checks

def workbook(b):
    w=Workbook();w.remove(w.active)
    def sheet(name,headers,rows):
        s=w.create_sheet(name);s.append(headers)
        for row in rows:s.append(row)
        s.freeze_panes='B2';s.auto_filter.ref=s.dimensions
        for cell in s[1]:cell.fill=PatternFill('solid',fgColor='17374B');cell.font=Font(color='FFFFFF',bold=True)
        for col in s.columns:s.column_dimensions[col[0].column_letter].width=min(65,max(18,max(len(str(x.value or '')) for x in list(col)[:80])+2))
        s.sheet_view.showGridLines=False
        return s
    sheet('Read Me',['Item','Explanation'],[
        ['P2','Systematic Equity & ML — retrospective research'],['Study','Nine selected sector ETFs; SPY benchmark; saved test 2023–2025'],
        ['Result',b['conclusion']],['Use','Start with Comparison, then Costs, Monthly and Execution Lab.'],
        ['Blue inputs','Edit Execution Lab B2:B5; Excel recalculates whole-share orders sequentially.'],
        ['Limit','Historical corrected/rounded feed; fixed funds; assumed trading costs; zero cash return.'],
        ['Forward','Snapshot ends 2025-12-31; no current signal or forward returns.'],
        ['Verification','Formula structure and independent Python cases checked; native Excel recalculation pending.']])
    keys=['cagr','total_return','annual_volatility','sharpe_zero_cash','max_drawdown','annual_oneway_turnover','fees','slippage','final_nav']
    s=sheet('Comparison',['Strategy']+keys,[[n]+[r['metrics'][k] for k in keys] for n,r in b['results'].items()])
    for row in s.iter_rows(min_row=2):
        for c in row[1:4]:c.number_format='0.00%'
        row[5].number_format='0.00%'
    sheet('Development',['Trial','CAGR','Sharpe','Selected'],[[n,m['cagr'],m['sharpe_zero_cash'],n==b['selected']] for n,m in b['development_metrics'].items()])
    sheet('Costs',['Scenario']+keys,[[n]+[m[k] for k in keys] for n,m in b['stress'].items()])
    names=list(b['results']);months=sorted(next(iter(b['results'].values()))['monthly'])
    s=sheet('Monthly',['Month']+names,[[d]+[b['results'][n]['monthly'][d] for n in names] for d in months])
    for row in s.iter_rows(min_row=2,min_col=2):
        for c in row:c.number_format='0.00%'
    ledger=next(iter(b['results'].values()))['ledger']
    s=sheet('NAV',['Date']+names,[[row['date']]+[b['results'][n]['ledger'][i]['nav'] for n in names] for i,row in enumerate(ledger)])
    ch=LineChart();ch.title='Saved test NAV | initial $100,000';ch.add_data(Reference(s,min_col=2,max_col=1+len(names),min_row=1,max_row=s.max_row),titles_from_data=True);ch.set_categories(Reference(s,min_col=1,min_row=2,max_row=s.max_row));ch.width=26;ch.height=13;s.add_chart(ch,'H2')
    u=b['uncertainty'];sheet('Uncertainty',['Statistic','Value'],list(u.items()))
    sheet('Fit Windows',['Model','Signal','Fill','Latest label end','Train rows','Train dates'],[[x[k] for k in ['model','signal_date','fill_date','max_label_end','fit_rows','fit_dates']] for x in b['fits']])
    rows=[]
    for n,r in b['results'].items():
        for t in r['trades']:rows.append([n]+[t[k] for k in ['signal_date','fill_date','asset','side','quantity','execution_price','fee','status']])
    sheet('Trades',['Strategy','Signal','Fill','Asset','Side','Quantity','Execution price','Fee','Status'],rows)
    v=b['review'];s=w.create_sheet('Execution Lab');s.append(['First rebalance',v['fill_date']]);
    for label,value in [('Initial NAV',v['initial_nav']),('Fee bps',v['fee_bps']),('Slippage bps',v['slippage_bps']),('Participation',v['participation'])]:s.append([label,value])
    for i in range(2,6):s.cell(i,2).font=Font(color='0066CC')
    headers=['Asset','Weight','Raw open','Raw close','Prior volume','Target qty','Capacity','Exec price','Cash before','Quantity','Fee','Cash after','Close value']
    for j,h in enumerate(headers,1):s.cell(7,j,h)
    for i,a in enumerate(v['assets'],8):
        for j,k in enumerate(['asset','target_weight','raw_open','raw_close','volume'],1):s.cell(i,j,a[k])
        formulas={6:f'=ROUNDDOWN($B$2*B{i}/C{i},0)',7:f'=ROUNDDOWN(E{i}*$B$5,0)',8:f'=C{i}*(1+$B$4/10000)',9:'=$B$2' if i==8 else f'=L{i-1}',10:f'=MIN(F{i},G{i},ROUNDDOWN(MAX(0,I{i})/(H{i}*(1+$B$3/10000)),0))',11:f'=J{i}*H{i}*$B$3/10000',12:f'=I{i}-J{i}*H{i}-K{i}',13:f'=J{i}*D{i}'}
        for j,f in formulas.items():s.cell(i,j,f)
    s['A19']='Closing NAV';s['B19']='=L16+SUM(M8:M16)';s['A20']='Saved Python NAV';s['B20']=v['python_ledger']['nav'];s['A21']='Difference after recalculation';s['B21']='=B19-B20'
    s['A23']='Changing inputs changes the scenario; saved Python NAV stays fixed.';s.freeze_panes='C8'
    for col in range(1,14):s.column_dimensions[chr(64+col)].width=19
    sheet('Sources',['Item','Value'],[['As of',b['as_of']],['Status',b['status']],['Private raw source hashes',str(b['data']['source_history_sha256'])],['Freeze engine',b['freeze']['code_sha256']],['Source details','See docs/SOURCES_AND_LIMITATIONS.md'],['Fee/slippage','1 bp / 5 bp per side; analyst assumptions'],['Cash','Zero return; no separate tax model']])
    path=R/'deliverables/P2_Systematic_Equity_Research.xlsx';w.save(path)
    restored=load_workbook(path);assert len(restored.sheetnames)==11
    return path

def dashboard(b):
    rows=''.join('<tr><td>'+html.escape(n)+'</td>'+''.join(f'<td>{m[k]:.2%}</td>' for k in ['cagr','annual_volatility','max_drawdown'])+f"<td>{m['sharpe_zero_cash']:.2f}</td></tr>" for n,r in b['results'].items() for m in [r['metrics']])
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>P2 | Systematic Equity Research</title><style>body{font:16px system-ui;color:#163346;background:#f4f7fa;max-width:1160px;margin:40px auto;padding:24px}h1{font-size:40px}p{line-height:1.6}.tag{color:#9b4c12}section{background:white;padding:24px;margin:20px 0;border-radius:12px}table{width:100%;border-collapse:collapse}td,th{text-align:right;border-bottom:1px solid #d9e3e9;padding:12px}td:first-child,th:first-child{text-align:left}svg{width:100%;height:auto}select{padding:8px}small{color:#526d7a}@media(max-width:650px){body{margin:0;padding:12px}section{overflow:auto;padding:16px}h1{font-size:30px}}</style><h1>Systematic Equity & ML</h1><p class="tag">RETROSPECTIVE RESEARCH · Test 2023–2025 · No live signal</p><section><h2>Did bounded ML add value?</h2><p>CONCLUSION</p><small>Selected on development 2020–2022: 24 boosted decision stumps. Six trials. Fixed nine-fund universe; SPY benchmark.</small></section><section><h2>Saved test comparison, after assumed costs</h2><table><tr><th>Strategy</th><th>CAGR</th><th>Volatility</th><th>Max drawdown</th><th>Sharpe, zero cash</th></tr>ROWS</table></section><section><h2>Explore saved NAV</h2><select id="strategy"></select><svg id="chart" viewBox="0 0 960 300" role="img" aria-label="Selected saved strategy NAV"></svg><p id="detail"></p><small>Initial $100,000. Selection loads saved results; it does not fit a model or fetch prices.</small></section><section><h2>Uncertainty and limits</h2><p>INTERVAL</p><p>Snapshot ends 2025-12-31. Corrected, rounded historical prices; fixed selected funds; assumed 1 bp fee and 5 bp slippage per side. Prior daily volume is a capacity proxy. Zero cash return. No institutional feed or broker-execution validation.</p><p>Forward observations: 0. Data is stale for current trading.</p></section><script>const bundle=DATA;const sel=document.getElementById('strategy');for(const n of Object.keys(bundle.results)){const o=document.createElement('option');o.value=n;o.textContent=n;sel.append(o)}sel.value=bundle.selected;function draw(){const r=bundle.results[sel.value],v=[100000,...r.ledger.map(x=>x.nav)],lo=Math.min(...v)*.97,hi=Math.max(...v)*1.03;const pts=v.map((y,i)=>`${60+i/(v.length-1)*870},${260-(y-lo)/(hi-lo)*230}`).join(' ');document.getElementById('chart').innerHTML=`<text x="5" y="24">$${Math.round(hi).toLocaleString()}</text><text x="5" y="280">$${Math.round(lo).toLocaleString()}</text><polyline points="${pts}" fill="none" stroke="#087e8b" stroke-width="2"/><text x="60" y="298">${r.ledger[0].date}</text><text x="820" y="298">${r.ledger.at(-1).date}</text>`;document.getElementById('detail').textContent=`${sel.value}: final NAV $${r.metrics.final_nav.toLocaleString(undefined,{maximumFractionDigits:2})}; total net return ${(100*r.metrics.total_return).toFixed(2)}%.`}sel.addEventListener('change',draw);draw();</script></html>'''
    u=b['uncertainty'];page=page.replace('CONCLUSION',html.escape(b['conclusion'])).replace('ROWS',rows).replace('INTERVAL',f"ML minus momentum: mean paired monthly difference {u['mean_monthly_net_difference']:.3%}; 95% circular block-bootstrap interval [{u['ci95_low']:.3%}, {u['ci95_high']:.3%}], {u['paired_months']} months. The interval includes zero.").replace('DATA',json.dumps(b).replace('</','<\\/'))
    path=R/'deliverables/P2_Systematic_Equity_Research.html';path.write_text(page);return path

def notebook(b,checks):
    cells=[]
    def md(t):cells.append(dict(cell_type='markdown',metadata={},source=t.splitlines(True)))
    def code(t):
        import contextlib,io
        stream=io.StringIO()
        with contextlib.redirect_stdout(stream):exec(compile(t,'review-notebook','exec'),namespace)
        cells.append(dict(cell_type='code',metadata={},source=t.splitlines(True),execution_count=sum(x['cell_type']=='code' for x in cells)+1,outputs=[dict(output_type='stream',name='stdout',text=stream.getvalue().splitlines(True))]))
    namespace={};md('# P2 — Saved locked-test review\nRetrospective research. These cells read saved artifacts; they do not rerun model selection or the holdout. Run from the repository root or notebooks directory. Private input prices are needed only to reproduce the earlier training pipeline.\n')
    code("from pathlib import Path\nimport json\nr = Path.cwd()\nif not (r/'artifacts/research').exists(): r=r.parent\nb=json.loads((r/'artifacts/research/public_bundle.json').read_text())\nprint(b['status'], b['as_of'], b['selected'])")
    code("for name, result in b['results'].items():\n m=result['metrics']\n print(name, 'CAGR', round(100*m['cagr'],2), 'Sharpe',round(m['sharpe_zero_cash'],3), 'MDD',round(100*m['max_drawdown'],2))")
    md('## Development selection\nAll six candidates remain visible. Only the development-selected candidate enters the saved test comparison.')
    code("for name,m in b['development_metrics'].items(): print(name,round(m['sharpe_zero_cash'],4),name==b['selected'])")
    code("print(json.dumps(b['uncertainty'],indent=2))\nprint(b['conclusion'])")
    code("assert all(x['max_label_end'] < x['signal_date'] < x['fill_date'] for x in b['fits'])\nprint('Temporal fit windows checked:',len(b['fits']))\nfor n,result in b['results'].items():\n residual=max(abs(x['nav']-x['cash']-x['market_value']-x['dividend_receivable']) for x in result['ledger'])\n assert residual < 1e-7\n print(n, 'NAV residual', residual)")
    code("for name,m in b['stress'].items(): print(name, round(100*m['cagr'],2),round(m['sharpe_zero_cash'],3))")
    md('## First rebalance\nThe workbook provides independent formulas for a cash-only initial rebalance. It does not replicate the complete walk-forward model or all corporate-action accounting.')
    code("v=b['review'];cash=v['initial_nav'];market=0\nfor a in v['assets']:\n px=a['raw_open']*(1+v['slippage_bps']/10000)\n q=min(int(v['initial_nav']*a['target_weight']/a['raw_open']),int(a['volume']*v['participation']),int(max(0,cash)/(px*(1+v['fee_bps']/10000))))\n cash-=q*px*(1+v['fee_bps']/10000);market+=q*a['raw_close']\n print(a['asset'],q)\nassert abs(cash+market-v['python_ledger']['nav'])<1e-7\nprint('NAV:',cash+market,'cash:',cash)")
    code("print(json.dumps(b['paper'],indent=2))\nprint('No prospective track record or current trading signal.')")
    for i,c in enumerate(cells):c['id']=f'review-{i:02}'
    path=R/'notebooks/07_locked_test_and_attribution.ipynb';path.write_text(json.dumps(dict(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}},nbformat=4,nbformat_minor=5),indent=2)+'\n');return path

def main():
    checks=audit();b=read('artifacts/research/public_bundle.json');outputs=[workbook(b),dashboard(b),notebook(b,checks)]
    receipt={'checks':checks,'passed':len(checks),'locked_result_sha256':sha(R/'artifacts/research/locked.json'),'outputs':[{'path':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size} for p in outputs],'native_excel_recalculation':False,'native_jupyter_kernel':False,'browser_render_review':False}
    (R/'artifacts/research/delivery_audit.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()

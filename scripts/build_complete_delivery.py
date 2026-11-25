#!/usr/bin/env python3
"""Build extended research workbook and self-contained dashboard from saved runs."""
import importlib.util,json,sys
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.styles import Font,PatternFill,Alignment
R=Path(__file__).resolve().parents[1]
def main():
 spec=importlib.util.spec_from_file_location('base_delivery',R/'scripts/build_research_delivery.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
 checks=base.audit();b=json.loads((R/'artifacts/research/public_bundle.json').read_text());a=b['analysis'];base.workbook(b);w=load_workbook(R/'deliverables/P2_Systematic_Equity_Research.xlsx')
 def sheet(name,head,rows):
  s=w.create_sheet(name);s.append(head)
  for row in rows:s.append(row)
  s.freeze_panes='B2';s.auto_filter.ref=s.dimensions;s.sheet_view.showGridLines=False
  for col in s.columns:s.column_dimensions[col[0].column_letter].width=min(65,max(18,max(len(str(x.value or '')) for x in list(col)[:100])+2))
  for cell in s[1]:cell.fill=PatternFill('solid',fgColor='17374B');cell.font=Font(color='FFFFFF',bold=True)
  return s
 sheet('Universe and Coverage',['Fund','Role','Start','End','Sessions'],[[n,'Benchmark' if n=='SPY' else 'Fixed sector fund',b['data']['start'],b['data']['end'],b['data']['audit']['sessions']] for n in b['config']['universe']+['SPY']])
 s=sheet('Feature Register',['Feature','Definition','Availability','Fit scope'],[[k,v,'Signal close; timestamp 16:15 New York','Learned scaling/cuts fitted on matured training rows'] for k,v in a['feature_register'].items()]);s.column_dimensions['B'].width=64
 for row in s.iter_rows(min_row=2):
  for c in row:c.alignment=Alignment(wrap_text=True,vertical='top')
  s.row_dimensions[row[0].row].height=44
 p=json.loads((R/'artifacts/research/locked.json').read_text());signals=p['plans'][b['selected']]
 sheet('Signal Snapshot',['Model','Signal','Intended fill','Target fund','Target weight'],[[b['selected'],x['signal_date'],x['fill_date'],n,v] for x in signals for n,v in x['weights'].items()])
 rows=[]
 for n,x in a['strategies'].items():
  for e in x['exposures']:
   if e['date'][:7]!=x['exposures'][min(len(x['exposures'])-1,x['exposures'].index(e)+1)]['date'][:7] or e is x['exposures'][-1]:
    rows.extend([n,e['date'],asset,v] for asset,v in e['weights'].items());rows.append([n,e['date'],'cash',e['cash_weight']])
 sheet('Month End Holdings',['Strategy','Date','Asset','Market weight'],rows)
 sheet('Attribution',['Strategy','Fund','Net P&L dollars','Mean market weight'],[[n,k,v,x['mean_weights'][k]] for n,x in a['strategies'].items() for k,v in x['cumulative_net_pnl_by_asset'].items()])
 s=sheet('Annual Returns',['Strategy','2023','2024','2025'],[[n]+[x['annual_returns'][y] for y in ['2023','2024','2025']] for n,x in a['strategies'].items()])
 for row in s.iter_rows(min_row=2,min_col=2):
  for cell in row:cell.number_format='0.00%'
 sheet('Drawdowns',['Date']+list(a['strategies']),[[x['date']]+[a['strategies'][n]['daily'][i]['drawdown'] for n in a['strategies']] for i,x in enumerate(next(iter(a['strategies'].values()))['daily'])])
 sheet('Paper Monitor',['Control','Value'],list(b['paper'].items())+[['Current orders submitted',False],['Live refresh configured',False]])
 # Add independent compounded return formulas using monthly observations.
 s=w['Monthly'];end=s.max_row
 s.cell(end+2,1,'Compounded net return')
 for j in range(2,7):
  letter=s.cell(1,j).column_letter;s.cell(end+2,j,'=PRODUCT('+','.join(f'1+{letter}{i}' for i in range(2,end+1))+')-1')
 w['Read Me'].append(['Extended review','19 sheets; monthly holdings, fund contribution, signal dates, annual returns, drawdowns and stale-data control.'])
 w.save(R/'deliverables/P2_Systematic_Equity_Research.xlsx')
 template=(R/'dashboard/research.html').read_text();page=template.replace('__BUNDLE__',json.dumps(b,separators=(',',':')).replace('</','<\\/'))
 (R/'deliverables/P2_Systematic_Equity_Research.html').write_text(page);(R/'index.html').write_text(page)
 print(json.dumps({'workbook_sheets':len(w.sheetnames),'frozen_checks_passed':len(checks),'dashboard_views':8,'html_bytes':len(page.encode())}))
if __name__=='__main__':main()

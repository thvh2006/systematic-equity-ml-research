#!/usr/bin/env python3
"""Create compact derived, public review artifacts without bulk provider records."""
import json,csv,sys,datetime as dt,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'src'))
from equity_research.data import load_market
from equity_research.ledger import run_ledger
from equity_research.statistics import monthly,returns
def main():
 d=json.loads((R/'artifacts/research/development.json').read_text());p=json.loads((R/'artifacts/research/locked.json').read_text());c=json.loads((R/'configs/research.json').read_text());f=json.loads((R/'artifacts/research/freeze.json').read_text());receipt=json.loads((R/'data/manifests/market_receipt.json').read_text());name=p['chosen_model'];names=list(p['results'])
 # Nine observation sample only: independent first cash rebalance, not a redistributed full feed.
 rows=load_market(R/'data/private/market_2017_2025.csv');plan=p['plans'][name][0];dates=sorted({r['date'] for r in rows});fill=plan['fill_date'];previous=dates[dates.index(fill)-1];bars={(r['date'],r['asset']):r for r in rows};assets=[]
 for a in c['universe']:
  bar=bars[fill,a];assets.append(dict(asset=a,target_weight=plan['weights'].get(a,0),raw_open=bar['open'],raw_close=bar['close'],volume=bars[previous,a]['volume']))
 selected=[r for r in rows if r['asset'] in c['universe'] and previous<=r['date']<=fill]
 def run(nav,fee):return run_ledger(selected,[plan],initial_nav=nav,fee_bps=fee,slippage_bps=c['slippage_bps'],participation=c['participation'],capacity_lag_sessions=1)
 base=run(c['initial_nav'],c['fee_bps']);review=dict(initial_nav=c['initial_nav'],fee_bps=c['fee_bps'],slippage_bps=c['slippage_bps'],participation=c['participation'],signal_date=plan['signal_date'],fill_date=fill,assets=assets,python_ledger=base['ledger'][-1],python_trades=base['trades'],capacity='Prior-session conservative volume proxy',counterfactuals={})
 for label,nav,fee in [('fee_plus20',c['initial_nav'],c['fee_bps']+20),('nav_double',c['initial_nav']*2,c['fee_bps'])]:
  rr=run(nav,fee);review['counterfactuals'][label]={'ledger':rr['ledger'][-1],'trades':rr['trades']}
 compact_results={}
 for k,r in p['results'].items():compact_results[k]={'metrics':p['metrics'][k],'ledger':r['ledger'],'trades':[{kk:vv for kk,vv in t.items() if kk!='raw_open'} for t in r['trades']],'monthly':monthly(returns(r['ledger'],c['initial_nav']))}
 bundle={'title':'Systematic Equity & ML Research','version':'0.2.0','status':'REAL DATA · RETROSPECTIVE EXPLORATORY','as_of':receipt['end'],'built_at':dt.datetime.now(dt.timezone.utc).isoformat(),'data':receipt,'config':c,'freeze':f,'selected':name,'development_metrics':d['metrics'],'results':compact_results,'stress':{k:v['metrics'] for k,v in p['stress'].items()},'diagnostics':p['diagnostics'],'fits':[{k:v for k,v in q.items() if k!='parameters'} for q in p['fits']],'uncertainty':p['paired_uncertainty'],'beta':p['benchmark_beta'],'mean_exposure':p['mean_gross_exposure'],'review':review,'paper':{'status':'BLOCKED_STALE_DATA','realised_forward_sessions':0,'signals_published':0,'message':'Historical snapshot ends2025-12-31. No current trade signal or prospective performance is available.'},'conclusion':'The selected ML model did not outperform momentum or equal-weight in the locked sample. The paired interval includes zero; no established incremental edge and no trading promotion.','artifacts':{'excel':'P2_Systematic_Equity_Research.xlsx','notebook':'../notebooks/07_locked_test_and_attribution.ipynb','evidence':'../docs/RESEARCH_RELEASE_VI.md','sources':'../docs/SOURCES_AND_LIMITATIONS.md'}}
 (R/'artifacts/research/review_case.json').write_text(json.dumps(review,indent=2)+'\n');(R/'artifacts/research/public_bundle.json').write_text(json.dumps(bundle,separators=(',',':'))+'\n')
 with (R/'reports/plan/trial_register.csv').open('w',newline='') as out:
  fields=['model','family','configuration','development_sharpe','development_cagr','selected','locked_evaluated'];w=csv.DictWriter(out,fieldnames=fields);w.writeheader()
  for s in c['trial_budget']:w.writerow(dict(model=s['id'],family=s['family'],configuration=json.dumps(s),development_sharpe=d['metrics'][s['id']]['sharpe_zero_cash'],development_cagr=d['metrics'][s['id']]['cagr'],selected=s['id']==name,locked_evaluated=s['id']==name))
 print(json.dumps({'public_bundle_bytes':(R/'artifacts/research/public_bundle.json').stat().st_size,'first_rebalance_assets':len(assets),'selected':name}))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Bounded walk-forward study: development -> freeze -> one locked evaluation."""
import argparse,csv,hashlib,json,sys,subprocess,datetime as dt
from pathlib import Path
from collections import defaultdict
import numpy as np
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'src'))
from equity_research.data import load_market,market_panel
from equity_research.features import build_panel,FEATURES
from equity_research.models import matured_train
from equity_research.learners import fit,predict
from equity_research.ledger import run_ledger
from equity_research.statistics import metrics,returns,monthly,block_bootstrap_difference,rank_ic
OUT=R/'artifacts/research';OUT.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def codehash():return hashlib.sha256(b''.join(p.relative_to(R).as_posix().encode()+p.read_bytes() for p in sorted((R/'src').rglob('*.py'))+[Path(__file__)])).hexdigest()
def save(name,value): (OUT/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def cap_weights(raw,cap=.35):
 total=sum(raw.values());w={k:v/total for k,v in raw.items()};fixed={}
 while any(v>cap+1e-12 for v in w.values()):
  over={k:cap for k,v in w.items() if v>cap};fixed.update(over);rem={k:v for k,v in w.items() if k not in over};budget=1-sum(fixed.values());s=sum(rem.values());w={k:v/s*budget for k,v in rem.items()}
 return {**fixed,**w}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('phase',choices=['development','freeze','locked']);a=p.parse_args();c=json.loads((R/'configs/research.json').read_text());receipt=json.loads((R/'data/manifests/market_receipt.json').read_text());rawpath=R/'data/private/market_2017_2025.csv'
 assert sha(rawpath)==receipt['normalized_sha256'];assert receipt['unresolved_action_discrepancies']==0
 if a.phase=='freeze':
  if (OUT/'freeze.json').exists():raise SystemExit('Freeze already exists; do not overwrite the research protocol')
  dev=json.loads((OUT/'development.json').read_text());assert dev['code_sha256']==codehash() and dev['config_sha256']==sha(R/'configs/research.json')
  candidates=dev['candidate_metrics'];chosen=max(c['trial_budget'],key=lambda s:candidates[s['id']]['sharpe_zero_cash'])['id']
  q=subprocess.run(['git','rev-parse','HEAD'],cwd=R,text=True,capture_output=True);commit=q.stdout.strip() if q.returncode==0 else 'NOT_COMMITTED'
  freeze={'frozen_at':dt.datetime.now(dt.timezone.utc).isoformat(),'chosen_model':chosen,'dataset_sha256':sha(rawpath),'code_sha256':codehash(),'config_sha256':sha(R/'configs/research.json'),'development_sha256':sha(OUT/'development.json'),'source_commit':commit,'candidate_budget':c['trial_budget'],'holdout':[c['locked_start'],c['locked_end']],'selection':c['selection'],'scope':'Retrospective real-data exploratory; frozen evaluation does not cure vintage, selection or execution limits'};save('freeze.json',freeze);print(json.dumps(freeze,indent=2));return
 if a.phase=='development' and (OUT/'freeze.json').exists():raise SystemExit('Development already frozen')
 if a.phase=='locked':
  if (OUT/'locked.json').exists():raise SystemExit('Locked evaluation already exists; read saved results instead of rerunning')
  freeze=json.loads((OUT/'freeze.json').read_text());assert freeze['dataset_sha256']==sha(rawpath) and freeze['code_sha256']==codehash() and freeze['config_sha256']==sha(R/'configs/research.json') and freeze['development_sha256']==sha(OUT/'development.json')
  specs=[s for s in c['trial_budget'] if s['id']==freeze['chosen_model']]
 else:specs=c['trial_budget']
 allrows=load_market(rawpath);equity=[r for r in allrows if r['asset'] in c['universe']];dates,assets,lookup=market_panel(equity);f,l=build_panel(equity,horizon=c['label_horizon'],signal_timezone='America/New_York');bydate=defaultdict(list)
 for row in f:bydate[row['date']].append(row)
 labels={(r['date'],r['asset']):r for r in l};start,end=(c['development_start'],c['development_end']) if a.phase=='development' else (c['locked_start'],c['locked_end'])
 names=['equal_weight','momentum_63','inverse_vol']+[s['id'] for s in specs];plans={k:[] for k in names};predictions=[];fits=[]
 for i in range(63,len(dates)-1):
  d=dates[i];filldate=dates[i+1]
  if d[:7]==filldate[:7] or not start<=filldate<=end:continue
  available=bydate[d];train=matured_train(f,l,i,c['embargo_sessions']);assert train and max(r['label_end'] for r in train)<d
  plans['equal_weight'].append(dict(signal_date=d,fill_date=filldate,weights={asset:1/len(assets) for asset in assets}))
  top=sorted(available,key=lambda r:(-r['momentum_63'],r['asset']))[:c['top_k']];plans['momentum_63'].append(dict(signal_date=d,fill_date=filldate,weights={r['asset']:1/c['top_k'] for r in top}))
  plans['inverse_vol'].append(dict(signal_date=d,fill_date=filldate,weights=cap_weights({r['asset']:1/max(r['volatility_20'],1e-6) for r in available},c['max_name_weight'])))
  for spec in specs:
   m=fit(train,spec);scores={r['asset']:predict(m,r) for r in available};chosen=sorted(scores,key=lambda x:(-scores[x],x))[:c['top_k']];plans[spec['id']].append(dict(signal_date=d,fill_date=filldate,weights={x:1/c['top_k'] for x in chosen}))
   fits.append(dict(model=spec['id'],signal_date=d,fill_date=filldate,max_label_end=max(r['label_end'] for r in train),fit_rows=len(train),fit_dates=len({r['date'] for r in train}),parameters=m))
   for r in available:
    lab=labels[d,r['asset']];target=lab['target'] if lab['status']=='MATURED' and lab['label_end']<=end else None
    predictions.append(dict(model=spec['id'],date=d,asset=r['asset'],score=scores[r['asset']],target=target,label_end=lab['label_end'],status='ELIGIBLE_FOR_DIAGNOSTIC' if target is not None else 'OUTSIDE_PHASE_OR_UNMATURED'))
  print('FIT',a.phase,d,'models',len(specs),'rows',len(train),flush=True)
 # Include the session immediately before the first fill so volume capacity uses known prior data.
 firstfill=min(p['fill_date'] for p in next(iter(plans.values())));first_i=dates.index(firstfill);warm=dates[first_i-1];window=[r for r in equity if warm<=r['date']<=end]
 def replay(rows,pp,mult=1):return run_ledger(rows,pp,initial_nav=c['initial_nav'],fee_bps=c['fee_bps']*mult,slippage_bps=c['slippage_bps']*mult,participation=c['participation'],capacity_lag_sessions=1)
 def trim(result):
  result['ledger']=[r for r in result['ledger'] if r['date']>=firstfill];return result
 results={};summary={}
 for name,pp in plans.items():
  result=trim(replay(window,pp));results[name]=result;summary[name]=metrics(result,c['initial_nav'])
 spy=[r for r in allrows if r['asset']==c['benchmark'] and warm<=r['date']<=end];spy_plan=[dict(signal_date=warm,fill_date=firstfill,weights={c['benchmark']:1.})];results['SPY_buy_hold']=trim(replay(spy,spy_plan));summary['SPY_buy_hold']=metrics(results['SPY_buy_hold'],c['initial_nav'])
 diagnostics=[]
 for spec in specs:
  pp=[r for r in predictions if r['model']==spec['id'] and r['target'] is not None]
  for day in sorted({r['date'] for r in pp}):
   v=[r for r in pp if r['date']==day];diagnostics.append(dict(model=spec['id'],date=day,rank_ic=rank_ic([r['score'] for r in v],[r['target'] for r in v]),assets=len(v)))
 payload={'phase':a.phase,'scope':'REAL_DATA_RETROSPECTIVE_EXPLORATORY','code_sha256':codehash(),'config_sha256':sha(R/'configs/research.json'),'dataset_sha256':sha(rawpath),'first_fill':firstfill,'end':end,'candidate_metrics':{s['id']:summary[s['id']] for s in specs},'metrics':summary,'fits':fits,'plans':plans,'predictions':predictions,'diagnostics':diagnostics,'results':results,'cash_return':0.,'native_broker_execution_verified':False,'prospective_paper_sessions':0,'data_limitations':receipt['limitations']+[receipt['precision'],receipt['volume_policy']]}
 if a.phase=='locked':
  chosen=freeze['chosen_model'];uncertainty=block_bootstrap_difference(monthly(returns(results[chosen]['ledger'],c['initial_nav'])),monthly(returns(results['momentum_63']['ledger'],c['initial_nav'])),block=c['bootstrap_block_months'],reps=c['bootstrap_repetitions'],seed=c['seed']);payload['chosen_model']=chosen;payload['paired_uncertainty']=uncertainty
  stress={}
  for name in [chosen,'momentum_63','equal_weight']:
   for mult in c['cost_multipliers']:
    rr=trim(replay(window,plans[name],mult));stress[f'{name}__cost{mult}']=dict(metrics=metrics(rr,c['initial_nav']),ledger=rr['ledger'])
   delayed=[{**p,'fill_date':dates[dates.index(p['fill_date'])+1]} for p in plans[name] if dates.index(p['fill_date'])+1<len(dates) and dates[dates.index(p['fill_date'])+1]<=end];rr=trim(replay(window,delayed));stress[name+'__delay1']=dict(metrics=metrics(rr,c['initial_nav']),ledger=rr['ledger'])
  payload['stress']=stress
  # Return comparison and exposure are descriptive, not factor-model alpha.
  rr=np.array([r['return'] for r in returns(results[chosen]['ledger'],c['initial_nav'])]);br=np.array([r['return'] for r in returns(results['SPY_buy_hold']['ledger'],c['initial_nav'])]);payload['benchmark_beta']=float(np.cov(rr,br,ddof=1)[0,1]/np.var(br,ddof=1));payload['mean_gross_exposure']=float(np.mean([r['market_value']/r['nav'] for r in results[chosen]['ledger']]))
  payload['freeze_sha256']=sha(OUT/'freeze.json')
 save(a.phase+'.json',payload);print(json.dumps({'phase':a.phase,'metrics':summary,'paired_uncertainty':payload.get('paired_uncertainty')},indent=2))
if __name__=='__main__':main()

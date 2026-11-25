#!/usr/bin/env python3
"""Run an explicitly synthetic integration build. Real research promotion stays gated."""
import argparse,csv,hashlib,json,sys,platform
import numpy as np
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'src'))
from equity_research.data import load_market,validate_market,market_panel,research_gate
from equity_research.features import build_panel,FEATURES
from equity_research.models import matured_train,fit_ridge,predict
from equity_research.ledger import run_ledger

def write_csv(path,rows):
 if not rows:return
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=rows[0],lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--fixture',action='store_true');args=parser.parse_args()
 if not args.fixture:raise SystemExit('Explicit --fixture required. No approved market-data snapshot is configured.')
 config=json.loads((R/'configs/foundation.json').read_text())
 manifest=json.loads((R/'data/manifests/fixture.json').read_text());path=R/'data/sample/synthetic_market.csv';assert hashlib.sha256(path.read_bytes()).hexdigest()==manifest['sha256']
 rows=load_market(path);audit=validate_market(rows);dates,assets,lookup=market_panel(rows);features,labels=build_panel(rows,horizon=config["label_horizon_sessions"]);bydate={d:[r for r in features if r['date']==d] for d in dates}
 plans={k:[] for k in ['equal_weight','momentum_21','ridge_alpha10']};fits=[];signals=[]
 for i in range(config["first_evaluation_session"],len(dates)-1):
  d=dates[i]
  if dates[i+1][:7]==d[:7]:continue
  available=[r for r in bydate[d] if lookup[d,r['asset']]['tradable']]
  train=matured_train(features,labels,i,gap_sessions=config["embargo_sessions"])
  model=fit_ridge(train,alpha=config["ridge_alpha"]);assert model['max_label_end']<d
  fits.append(dict(signal_date=d,fill_date=dates[i+1],**model));
  for strategy in plans:
   scores={r['asset']:0. if strategy=='equal_weight' else r['momentum_21'] if strategy=='momentum_21' else predict(model,r) for r in available}
   chosen=sorted(scores,key=lambda a:(-scores[a],a))[:len(scores) if strategy=='equal_weight' else config['top_k']]
   weights={a:1/len(chosen) for a in chosen};assert max(weights.values(),default=0)<=config["max_target_weight"]
   plans[strategy].append(dict(signal_date=d,fill_date=dates[i+1],weights=weights))
   for a,score in sorted(scores.items()):signals.append(dict(strategy=strategy,signal_date=d,fill_date=dates[i+1],asset=a,score=score,target_weight=weights.get(a,0)))
 out=R/'artifacts/foundation';out.mkdir(parents=True,exist_ok=True);results={}
 for strategy,plan in plans.items():
  for costs in config["cost_multipliers"]:
   key=f'{strategy}__cost{costs}';results[key]=run_ledger(rows,plan,initial_nav=config["initial_nav"],fee_bps=config["fee_bps"]*costs,slippage_bps=config["slippage_bps"]*costs,participation=config["max_volume_participation"])
 code_files=sorted((R/'src').rglob('*.py'))+[Path(__file__)]
 code_hash=hashlib.sha256(b''.join(p.relative_to(R).as_posix().encode()+p.read_bytes() for p in code_files)).hexdigest()
 config_hash=hashlib.sha256((R/'configs/foundation.json').read_bytes()).hexdigest()
 runid='fixture-'+hashlib.sha256((manifest['sha256']+code_hash+config_hash).encode()).hexdigest()[:12]
 payload=dict(run_id=runid,code_sha256=code_hash,config_sha256=config_hash,data_sha256=manifest['sha256'],runtime={'python':platform.python_version(),'numpy':np.__version__},config=config,status='SYNTHETIC_FOUNDATION_ONLY',research_gate=research_gate(manifest),data_audit=audit,label_status_counts=dict(Counter(r['status'] for r in labels)),walk_forward_fits=len(fits),strategies=list(plans),cost_multipliers=[1,2,3],results=results)
 (out/'results.json').write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n');(out/'fit_receipts.json').write_text(json.dumps(fits,indent=2)+'\n')
 write_csv(out/'signals.csv',signals);write_csv(out/'validation_windows.csv',[{k:r[k] for k in ['signal_date','fill_date','fit_rows','fit_dates','train_start','train_end','max_label_end','alpha']} for r in fits]);write_csv(out/'feature_labels.csv',[{**f,**l} for f,l in zip(features,labels)])
 selected=results['ridge_alpha10__cost1'];write_csv(out/'trade_blotter.csv',selected['trades']);write_csv(out/'cash_ledger.csv',[{k:v for k,v in r.items() if k!='holdings'} for r in selected['ledger']])
 print(json.dumps(dict(run_id=runid,status=payload['status'],data_rows=audit['rows'],walk_forward_fits=len(fits),scenario_runs=len(results),research_release=payload['research_gate']['status'],max_cash_difference=max(r['max_cash_difference'] for r in results.values())),indent=2))
if __name__=='__main__':main()

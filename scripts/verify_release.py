#!/usr/bin/env python3
"""Verify public derived evidence without provider data or any model fitting."""
import hashlib,importlib.util,json,math,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'src'))
from equity_research.statistics import metrics,returns,monthly,block_bootstrap_difference
def get(p):return json.loads((R/p).read_text())
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def main():
 f=get('artifacts/research/freeze.json');p=get('artifacts/research/locked.json');d=get('artifacts/research/development.json');b=get('artifacts/research/public_bundle.json');a=get('artifacts/research/analysis.json');c=b['config'];checks={}
 spec=importlib.util.spec_from_file_location('frozen_runner',R/'scripts/run_research.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 checks['original_engine_hash']=m.codehash()==f['code_sha256']==p['code_sha256'];checks['original_configuration']=sha('configs/research.json')==f['config_sha256']==p['config_sha256'];checks['development_hash']=sha('artifacts/research/development.json')==f['development_sha256'];checks['freeze_reference']=sha('artifacts/research/freeze.json')==p['freeze_sha256'];checks['data_hash_receipt']=get('data/manifests/market_receipt.json')['normalized_sha256']==f['dataset_sha256']==p['dataset_sha256']
 checks['selection']=max(c['trial_budget'],key=lambda s:d['metrics'][s['id']]['sharpe_zero_cash'])['id']==f['chosen_model']==b['selected']==p['chosen_model']
 checks['fit_timing']=all(x['max_label_end']<x['signal_date']<x['fill_date'] for x in p['fits'])
 for n,r in p['results'].items():
  mm=metrics(r,c['initial_nav']);checks['metrics_'+n]=all(abs(mm[k]-v)<1e-9 for k,v in p['metrics'][n].items());checks['public_metrics_'+n]=all(abs(mm[k]-v)<1e-9 for k,v in b['results'][n]['metrics'].items())
  checks['nav_'+n]=all(abs(x['cash']+x['market_value']+x['dividend_receivable']-x['nav'])<1e-7 for x in r['ledger'])
  checks['public_path_'+n]=b['results'][n]['ledger']==r['ledger']
  checks['monthly_'+n]=monthly(returns(r['ledger'],c['initial_nav']))==b['results'][n]['monthly']
  x=a['strategies'][n];checks['attribution_'+n]=abs(sum(x['cumulative_net_pnl_by_asset'].values())-(r['final_nav']-c['initial_nav']))<1e-6 and all(abs(sum(v['contributions_dollars'].values())-rr['return']*(r['ledger'][i-1]['nav'] if i else c['initial_nav']))<1e-6 for i,(v,rr) in enumerate(zip(x['daily'],returns(r['ledger'],c['initial_nav']))))
  checks['exposure_'+n]=all(abs(sum(e['weights'].values())+e['cash_weight']+e['receivable_weight']-1)<1e-9 for e in x['exposures'])
 u=block_bootstrap_difference(b['results'][b['selected']]['monthly'],b['results']['momentum_63']['monthly'],block=c['bootstrap_block_months'],reps=c['bootstrap_repetitions'],seed=c['seed']);checks['paired_interval']=all(u[k]==p['paired_uncertainty'][k]==b['uncertainty'][k] for k in u)
 checks['cost0_label']=all(n+'__cost0' in p['stress'] for n in [b['selected'],'momentum_63','equal_weight']);checks['no_forward_claim']=b['paper']['realised_forward_sessions']==b['paper']['signals_published']==0
 for n,x in p['stress'].items():checks['stress_'+n]=x['metrics']==b['stress'][n]
 v=b['review']
 for label,nav,fee,expected in [('base',v['initial_nav'],v['fee_bps'],v['python_ledger']),('fee_plus20',v['initial_nav'],v['fee_bps']+20,v['counterfactuals']['fee_plus20']['ledger']),('nav_double',v['initial_nav']*2,v['fee_bps'],v['counterfactuals']['nav_double']['ledger'])]:
  cash=nav;mv=0
  for x in v['assets']:
   px=x['raw_open']*(1+v['slippage_bps']/1e4);q=min(math.floor(nav*x['target_weight']/x['raw_open']),math.floor(x['volume']*v['participation']),math.floor(max(cash,0)/(px*(1+fee/1e4))));cash-=q*px*(1+fee/1e4);mv+=q*x['raw_close']
  checks['independent_rebalance_'+label]=abs(cash-expected['cash'])<1e-7 and abs(cash+mv-expected['nav'])<1e-7
 for n in ['01_market_data_and_universe_audit','02_hypotheses_labels_and_features','03_baseline_strategy_research','04_temporal_ml_validation','05_portfolio_and_execution','06_robustness_and_multiple_testing','07_locked_test_and_attribution','08_forward_paper_monitor']:
  nb=get('notebooks/'+n+'.ipynb');checks['notebook_'+n]=all(x.get('execution_count') and not any(o['output_type']=='error' for o in x['outputs']) for x in nb['cells'] if x['cell_type']=='code')
 review_path=R/'artifacts/review/polish.json'
 if review_path.exists():
  review=get('artifacts/review/polish.json');checks['review_original_locked']=sha('artifacts/research/locked.json')==review['original_locked_sha256']
  for path,digest in review['sources'].items():checks['review_source_'+path]=sha(path)==digest
  for name,x in review['comparisons'].items():
   ml=b['results'][b['selected']];ref=b['results'][name];net=ml['metrics']['final_nav']-ref['metrics']['final_nav'];gross=b['stress'][b['selected']+'__cost0']['final_nav']-b['stress'][name+'__cost0']['final_nav']
   checks['review_bridge_'+name]=abs(x['net_nav_gap']-net)<1e-7 and abs(x['zero_cost_nav_gap']-gross)<1e-7 and abs(x['differential_friction_effect']-(net-gross))<1e-7
   checks['review_sector_'+name]=abs(sum(row['difference'] for row in x['sectors'])-net)<1e-6 and all(abs(row['difference']-(a['strategies'][b['selected']]['cumulative_net_pnl_by_asset'][row['asset']]-a['strategies'][name]['cumulative_net_pnl_by_asset'].get(row['asset'],0)))<1e-7 for row in x['sectors'])
   checks['review_relative_wealth_'+name]=len(x['relative_wealth'])==len(ml['ledger'])+1 and all(row['date']==l['date']==r['date'] and abs(row['relative_wealth']-(l['nav']/r['nav']-1))<1e-12 for row,l,r in zip(x['relative_wealth'][1:],ml['ledger'],ref['ledger']))
 manifest=R/'release_manifest.json'
 if manifest.exists():
  for x in get('release_manifest.json')['files']:checks['sha_'+x['path']]=sha(x['path'])==x['sha256']
 failed=[k for k,v in checks.items() if not v];print(json.dumps({'passed':len(checks)-len(failed),'total':len(checks),'failed':failed,'private_market_data_required':False,'model_refitted':False},indent=2))
 if failed:raise SystemExit(1)
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Post-study descriptions of saved outcomes. No fitting or policy selection."""
import hashlib,json,statistics,math
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def main():
 b=json.loads((R/'artifacts/research/public_bundle.json').read_text());a=b['analysis'];m=b['selected'];out={}
 for n in ['momentum_63','equal_weight']:
  ml=b['results'][m];ref=b['results'][n];net=ml['metrics']['final_nav']-ref['metrics']['final_nav'];gross=b['stress'][m+'__cost0']['final_nav']-b['stress'][n+'__cost0']['final_nav']
  months=sorted(ml['monthly']);excess=[ml['monthly'][d]-ref['monthly'][d] for d in months]
  sectors=[{'asset':k,'ml':v,'reference':a['strategies'][n]['cumulative_net_pnl_by_asset'].get(k,0),'difference':v-a['strategies'][n]['cumulative_net_pnl_by_asset'].get(k,0)} for k,v in a['strategies'][m]['cumulative_net_pnl_by_asset'].items()]
  assert abs(sum(x['difference'] for x in sectors)-net)<1e-6
  curve=[{'date':'2022-12-30','relative_wealth':0.}]+[{'date':x['date'],'relative_wealth':x['nav']/y['nav']-1} for x,y in zip(ml['ledger'],ref['ledger'])]
  out[n]={'comparator':n,'net_nav_gap':net,'zero_cost_nav_gap':gross,'differential_friction_effect':net-gross,'bridge_residual':net-gross-(net-gross),'sectors':sorted(sectors,key=lambda x:x['difference']),'months':months,'monthly_excess':excess,'positive_months':sum(x>0 for x in excess),'mean_monthly_excess':statistics.mean(excess),'monthly_excess_sd':statistics.stdev(excess),'tracking_error_annualized_monthly':statistics.stdev(excess)*math.sqrt(12),'relative_wealth':curve,'relative_terminal_wealth':curve[-1]['relative_wealth'],'mean_ml_exposure':statistics.mean(sum(x['weights'].values()) for x in a['strategies'][m]['exposures']),'mean_reference_exposure':statistics.mean(sum(x['weights'].values()) for x in a['strategies'][n]['exposures'])}
 result={'version':'0.4.0','review_date':'2026-11-25','scope':'Post-study descriptive review of the consumed 2023-2025 test. No strategy tuning, new holdout or causal attribution.','original_locked_sha256':sha('artifacts/research/locked.json'),'sources':{p:sha(p) for p in ['artifacts/research/public_bundle.json','artifacts/research/locked.json','artifacts/research/freeze.json']},'comparisons':out,'interpretation':{'momentum_63':'ML also trails momentum in the zero-cost rerun. Differential friction slightly narrows this gap, so extra trading costs alone do not explain the primary shortfall.','equal_weight':'ML trails equal weight before costs; its larger friction drag further widens that shortfall.','sector':'Differences in fund-level net dollar contributions reconcile the NAV gap. They combine differing holdings, timing and execution, and are not Brinson or causal selection effects.','curve':'Relative wealth is ML NAV divided by comparator NAV minus one; it differs from a difference of CAGRs and a sum of monthly excess returns.'}}
 p=R/'artifacts/review';p.mkdir(exist_ok=True);(p/'polish.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({n:{k:v[k] for k in ['net_nav_gap','zero_cost_nav_gap','differential_friction_effect','positive_months','relative_terminal_wealth']} for n,v in out.items()},indent=2))
if __name__=='__main__':main()

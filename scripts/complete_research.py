#!/usr/bin/env python3
"""Descriptive analysis of the SAVED study. No fitting, selection or test replay."""
import contextlib,csv,hashlib,io,json,math,os,sys
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'src'))
from equity_research.data import load_market
from equity_research.statistics import returns,monthly
FEATURES={
 'momentum_21':'21-session trailing distribution-inclusive wealth return',
 'momentum_63':'63-session trailing distribution-inclusive wealth return',
 'volatility_20':'Sample standard deviation of 20 daily wealth returns; not annualised',
 'drawdown_63':'Current wealth divided by maximum wealth in 64 observations, minus one',
 'log_dollar_volume_20':'log(1 + trailing 20-session mean raw close × capacity-proxy volume)'}
def get(p):return json.loads((R/p).read_text())
def put(p,v):(R/p).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def main():
 p=get('artifacts/research/locked.json');b=get('artifacts/research/public_bundle.json');c=b['config']
 bars={(x['date'],x['asset']):x for x in load_market(R/'data/private/market_2017_2025.csv')}
 analysis={'scope':'Post-evaluation descriptive accounting; no model or rule reselection','strategies':{},'feature_register':FEATURES}
 for name,result in p['results'].items():
  assets=sorted(result['ledger'][0]['holdings']);previous_mv={a:0 for a in assets};previous_q={a:0 for a in assets};cum={a:0. for a in assets};series=[];exposures=[];prior=c['initial_nav'];peak=prior;bydate={}
  for t in result['trades']:bydate.setdefault(t['fill_date'],[]).append(t)
  maxdiff=0
  for row in result['ledger']:
   day=row['date'];at={a:0. for a in assets};weights={}
   for a in assets:
    bar=bars[day,a];mv=row['holdings'][a]*bar['close'];entitlement=previous_q[a]*bar['split_factor']*bar['dividend'];redemption=previous_q[a]*bar['split_factor']*bar['delist_cash'] if not bar['active'] else 0
    at[a]=mv-previous_mv[a]+entitlement+redemption;previous_mv[a]=mv;previous_q[a]=row['holdings'][a];weights[a]=mv/row['nav']
   for t in bydate.get(day,[]):at[t['asset']]+=t['cash_change']
   residual=sum(at.values())-(row['nav']-prior);maxdiff=max(maxdiff,abs(residual))
   if abs(residual)>1e-6:raise ArithmeticError((name,day,residual))
   for a,v in at.items():cum[a]+=v
   peak=max(peak,row['nav']);series.append({'date':day,'drawdown':row['nav']/peak-1,'net_return':row['nav']/prior-1,'contributions_dollars':at});prior=row['nav'];exposures.append({'date':day,'weights':weights,'cash_weight':row['cash']/row['nav'],'receivable_weight':row['dividend_receivable']/row['nav']})
  annual={}
  for year in ['2023','2024','2025']:
   sub=[x['net_return'] for x in series if x['date'].startswith(year)];annual[year]=math.prod(1+x for x in sub)-1
  dd=min(series,key=lambda x:x['drawdown'])
  trade_notional=sum(t['notional'] for t in result['trades']);maxparticipation=0
  analysis['strategies'][name]={'annual_returns':annual,'cumulative_net_pnl_by_asset':cum,'attribution_max_daily_residual':maxdiff,'attribution_total_difference':sum(cum.values())-(result['final_nav']-c['initial_nav']),'drawdown_trough_date':dd['date'],'mean_weights':{a:float(np.mean([e['weights'][a] for e in exposures])) for a in assets},'max_realised_name_weight':max(v for e in exposures for v in e['weights'].values()),'rebalance_dates':len({t['fill_date'] for t in result['trades']}),'trade_count':len(result['trades']),'unfilled_or_partial_orders':sum(t['status']!='FILLED' for t in result['trades']),'daily':series,'exposures':exposures}
 ic=np.array([x['rank_ic'] for x in p['diagnostics'] if x['rank_ic'] is not None]);analysis['rank_ic']={'observations':len(ic),'mean':float(ic.mean()),'sample_sd':float(ic.std(ddof=1)),'mean_over_sd':float(ic.mean()/ic.std(ddof=1)),'annualisation':'Not annualised: overlapping 21-session labels and small date count','positive_fraction':float(np.mean(ic>0))}
 chosen=p['chosen_model'];features=list(FEATURES);stump_counts={f:0 for f in features}
 for fit in p['fits']:
  for stump in fit['parameters'].get('stumps',[]):stump_counts[features[stump['feature']]]+=1
 analysis['descriptive_stump_split_counts']={'counts':stump_counts,'interpretation':'Counts are diagnostics of saved fits; not causal importance, not a feature ablation.'}
 put('artifacts/research/analysis.json',analysis)
 with (R/'artifacts/research/sector_attribution.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['strategy','asset','net_pnl_dollars','mean_market_weight'])
  for n,x in analysis['strategies'].items():
   for a,v in x['cumulative_net_pnl_by_asset'].items():w.writerow([n,a,v,x['mean_weights'][a]])
 # Include only original derived information in the public bundle.
 b['analysis']=analysis;b['paper']['signals_published']=0;put('artifacts/research/public_bundle.json',b)
 print(json.dumps({'strategies':len(analysis['strategies']),'rank_ic':analysis['rank_ic'],'max_attribution_residual':max(x['attribution_max_daily_residual'] for x in analysis['strategies'].values())},indent=2))
 notebooks(b)

def notebooks(b):
 setup="from pathlib import Path\nimport json,sys\nr=Path.cwd()\nif not (r/'artifacts/research').exists(): r=r.parent\nsys.path.insert(0,str(r/'src'))\nb=json.loads((r/'artifacts/research/public_bundle.json').read_text())\na=b['analysis']\n"
 plans=[
 ('01_market_data_and_universe_audit','Market data and universe audit',[
  ('Data acceptance scope','print(json.dumps(b["data"],indent=2))'),
  ('Fixed fund wrappers, not historical sector membership','print("Sector funds:",b["config"]["universe"])\nprint("Benchmark:",b["config"]["benchmark"])\nassert b["data"]["audit"]["rows"]==b["data"]["audit"]["sessions"]*10\nprint("Rectangular panel: PASS. Raw feed remains private; no license inferred.")'),
  ('Corporate-action engineering tests; source reconciliation receipts are separate','from equity_research.ledger import run_ledger\nimport importlib.util\nspec=importlib.util.spec_from_file_location("econ",r/"tests/test_economics.py")\nm=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)\nm.test_hand_calculated_split_dividend_receivable_and_payment_preserve_nav()\nprint("Independent split/dividend receivable/pay-date example: PASS")')]),
 ('02_hypotheses_labels_and_features','Hypotheses, labels and availability',[
  ('Feature register','for k,v in a["feature_register"].items(): print(k,":",v)'),
  ('Trade and information timing','print("Signal: session close + conservative timestamp at 16:15 New York")\nprint("Fill: next-session opening mark; exit label: 21 sessions after entry")\nprint("Labels admitted only after maturity and one further session gap.")\nassert all(x["max_label_end"]<x["signal_date"]<x["fill_date"] for x in b["fits"])\nprint("Saved fit windows:",len(b["fits"]))'),
  ('Deliberate future-data perturbation','import importlib.util\nspec=importlib.util.spec_from_file_location("temporal",r/"tests/test_temporal.py")\nm=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)\nm.test_future_price_changes_cannot_change_earlier_features_or_ridge_predictions()\nprint("Future-price perturbation cannot alter earlier features/prediction: PASS")')]),
 ('03_baseline_strategy_research','Baseline comparison',[
  ('Baseline evidence','for n in ["equal_weight","momentum_63","inverse_vol","SPY_buy_hold"]:\n m=b["results"][n]["metrics"];print(n,"CAGR",round(m["cagr"],4),"Sharpe",round(m["sharpe_zero_cash"],4))'),
  ('Annual subperiods, descriptive','for n,x in a["strategies"].items(): print(n,x["annual_returns"])')]),
 ('04_temporal_ml_validation','Bounded model selection',[
  ('All trials and development-only selection','trials=b["config"]["trial_budget"]\nassert len(trials)==6\nfor x in trials: print(x,b["development_metrics"][x["id"]]["sharpe_zero_cash"])\nselected=max(trials,key=lambda x:b["development_metrics"][x["id"]]["sharpe_zero_cash"])["id"]\nassert selected==b["selected"]\nprint("Chosen:",selected)'),
  ('Saved diagnostics are not retuning inputs','print(a["rank_ic"])\nprint(a["descriptive_stump_split_counts"])\nprint("No post-test model search, ablation or feature reselection performed.")')]),
 ('05_portfolio_and_execution','Portfolio accounting and independent rebalance',[
  ('First cash rebalance; independently implemented','v=b["review"];cash=v["initial_nav"];mv=0\nfor x in v["assets"]:\n price=x["raw_open"]*(1+v["slippage_bps"]/10000)\n q=min(int(v["initial_nav"]*x["target_weight"]/x["raw_open"]),int(x["volume"]*v["participation"]),int(max(cash,0)/(price*(1+v["fee_bps"]/10000))))\n cash-=q*price*(1+v["fee_bps"]/10000);mv+=q*x["raw_close"]\n print(x["asset"],q)\nassert abs(cash+mv-v["python_ledger"]["nav"])<1e-7\nprint("NAV",cash+mv,"cash",cash)'),
  ('Asset P&L reconciliation','for n,x in a["strategies"].items():\n assert abs(x["attribution_total_difference"])<1e-6\n print(n,x["cumulative_net_pnl_by_asset"],x["attribution_max_daily_residual"])')]),
 ('06_robustness_and_multiple_testing','Costs, delay and uncertainty',[
  ('Predeclared saved stresses','for n,m in b["stress"].items(): print(n,"CAGR",round(m["cagr"],4),"Sharpe",round(m["sharpe_zero_cash"],4))'),
  ('Paired inference','print(json.dumps(b["uncertainty"],indent=2))\nassert b["uncertainty"]["ci95_low"]<0<b["uncertainty"]["ci95_high"]\nprint("No CSCV/PBO, multiple-testing correction, independent regime test or causal alpha claim.")')]),
 ('08_forward_paper_monitor','Forward paper readiness and stale-data control',[
  ('No fabricated forward performance','print(json.dumps(b["paper"],indent=2))\nassert b["paper"]["realised_forward_sessions"]==0\nassert b["paper"]["signals_published"]==0'),
  ('Staleness test at fixed reproducible wall clock','import datetime as dt,importlib.util\nspec=importlib.util.spec_from_file_location("monitor",r/"scripts/paper_monitor.py")\nm=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)\nstatus=m.check(b["as_of"],dt.datetime(2026,11,25,5,0,tzinfo=dt.timezone.utc))\nassert status["status"]=="BLOCKED_STALE_DATA" and not status["forecast_emitted"]\nprint(status)')])]
 old=os.getcwd();os.chdir(R)
 try:
  for stem,title,sections in plans:
   cells=[{'cell_type':'markdown','metadata':{},'source':[f'# {title}\n','Saved retrospective research. No training or held-out reselection. Run from the repository root or notebooks directory.\n']}];ns={}
   def add(code):
    stream=io.StringIO()
    with contextlib.redirect_stdout(stream):exec(compile(code,stem,'exec'),ns)
    cells.append({'cell_type':'code','metadata':{},'source':code.splitlines(True),'execution_count':sum(x['cell_type']=='code' for x in cells)+1,'outputs':[{'output_type':'stream','name':'stdout','text':stream.getvalue().splitlines(True)}]})
   add(setup)
   for heading,code in sections:cells.append({'cell_type':'markdown','metadata':{},'source':[f'## {heading}']});add(code)
   for i,x in enumerate(cells):x['id']=f'{stem[:2]}-{i:02}'
   put('notebooks/'+stem+'.ipynb',{'cells':cells,'metadata':{'kernelspec':{'name':'python3','display_name':'Python 3','language':'python'}},'nbformat':4,'nbformat_minor':5})
 finally:os.chdir(old)
if __name__=='__main__':main()

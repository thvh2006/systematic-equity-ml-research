import math
import numpy as np
from equity_research.calendar import sessions,available_timestamp
from equity_research.learners import fit,predict
from equity_research.features import FEATURES
from equity_research.statistics import rank_ic,block_bootstrap_difference
from equity_research.ledger import run_ledger
def toy():
 rows=[]
 for i,x in enumerate([-2.,-1.,1.,2.]):
  row={k:0. for k in FEATURES};row.update(date=f'2020-01-0{i+1}',label_end=f'2020-01-0{i+2}',target=1. if x>0 else -1.,momentum_21=x);rows.append(row)
 return rows
def test_stump_step_function_has_exact_one_tree_solution():
 rows=toy();m=fit(rows,{'family':'boosted_stumps','n_estimators':1,'learning_rate':1.})
 assert all(abs(predict(m,r)-r['target'])<1e-12 for r in rows)
def test_elastic_net_penalty_can_set_all_coefficients_to_zero():
 m=fit(toy(),{'family':'elastic_net','alpha':100.,'l1_ratio':.5});assert m['coef']==[0.]*len(FEATURES)
def test_elastic_net_single_coordinate_matches_soft_threshold_solution():
 rows=toy()
 for r in rows:r['target']=2*r['momentum_21']/math.sqrt(2.5)
 m=fit(rows,{'family':'elastic_net','alpha':.2,'l1_ratio':.5})
 assert abs(m['coef'][0]-(2-.1)/1.1)<1e-9
def test_nyse_calendar_includes_mourning_and_saturday_new_year_exceptions():
 assert sessions('2025-01-08','2025-01-10')==['2025-01-08','2025-01-10']
 assert '2021-12-31' in sessions('2021-12-30','2022-01-03')
 assert '2018-12-05' not in sessions('2018-12-04','2018-12-06')
 assert '2022-06-20' not in sessions('2022-06-17','2022-06-21')
def test_signal_timestamp_handles_dst_and_is_after_regular_close():
 assert available_timestamp('2025-01-10').endswith('16:15:00-05:00')
 assert available_timestamp('2025-07-10').endswith('16:15:00-04:00')
def test_prior_volume_capacity_does_not_depend_on_future_session_volume():
 def rows(v):return [dict(date=d,asset='A',open=10.,close=10.,volume=vol,split_factor=1.,dividend=0.,dividend_pay_date='',delist_cash=0.,active=True,tradable=True) for d,vol in [('2020-01-02',100),('2020-01-03',v)]]
 p=[dict(signal_date='2020-01-02',fill_date='2020-01-03',weights={'A':1.})]
 a=run_ledger(rows(100000),p,initial_nav=1000,fee_bps=0,slippage_bps=0,capacity_lag_sessions=1)
 b=run_ledger(rows(500000),p,initial_nav=1000,fee_bps=0,slippage_bps=0,capacity_lag_sessions=1)
 assert a['trades']==b['trades'] and a['trades'][0]['quantity']==1
def test_rank_ic_ties_and_bootstrap_constant_difference():
 assert abs(rank_ic([1,1,2],[1,1,2])-1)<1e-12
 a={f'2020-{i:02}':.02 for i in range(1,13)};b={k:.01 for k in a};r=block_bootstrap_difference(a,b,reps=100)
 assert abs(r['ci95_low']-.01)<1e-12 and abs(r['ci95_high']-.01)<1e-12

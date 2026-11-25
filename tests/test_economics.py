from copy import deepcopy
from equity_research.data import validate_market,forward_index,research_gate
from equity_research.ledger import run_ledger

def bar(day,price,**kw):
 row=dict(date=f'2022-01-{day:02}',asset='TEST',open=price,close=price,volume=100000,tradable=True,active=True,split_factor=1.,dividend=0.,dividend_pay_date='',delist_cash=0.);row.update(kw);return row

def plan():return [dict(signal_date='2022-01-01',fill_date='2022-01-02',weights={'TEST':1.})]
def raises(fn,text):
 try:fn()
 except (ValueError,ArithmeticError) as e:
  assert text in str(e);return
 raise AssertionError('Invalid case accepted')

def test_hand_calculated_split_dividend_receivable_and_payment_preserve_nav():
 rows=[bar(1,10),bar(2,10),bar(3,5,split_factor=2),bar(4,4,dividend=1,dividend_pay_date='2022-01-05'),bar(5,4)]
 result=run_ledger(rows,plan(),initial_nav=100,fee_bps=0,slippage_bps=0)
 assert result['ledger'][1]['holdings']['TEST']==10
 assert result['ledger'][2]['holdings']['TEST']==20
 assert result['ledger'][3]['cash']==0 and result['ledger'][3]['dividend_receivable']==20
 assert result['ledger'][4]['cash']==20 and result['ledger'][4]['dividend_receivable']==0
 assert all(abs(r['nav']-100)<1e-10 for r in result['ledger'])
 # The forward-only total-return feature index also avoids a false split/dividend crash.
 idx=forward_index(rows);assert all(abs(v-1)<1e-10 for v in idx.values())

def test_new_ex_dividend_buyer_does_not_receive_old_holders_distribution():
 rows=[bar(1,10),bar(2,9,dividend=1,dividend_pay_date='2022-01-03'),bar(3,9)]
 r=run_ledger(rows,plan(),initial_nav=90,fee_bps=0,slippage_bps=0)
 assert r['ledger'][-1]['dividend_cash_received']==0 and r['final_nav']==90

def test_delisting_settles_at_recovery_and_closes_position():
 rows=[bar(1,10),bar(2,10),bar(3,0,active=False,tradable=False,volume=0,delist_cash=6),bar(4,0,active=False,tradable=False,volume=0)]
 r=run_ledger(rows,plan(),initial_nav=100,fee_bps=0,slippage_bps=0)
 assert r['final_nav']==60 and r['ledger'][-1]['holdings']['TEST']==0
 assert r['ledger'][2]['delisting_cash']==60

def test_suspended_asset_is_not_filled_and_order_expires():
 rows=[bar(1,10),bar(2,10,tradable=False,volume=0),bar(3,10)]
 r=run_ledger(rows,plan(),initial_nav=100,fee_bps=0,slippage_bps=0)
 assert r['final_nav']==100 and r['ledger'][-1]['holdings']['TEST']==0
 assert r['trades'][0]['status']=='UNFILLED_NOT_TRADABLE'

def test_fee_is_deducted_once_and_cash_budget_limits_whole_shares():
 r=run_ledger([bar(1,10),bar(2,10)],plan(),initial_nav=100,fee_bps=100,slippage_bps=0)
 # 9 shares cost90 plus0.9 fee. Cash9.1, position90, NAV99.1.
 assert r['trades'][0]['quantity']==9
 assert abs(r['ledger'][-1]['cash']-9.1)<1e-10 and abs(r['final_nav']-99.1)<1e-10

def test_volume_participation_caps_quantity():
 r=run_ledger([bar(1,10),bar(2,10,volume=100)],plan(),initial_nav=1000,fee_bps=0,slippage_bps=0,participation=.01)
 assert r['trades'][0]['quantity']==1 and r['trades'][0]['status']=='PARTIAL_OR_CASH_CAP'

def test_same_close_signal_fill_is_rejected():
 p=plan();p[0]['fill_date']=p[0]['signal_date'];raises(lambda:run_ledger([bar(1,10)],p),'precede')

def test_missing_duplicate_and_invalid_prices_fail_data_audit():
 raises(lambda:validate_market([bar(1,10),bar(1,10)]),'Duplicate')
 raises(lambda:validate_market([bar(1,0)]),'positive')
 row=bar(1,10);row['close']=float('nan');raises(lambda:validate_market([row]),'Invalid')

def test_reverse_split_requires_unimplemented_cash_in_lieu_policy():
 raises(lambda:validate_market([bar(1,10,split_factor=.5)]),'cash-in-lieu')

def test_fixture_cannot_be_promoted_to_real_market_research():
 r=research_gate(dict(kind='synthetic_fixture',provider_contract_verified=True,corporate_actions_verified=True,universe_scope_documented=True,calendar_verified=True,benchmark_verified=True,usage_rights_verified=True))
 assert r['status']=='BLOCKED' and not r['investment_performance_claims_allowed']
 assert 'real_market_data' in r['missing']

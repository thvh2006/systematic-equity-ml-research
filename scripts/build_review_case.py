#!/usr/bin/env python3
import csv,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/"src"))
from equity_research.data import load_market
from equity_research.ledger import run_ledger
def main():
 out=R/'artifacts/foundation';r=json.loads((out/'results.json').read_text());fits=json.loads((out/'fit_receipts.json').read_text());first=fits[0];d=first['fill_date']
 with (out/'signals.csv').open() as f: signals=[x for x in csv.DictReader(f) if x['strategy']=='ridge_alpha10' and x['signal_date']==first['signal_date']]
 weights={x['asset']:float(x['target_weight']) for x in signals}
 with (R/'data/sample/synthetic_market.csv').open() as f: bars=[x for x in csv.DictReader(f) if x['date']==d]
 items=[dict(asset=b['asset'],target_weight=weights.get(b['asset'],0),raw_open=float(b['open']),raw_close=float(b['close']),volume=float(b['volume'])) for b in bars]
 ledger=next(x for x in r['results']['ridge_alpha10__cost1']['ledger'] if x['date']==d)
 trades=[x for x in r['results']['ridge_alpha10__cost1']['trades'] if x['fill_date']==d]
 payload=dict(run_id=r['run_id'],status='SYNTHETIC_FIXTURE_ONLY',signal_date=first['signal_date'],fill_date=d,initial_nav=r['config']['initial_nav'],fee_bps=r['config']['fee_bps'],slippage_bps=r['config']['slippage_bps'],participation=r['config']['max_volume_participation'],assets=items,python_ledger=ledger,python_trades=trades)
 short_rows=[b for b in load_market(R/'data/sample/synthetic_market.csv') if b['date']<=d]
 plan=[dict(signal_date=first['signal_date'],fill_date=d,weights=weights)]
 payload['counterfactuals']={}
 for name,nav,fee in [('fee_plus20',100000.,30.),('nav_double',200000.,10.)]:
  case=run_ledger(short_rows,plan,initial_nav=nav,fee_bps=fee,slippage_bps=5.,participation=.01)
  payload['counterfactuals'][name]=dict(ledger=case['ledger'][-1],trades=case['trades'])
 (out/'review_case.json').write_text(json.dumps(payload,indent=2)+'\n');print('Prepared independent first-rebalance review case')
if __name__=='__main__':main()

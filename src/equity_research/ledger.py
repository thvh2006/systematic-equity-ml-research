"""Whole-share, self-financing daily cash/holdings/dividend-receivable ledger."""
import math
from .data import market_panel

def run_ledger(rows,plans,*,initial_nav=100000.,fee_bps=10.,slippage_bps=5.,participation=.01,capacity_lag_sessions=0):
 if initial_nav<=0 or min(fee_bps,slippage_bps)<0 or not 0<participation<=1:raise ValueError('Invalid execution input')
 dates,assets,lookup=market_panel(rows);cash=float(initial_nav);holdings={a:0 for a in assets};pending=[];trades=[];ledger=[]
 byfill={p['fill_date']:p for p in plans}
 if len(byfill)!=len(plans):raise ValueError('Duplicate fill date')
 for p in plans:
  if p['signal_date']>=p['fill_date']:raise ValueError('Signal must precede fill')
  if min(p['weights'].values(),default=0)<0 or sum(p['weights'].values())>1+1e-10:raise ValueError('Invalid target weights')
 if capacity_lag_sessions not in [0,1]:raise ValueError('Only current or prior session capacity supported')
 for session_i,d in enumerate(dates):
  opening_cash=cash;paid=0.;redemption=0.;net_trade_cash=0.;fees=0.;slippage=0.;notional=0.
  for a in assets:
   r=lookup[d,a];holdings[a]*=r['split_factor']
   if r['dividend'] and holdings[a]:pending.append(dict(pay_date=r['dividend_pay_date'],amount=holdings[a]*r['dividend'],asset=a))
   if not r['active'] and holdings[a]:
    v=holdings[a]*r['delist_cash'];cash+=v;redemption+=v;holdings[a]=0
  still=[]
  for receivable in pending:
   if receivable['pay_date']<=d:cash+=receivable['amount'];paid+=receivable['amount']
   else:still.append(receivable)
  pending=still
  if d in byfill:
   plan=byfill[d];pre_nav=cash+sum(holdings[a]*lookup[d,a]['open'] for a in assets)+sum(r['amount'] for r in pending)
   targets={a:math.floor(pre_nav*plan['weights'].get(a,0)/lookup[d,a]['open']) if lookup[d,a]['active'] else 0 for a in assets}
   orders=[(a,targets[a]-holdings[a]) for a in assets]
   # Sell before buying. Unfilled quantities expire; not magically filled in a suspension.
   for a,wanted in sorted(orders,key=lambda item:(item[1]>0,item[0])):
    if abs(wanted)<1e-10:continue
    bar=lookup[d,a];side=1 if wanted>0 else -1
    capacity_volume=lookup[dates[session_i-1],a]['volume'] if capacity_lag_sessions and session_i else (0 if capacity_lag_sessions else bar['volume'])
    capacity=math.floor(capacity_volume*participation)
    if not bar['tradable']:
     trades.append(dict(signal_date=plan['signal_date'],fill_date=d,asset=a,side='BUY' if side>0 else 'SELL',requested_quantity=abs(wanted),quantity=0,raw_open=bar['open'],execution_price=0.,notional=0.,fee=0.,slippage_cost=0.,cash_change=0.,status='UNFILLED_NOT_TRADABLE'));continue
    px=bar['open']*(1+side*slippage_bps/10000);quantity=min(abs(wanted),capacity)
    if side<0:quantity=min(quantity,holdings[a])
    else:quantity=min(quantity,math.floor(max(cash,0)/(px*(1+fee_bps/10000))))
    quantity=math.floor(quantity+1e-10);value=quantity*px;fee=value*fee_bps/10000;cash_change=-side*value-fee
    cash+=cash_change;holdings[a]+=side*quantity;net_trade_cash-=side*value;fees+=fee;slippage+=quantity*bar['open']*slippage_bps/10000;notional+=quantity*bar['open']
    trades.append(dict(signal_date=plan['signal_date'],fill_date=d,asset=a,side='BUY' if side>0 else 'SELL',requested_quantity=abs(wanted),quantity=quantity,raw_open=bar['open'],execution_price=px,notional=value,fee=fee,slippage_cost=quantity*bar['open']*slippage_bps/10000,cash_change=cash_change,status='FILLED' if abs(quantity-abs(wanted))<1e-8 else 'PARTIAL_OR_CASH_CAP'))
  market_value=sum(holdings[a]*lookup[d,a]['close'] for a in assets);receivables=sum(r['amount'] for r in pending);nav=cash+market_value+receivables
  difference=cash-opening_cash-paid-redemption-net_trade_cash+fees
  if abs(difference)>1e-6 or cash < -1e-7:raise ArithmeticError('Cash ledger not self-financing')
  ledger.append(dict(date=d,opening_cash=opening_cash,dividend_cash_received=paid,delisting_cash=redemption,net_executed_notional_cash=net_trade_cash,fees=fees,slippage_cost=slippage,traded_notional=notional,cash=cash,market_value=market_value,dividend_receivable=receivables,nav=nav,cash_reconciliation=difference,holdings=dict(holdings)))
 return dict(ledger=ledger,trades=trades,final_nav=ledger[-1]['nav'],total_fees=sum(r['fees'] for r in ledger),total_slippage=sum(r['slippage_cost'] for r in ledger),max_cash_difference=max(abs(r['cash_reconciliation']) for r in ledger))

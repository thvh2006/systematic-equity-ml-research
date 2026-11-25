"""Explicit raw-price/action contract and a forward-only return index."""
from collections import Counter,defaultdict
from datetime import date
import csv,math

def load_market(path):
 with open(path,newline='') as f: rows=list(csv.DictReader(f))
 for r in rows:
  for k in ['open','close','volume','split_factor','dividend','delist_cash']:r[k]=float(r[k])
  r['tradable']=str(r['tradable']).lower() in ['true','1'];r['active']=str(r['active']).lower() in ['true','1']
 return rows

def validate_market(rows):
 if not rows:raise ValueError('Empty market input')
 keys=[(r['date'],r['asset']) for r in rows]
 if len(set(keys))!=len(keys):raise ValueError('Duplicate date/asset')
 if keys!=sorted(keys):raise ValueError('Market input must be sorted by date and asset')
 for r in rows:
  date.fromisoformat(r['date'])
  for k in ['open','close','volume','split_factor','dividend','delist_cash']:
   if isinstance(r[k],bool) or not isinstance(r[k],(int,float)) or not math.isfinite(r[k]) or r[k]<0:raise ValueError('Invalid market field '+k)
  if r['split_factor']<1 or r['split_factor']!=int(r['split_factor']):raise ValueError('Reverse or fractional splits require an explicit cash-in-lieu policy')
  if r['active'] and min(r['open'],r['close'])<=0:raise ValueError('Active asset price must be positive')
  if r['tradable'] and (not r['active'] or r['volume']<=0):raise ValueError('Tradability/volume inconsistency')
  if r['dividend'] and (not r['dividend_pay_date'] or r['dividend_pay_date']<r['date']):raise ValueError('Invalid dividend payment date')
  if r['delist_cash'] and r['active']:raise ValueError('Delisting cash on active asset')
 dates=sorted({r['date'] for r in rows});assets=sorted({r['asset'] for r in rows})
 if len(rows)!=len(dates)*len(assets):raise ValueError('Missing panel rows; stale or missing marks require explicit records')
 return dict(rows=len(rows),sessions=len(dates),assets=len(assets),split_events=sum(r['split_factor']!=1 for r in rows),dividend_events=sum(r['dividend']>0 for r in rows),suspended_rows=sum(r['active'] and not r['tradable'] for r in rows),delist_events=sum(r['delist_cash']>0 for r in rows))

def market_panel(rows):
 validate_market(rows);dates=sorted({r['date'] for r in rows});assets=sorted({r['asset'] for r in rows});lookup={(r['date'],r['asset']):r for r in rows}
 return dates,assets,lookup

def forward_index(rows):
 dates,assets,lookup=market_panel(rows);out={}
 for a in assets:
  wealth=1.;prior=None
  for d in dates:
   r=lookup[d,a]
   if prior is not None and prior['active']:
    settlement=r['delist_cash'] if not r['active'] else (r['close']+r['dividend'])*r['split_factor']
    wealth*=settlement/prior['close']
   out[d,a]=wealth;prior=r
 return out

def research_gate(manifest):
 required=['provider_contract_verified','corporate_actions_verified','universe_scope_documented','calendar_verified','benchmark_verified','usage_rights_verified']
 missing=[k for k in required if manifest.get(k) is not True]
 if manifest.get('kind')!='market_data':missing.insert(0,'real_market_data')
 return dict(status='BLOCKED' if missing else 'READY_FOR_RESEARCH',missing=missing,investment_performance_claims_allowed=not missing)

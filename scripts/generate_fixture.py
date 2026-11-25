#!/usr/bin/env python3
"""Deterministic fictional data for accounting and temporal checks, never market evidence."""
import csv,hashlib,json
from datetime import date,timedelta
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1]
def main():
 rng=np.random.default_rng(20261124);dates=[];d=date(2022,1,3)
 while len(dates)<500:
  if d.weekday()<5:dates.append(d.isoformat())
  d+=timedelta(days=1)
 assets=['ALFA','BETA','DELTA','EPSI','ETA','GAMMA','THETA','ZETA'];prices={a:40+10*i for i,a in enumerate(assets)};alive={a:True for a in assets};rows=[];market=rng.normal(.0002,.008,len(dates))
 for i,d in enumerate(dates):
  for j,a in enumerate(assets):
   split=2. if a=='ALFA' and i==120 else 1.;div=1. if a=='BETA' and i==170 else 0.;delist=prices[a]*.6 if a=='THETA' and i==300 else 0.
   if delist:alive[a]=False
   tradable=alive[a] and not(a=='EPSI' and 220<=i<=224)
   if not alive[a]:op=cl=volume=0.
   elif not tradable:op=cl=prices[a];volume=0.
   else:
    op=max(.5,prices[a]/split*(1+rng.normal(0,.001))-div)
    cl=max(.5,op*(1+market[i]*(.65+j*.08)+rng.normal(0,.009)+.0003*np.sin(i/45+j)))
    volume=int(rng.integers(80000,300000));prices[a]=cl
   rows.append(dict(date=d,asset=a,open=op,close=cl,volume=volume,tradable=tradable,active=alive[a],split_factor=split,dividend=div,dividend_pay_date=dates[190] if div else '',delist_cash=delist))
 path=R/'data/sample/synthetic_market.csv'
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=rows[0],lineterminator='\n');w.writeheader();w.writerows(rows)
 manifest=dict(kind='synthetic_fixture',seed=20261124,fictional_assets=assets,rows=len(rows),sessions=len(dates),calendar='Synthetic weekdays, no exchange-holiday claim',source='Locally generated deterministic fixture',sha256=hashlib.sha256(path.read_bytes()).hexdigest(),provider_contract_verified=False,corporate_actions_verified=False,universe_scope_documented=True,calendar_verified=False,benchmark_verified=False,usage_rights_verified=True,rights_note='Project-generated fictional fixture. No provider market data is redistributed.',purpose='Pipeline/accounting/leakage demonstrations only. No alpha or investment-performance evidence.')
 (R/'data/manifests/fixture.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Generated4000 fictional asset/session rows; not market data')
if __name__=='__main__':main()

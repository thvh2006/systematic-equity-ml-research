#!/usr/bin/env python3
"""Append-only operational status. Refuses to invent a stale-data trading signal."""
import argparse,json,hashlib,datetime as dt,sys
from pathlib import Path
from zoneinfo import ZoneInfo
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'src'))
from equity_research.calendar import sessions
def check(asof,now=None):
 now=now or dt.datetime.now(dt.timezone.utc);ny=now.astimezone(ZoneInfo('America/New_York'));last=ny.date() if (ny.hour,ny.minute)>=(16,15) else ny.date()-dt.timedelta(days=1)
 cal=sessions((last-dt.timedelta(days=10)).isoformat(),last.isoformat());expected=cal[-1];stale=asof<expected
 return {'at':now.isoformat(),'expected_latest_session':expected,'data_as_of':asof,'status':'BLOCKED_STALE_DATA' if stale else 'DATA_CURRENT_REVIEW_REQUIRED','order_submission':False,'forecast_emitted':False,'realised_forward_sessions':0}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check-only',action='store_true');a=p.parse_args();m=json.loads((R/'data/manifests/market_receipt.json').read_text());event=check(m['end']);path=R/'artifacts/paper/events.jsonl'
 if not a.check_only:
  path.parent.mkdir(parents=True,exist_ok=True);prev=path.read_text().splitlines() if path.exists() else [];event['previous_hash']=hashlib.sha256(prev[-1].encode()).hexdigest() if prev else None
  with path.open('a') as f:f.write(json.dumps(event,sort_keys=True)+'\n')
 print(json.dumps(event,indent=2))
 if a.check_only and event['status']=='BLOCKED_STALE_DATA':raise SystemExit(2)
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Normalize a visible Yahoo history export and issuer distributions; raw stays private."""
import csv,hashlib,json,sys,collections,datetime as dt,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'src'))
from equity_research.calendar import sessions
from equity_research.data import validate_market
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 import openpyxl
 raw=R/'data/private/yahoo_pages/P2_ETF_history_20261124.csv';issuer=R/'data/private/issuer_distributions.xlsx'
 prices=collections.defaultdict(dict);events=collections.defaultdict(dict);universe=['XLB','XLE','XLF','XLI','XLK','XLP','XLU','XLV','XLY','SPY']
 for r in csv.reader(raw.open()):
  if r[1]=='Date':continue
  d=dt.datetime.strptime(r[1],'%b %d, %Y').date().isoformat();a=r[0]
  if not '2017-01-01'<=d<='2025-12-31':continue
  if len(r)==8:
   if d in prices[a]:raise ValueError('Duplicate source price')
   prices[a][d]=[float(x.replace(',','')) for x in r[2:]]
  elif len(r)==3:events[a].setdefault(d,[]).append(r[2].strip())
  else:raise ValueError('Unknown history row shape')
 dividends=collections.defaultdict(dict)
 for r in list(openpyxl.load_workbook(issuer,read_only=True,data_only=True).active.values)[1:]:
  if r[1] not in universe:continue
  ex=dt.datetime.strptime(r[3],'%m/%d/%Y').date().isoformat();pay=dt.datetime.strptime(r[5],'%m/%d/%Y').date().isoformat()
  amount=sum(float(str(x).strip() or 0) for x in r[6:9]);old=dividends[r[1]].get(ex)
  if old and old['pay']!=pay:raise ValueError('Conflicting pay dates')
  dividends[r[1]][ex]={'pay':pay,'amount':amount+(old['amount'] if old else 0)}
 start,end='2017-01-01','2025-12-31';dates=sessions(start,end);out=[];checks=[];price_checks=[];mismatches=[]
 split_assets={'XLB','XLE','XLK','XLU','XLY'};split_date='2025-12-05'
 for a in universe:
  observed_dates={d for d in prices[a] if start<=d<=end}
  if observed_dates!=set(dates):raise ValueError(f'Calendar mismatch {a}: missing {set(dates)-observed_dates}, extra {observed_dates-set(dates)}')
  for d in dates:
   op,hi,lo,cl,adj,vol=prices[a][d];factor=2 if a in split_assets and d<split_date else 1
   if not lo<=min(op,cl)<=max(op,cl)<=hi:raise ValueError('OHLC ordering')
   dist=dividends[a].get(d,{'amount':0.,'pay':''});action=events[a].get(d,[])
   yd=sum(float(x.split()[0])*factor for x in action if 'Dividend' in x or 'Capital Gain' in x)
   if dist['amount'] or yd:
    delta=abs(yd-dist['amount']);checks.append(dict(asset=a,date=d,yahoo_reconstructed=yd,issuer=dist['amount'],difference=delta,pay_date=dist['pay']))
    if delta>.003: mismatches.append(checks[-1])
   for action_text in action:
    if 'Splits' in action_text and not (a in split_assets and d==split_date and action_text.startswith('2:1')):raise ValueError('Unreviewed action '+action_text)
   out.append(dict(date=d,asset=a,open=op*factor,close=cl*factor,volume=math.floor(vol/factor),tradable=True,active=True,split_factor=2. if a in split_assets and d==split_date else 1.,dividend=dist['amount'],dividend_pay_date=dist['pay'],delist_cash=0.))
 # Official issuer announcement reports contemporaneous 18-Nov-2025 prices.
 for a,want in {'XLK':279.03,'XLY':224.50,'XLE':91.06,'XLU':89.22,'XLB':85.52}.items():
  got=prices[a]['2025-11-18'][3]*2;price_checks.append(dict(asset=a,date='2025-11-18',reconstructed_close=got,issuer_price=want,difference=abs(got-want)))
  if abs(got-want)>.021:raise ValueError('Split price reconstruction failed')
 out.sort(key=lambda r:(r['date'],r['asset']));audit=validate_market(out);p=R/'data/private/market_2017_2025.csv'
 with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=out[0]);w.writeheader();w.writerows(out)
 receipt=dict(status='REAL_DATA_EXPLORATORY_ONLY',start=dates[0],end=dates[-1],audit=audit,source_history_sha256=digest(raw),issuer_file_sha256=digest(issuer),normalized_sha256=digest(p),corporate_action_comparisons=len(checks),corporate_action_mismatches=mismatches,split_price_checks=price_checks,calendar='Independent NYSE-rule calendar including 2018/2025 mourning closures; shared SPY sessions reconciled',precision='Displayed prices rounded to 0.01; reconstructed pre-split ticks can have 0.02 increments',volume_policy='Reported Yahoo volume divided by future split factor, a conservative capacity assumption; volume basis not independently verified',publication='Raw provider records private and excluded from GitHub; redistribution permission not established',usagerights='Personal research source review; no third-party data license conveyed',limitations=['No historical provider-vintage archive; retrospective corrected dataset','Fixed selected funds, not survivorship-free all-ETF or constant-sector universe','No independent opening-auction volume or spread history','No institutional data sign-off'],checks=checks)
 (R/'artifacts/market').mkdir(parents=True,exist_ok=True);(R/'artifacts/market/intake_audit_private.json').write_text(json.dumps(receipt,indent=2)+'\n')
 public={k:v for k,v in receipt.items() if k not in ['checks','split_price_checks','corporate_action_mismatches']};public['corporate_action_mismatch_count']=len(mismatches);public['split_price_check_count']=len(price_checks)
 (R/'data/manifests/market_receipt.json').write_text(json.dumps(public,indent=2)+'\n');print(json.dumps(public,indent=2))
 # Reviewed discrepancy: use issuer's primary cash-distribution record, not Yahoo's rounded/revised figure.
 approved={('SPY','2021-12-17'):'Issuer record takes precedence; Yahoo shows 1.633 versus issuer 1.636431. All cash entitlements use issuer amounts.'}
 receipt['action_resolutions']=[{**x,'resolution':approved.get((x['asset'],x['date']))} for x in mismatches]
 unresolved=[x for x in mismatches if (x['asset'],x['date']) not in approved]
 public['resolved_action_discrepancies']=len(mismatches)-len(unresolved);public['unresolved_action_discrepancies']=len(unresolved)
 (R/'artifacts/market/intake_audit_private.json').write_text(json.dumps(receipt,indent=2)+'\n');(R/'data/manifests/market_receipt.json').write_text(json.dumps(public,indent=2)+'\n')
 if unresolved:raise SystemExit('Action differences require review before modelling')
if __name__=='__main__':main()

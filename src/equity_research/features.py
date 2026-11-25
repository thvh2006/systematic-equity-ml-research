"""Features use information through signal close; targets begin next-session open."""
import math
from .data import market_panel,forward_index
FEATURES=['momentum_21','momentum_63','volatility_20','drawdown_63','log_dollar_volume_20']

def build_panel(rows,horizon=21,signal_timezone='UTC'):
 dates,assets,lookup=market_panel(rows);idx=forward_index(rows);features=[];labels=[]
 for i in range(63,len(dates)):
  d=dates[i]
  for a in assets:
   r=lookup[d,a]
   if not r['active']:continue
   vals=[idx[dates[j],a] for j in range(i-63,i+1)]
   returns=[vals[j]/vals[j-1]-1 for j in range(len(vals)-20,len(vals))]
   mu=sum(returns)/len(returns);vol=math.sqrt(sum((v-mu)**2 for v in returns)/(len(returns)-1))
   dv=sum(lookup[dates[j],a]['close']*lookup[dates[j],a]['volume'] for j in range(i-19,i+1))/20
   from .calendar import available_timestamp
   timestamp=available_timestamp(d) if signal_timezone=='America/New_York' else d+'T16:00:00+00:00'
   features.append(dict(date=d,asset=a,session_index=i,feature_available_at=timestamp,momentum_21=idx[d,a]/idx[dates[i-21],a]-1,momentum_63=vals[-1]/vals[0]-1,volatility_20=vol,drawdown_63=vals[-1]/max(vals)-1,log_dollar_volume_20=math.log1p(dv)))
   end=i+1+horizon
   label=dict(date=d,asset=a,label_start=dates[i+1] if i+1<len(dates) else None,label_end=dates[end] if end<len(dates) else None,label_end_index=end,target=None,status='UNMATURED')
   if end<len(dates):
    entry=lookup[dates[i+1],a]
    if not entry['tradable']:label['status']='NO_EXECUTABLE_ENTRY'
    else:
     # One post-action share bought at the entry open. Entry-day ex-dividend is not owned.
     q=1.;distribution=0.;settlement=0.;active=True
     for j in range(i+2,end+1):
      bar=lookup[dates[j],a]
      if not active:continue
      q*=bar['split_factor'];distribution+=q*bar['dividend']
      if not bar['active']:
       settlement+=q*bar['delist_cash'];q=0;active=False
     final=lookup[dates[end],a]
     label['target']=(q*final['open']+distribution+settlement)/entry['open']-1;label['status']='MATURED'
   labels.append(label)
 return features,labels

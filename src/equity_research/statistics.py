"""Explicit daily/monthly return conventions and paired time-block uncertainty."""
import math
import numpy as np
def returns(ledger,initial_nav):
 prior=initial_nav;out=[]
 for r in ledger:out.append({'date':r['date'],'return':r['nav']/prior-1});prior=r['nav']
 return out
def monthly(daily):
 out={}
 for r in daily:k=r['date'][:7];out[k]=(1+out.get(k,0))*(1+r['return'])-1
 return out
def metrics(result,initial_nav=100000.):
 led=result['ledger'];rr=np.array([r['return'] for r in returns(led,initial_nav)]);n=len(rr);nav=np.array([initial_nav]+[r['nav'] for r in led]);peak=np.maximum.accumulate(nav);dd=nav/peak-1;sd=float(np.std(rr,ddof=1)) if n>1 else 0.;years=n/252
 return {'sessions':n,'total_return':float(nav[-1]/initial_nav-1),'cagr':float((nav[-1]/initial_nav)**(1/years)-1),'annual_volatility':sd*math.sqrt(252),'sharpe_zero_cash':float(np.mean(rr)/sd*math.sqrt(252)) if sd else 0.,'max_drawdown':float(dd.min()),'fees':result['total_fees'],'slippage':result['total_slippage'],'annual_oneway_turnover':sum(r['traded_notional']/r['nav']/2 for r in led)/years,'final_nav':float(nav[-1]),'max_cash_difference':result['max_cash_difference']}
def block_bootstrap_difference(a,b,*,block=3,reps=2000,seed=20261124):
 keys=sorted(set(a)&set(b));x=np.array([a[k]-b[k] for k in keys]);n=len(x)
 if not n:raise ValueError('Empty paired sample')
 rng=np.random.default_rng(seed);samples=[]
 for _ in range(reps):
  starts=rng.integers(0,n,size=math.ceil(n/block));indices=np.concatenate([(s+np.arange(block))%n for s in starts])[:n];samples.append(float(np.mean(x[indices])))
 lo,hi=np.quantile(samples,[.025,.975]);return {'paired_months':n,'mean_monthly_net_difference':float(x.mean()),'ci95_low':float(lo),'ci95_high':float(hi),'block_months':block,'repetitions':reps,'seed':seed,'interpretation':'Circular time-block bootstrap interval for arithmetic mean paired monthly return difference; descriptive small-sample uncertainty, not proof of alpha.'}
def rank_ic(scores,targets):
 if len(scores)<3:return None
 def rank(x):
  a=np.asarray(x);return np.array([sum(a<v)+(sum(a==v)-1)/2 for v in a],dtype=float)
 a=rank(scores);b=rank(targets)
 if min(a.std(),b.std())<1e-12:return None
 return float(np.corrcoef(a,b)[0,1])

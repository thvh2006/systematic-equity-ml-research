"""Small bounded challengers implemented in NumPy; not XGBoost or LightGBM."""
import numpy as np
from collections import Counter
from .features import FEATURES
from .models import fit_ridge,predict as ridge_predict
def arrays(train):
 X=np.array([[r[k] for k in FEATURES] for r in train]);y=np.array([r['target'] for r in train]);counts=Counter(r['date'] for r in train);w=np.array([1/counts[r['date']] for r in train]);w/=w.sum()
 mean=(w[:,None]*X).sum(0);scale=np.sqrt((w[:,None]*(X-mean)**2).sum(0));scale[scale<1e-12]=1
 return (X-mean)/scale,y,w,mean,scale
def fit(train,spec):
 if spec['family']=='ridge':return {'family':'ridge','model':fit_ridge(train,alpha=spec['alpha'])}
 X,y,w,mean,scale=arrays(train);intercept=float(w@y);yc=y-intercept
 common={'family':spec['family'],'mean':mean.tolist(),'scale':scale.tolist(),'intercept':intercept,'max_label_end':max(r['label_end'] for r in train),'fit_rows':len(train)}
 if spec['family']=='elastic_net':
  coef=np.zeros(X.shape[1]);alpha=spec['alpha'];ratio=spec['l1_ratio'];converged=False
  for iteration in range(2000):
   old=coef.copy()
   for j in range(X.shape[1]):
    residual=yc-X@coef+X[:,j]*coef[j];rho=float((w*X[:,j])@residual);coef[j]=np.sign(rho)*max(abs(rho)-alpha*ratio,0)/(float((w*X[:,j])@X[:,j])+alpha*(1-ratio))
   if np.max(np.abs(coef-old))<1e-9:converged=True;break
  if not converged:raise ArithmeticError('Elastic net convergence failed')
  return {**common,'coef':coef.tolist(),'iterations':iteration+1,'alpha':alpha,'l1_ratio':ratio}
 if spec['family']!='boosted_stumps':raise ValueError('Unknown learner')
 estimate=np.zeros(len(y));stumps=[]
 # Fixed quantile cuts are learned within train only. All candidates are deterministic.
 cuts=[np.unique(np.quantile(X[:,j],[.2,.4,.5,.6,.8])) for j in range(X.shape[1])]
 for _ in range(spec['n_estimators']):
  residual=yc-estimate;best=None
  for j in range(X.shape[1]):
   for threshold in cuts[j]:
    left=X[:,j]<=threshold;wl=w[left].sum();wr=w[~left].sum()
    if min(wl,wr)<1e-10:continue
    lv=float(w[left]@residual[left]/wl);rv=float(w[~left]@residual[~left]/wr);prediction=np.where(left,lv,rv);loss=float(w@((residual-prediction)**2))
    if best is None or loss<best[0]:best=(loss,j,float(threshold),lv,rv,prediction)
  if best is None:break
  _,j,threshold,lv,rv,prediction=best;rate=spec['learning_rate'];estimate+=rate*prediction;stumps.append({'feature':j,'threshold':threshold,'left':lv*rate,'right':rv*rate})
 return {**common,'stumps':stumps}
def predict(model,row):
 if model['family']=='ridge':return ridge_predict(model['model'],row)
 x=(np.array([row[k] for k in FEATURES])-model['mean'])/model['scale'];value=model['intercept']
 if model['family']=='elastic_net':return float(value+x@model['coef'])
 return float(value+sum(s['left'] if x[s['feature']]<=s['threshold'] else s['right'] for s in model['stumps']))

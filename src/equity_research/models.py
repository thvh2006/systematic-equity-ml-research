"""Small fixed-spec ridge baseline with train-only scaling; no model promotion."""
from collections import Counter
import numpy as np
from .features import FEATURES

def fit_ridge(train,alpha=10.):
 if not np.isfinite(alpha) or alpha<=0:raise ValueError('Ridge alpha must be positive')
 if not train:raise ValueError('No matured training data')
 X=np.array([[r[k] for k in FEATURES] for r in train],dtype=float);y=np.array([r['target'] for r in train],dtype=float)
 if not np.isfinite(X).all() or not np.isfinite(y).all():raise ValueError('Nonfinite model input')
 counts=Counter(r['date'] for r in train);weights=np.array([1/counts[r['date']] for r in train]);weights/=weights.mean()
 mean=np.average(X,axis=0,weights=weights);scale=np.sqrt(np.average((X-mean)**2,axis=0,weights=weights));scale=np.where(scale>1e-12,scale,1.)
 z=(X-mean)/scale;intercept=float(np.average(y,weights=weights));coef=np.linalg.solve(z.T@(z*weights[:,None])+alpha*np.eye(len(FEATURES)),z.T@((y-intercept)*weights))
 return dict(alpha=alpha,mean=mean.tolist(),scale=scale.tolist(),coef=coef.tolist(),intercept=intercept,fit_rows=len(train),fit_dates=len(counts),max_label_end=max(r['label_end'] for r in train),train_start=min(r['date'] for r in train),train_end=max(r['date'] for r in train))

def predict(model,row):
 return model['intercept']+sum((row[k]-m)/s*c for k,m,s,c in zip(FEATURES,model['mean'],model['scale'],model['coef']))

def matured_train(features,labels,signal_index,gap_sessions=1):
 lab={(r['date'],r['asset']):r for r in labels}
 return [{**f,**lab[f['date'],f['asset']]} for f in features if lab[f['date'],f['asset']]['status']=='MATURED' and lab[f['date'],f['asset']]['label_end_index']<signal_index-gap_sessions]

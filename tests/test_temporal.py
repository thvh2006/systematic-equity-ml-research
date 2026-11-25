from copy import deepcopy
from pathlib import Path
from equity_research.data import load_market,market_panel
from equity_research.features import build_panel
from equity_research.models import matured_train,fit_ridge,predict
R=Path(__file__).resolve().parents[1]
def sample():return load_market(R/'data/sample/synthetic_market.csv')
def test_all_training_labels_mature_before_signal_with_embargo():
 rows=sample();dates,_,_=market_panel(rows);f,l=build_panel(rows)
 for cutoff in [210,300,450]:
  train=matured_train(f,l,cutoff,1)
  assert train and all(r['label_end_index']<cutoff-1 for r in train)
  assert max(r['label_end'] for r in train)<dates[cutoff]

def test_future_price_changes_cannot_change_earlier_features_or_ridge_predictions():
 rows=sample();dates,_,_=market_panel(rows);cutoff=230;f,l=build_panel(rows);train=matured_train(f,l,cutoff,1);m=fit_ridge(train)
 changed=deepcopy(rows)
 for r in changed:
  if r['date']>dates[cutoff] and r['active']:r['open']*=1.7;r['close']*=1.7
 f2,l2=build_panel(changed);m2=fit_ridge(matured_train(f2,l2,cutoff,1))
 assert m==m2
 past=[r for r in f if r['date']==dates[cutoff]];past2=[r for r in f2 if r['date']==dates[cutoff]]
 assert past==past2
 assert [predict(m,r) for r in past]==[predict(m2,r) for r in past2]

def test_last_horizon_labels_are_unmatured_and_not_used():
 rows=sample();dates,_,_=market_panel(rows);f,l=build_panel(rows)
 assert any(r['status']=='UNMATURED' for r in l)
 assert all(r['target'] is None for r in l if r['status']!='MATURED')
 assert all(r['label_end_index']<len(dates)-2 for r in matured_train(f,l,len(dates)-1,1))

def test_scaling_is_fitted_only_on_matured_train_rows():
 f,l=build_panel(sample());train=matured_train(f,l,230,1);m=fit_ridge(train)
 assert m['fit_rows']==len(train) and m['train_end']<max(r['date'] for r in f)
 assert m['max_label_end']<max(r['date'] for r in f)

def test_ridge_closed_form_has_independent_one_feature_golden_value():
 from equity_research.features import FEATURES
 train=[]
 for i,x in enumerate([-1.,-1.,1.,1.]):
  row={k:0. for k in FEATURES};row.update(date=f'2022-01-0{i+1}',label_end=f'2022-01-0{i+2}',target=2*x,momentum_21=x);train.append(row)
 model=fit_ridge(train,alpha=4.)
 # Standardised x already has mean0, variance1. Sxy8/(Sxx4+penalty4)=1.
 assert abs(model['coef'][0]-1)<1e-10 and abs(model['intercept'])<1e-10
 assert abs(predict(model,train[-1])-1)<1e-10

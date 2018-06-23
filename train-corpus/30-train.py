
import pandas as pd
import pickle
import numpy as np
from sklearn import metrics

df                = pd.read_csv('eiga_score_texts.csv')
ready_df, tfvocab = pickle.load(open('vars/tfidf.saprse', 'rb'))
X = ready_df # Sparse Matrix

def tofloat(x):
  try:
    return float(x)
  except:
    return 0.0
y = df['points'].apply(tofloat)

lgbm_params =  {
  'task'          : 'train',
  'boosting_type' : 'gbdt',
  'objective'     : 'regression',
  'metric'        : 'rmse',
  'num_leaves'    : 270,
  'feature_fraction': 0.5,
  'bagging_fraction': 0.75,
  'bagging_freq'  : 2,
  'learning_rate' : 0.016,
  'verbose'       : 0
}  
from sklearn.model_selection import train_test_split
import lightgbm as lgb
'''
# round 450でRSME 0.8程度
X_train, X_valid, y_train, y_valid = train_test_split( X, y, test_size=0.10, random_state=23)
# LGBM Dataset Formatting 
lgtrain = lgb.Dataset(X_train, y_train,
                feature_name=tfvocab )
lgvalid = lgb.Dataset(X_valid, y_valid,
                feature_name=tfvocab)
lgb_clf = lgb.train(
    lgbm_params,
    lgtrain,
    num_boost_round    =  2000,
    valid_sets         =  [lgtrain, lgvalid],
    valid_names        =  ['train','valid'],
    early_stopping_rounds = 5,
    verbose_eval       = 10 )
print("Model Evaluation Stage")
print('RMSE:', np.sqrt(metrics.mean_squared_error(y_valid, lgb_clf.predict(X_valid))))
'''
# ^- 全量をやってmodelをsave
# ^- round 450でRSME 0.8程度
lgtrain = lgb.Dataset( X, y, feature_name=tfvocab )
lgb_clf = lgb.train(
    lgbm_params,
    lgtrain    ,
    num_boost_round = 450,
    valid_sets      = [ lgtrain ],
   valid_names     = [ 'train' ],
    verbose_eval    = 10 )
print("Model Evaluation Stage")
pickle.dump( lgb_clf, open('vars/lgb_clf.pkl', 'wb') )

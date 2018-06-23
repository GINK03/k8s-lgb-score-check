# Gradient Boosting
import lightgbm as lgb
from sklearn.linear_model import Ridge
from sklearn.cross_validation import KFold

# Tf-Idf
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.pipeline import FeatureUnion
from scipy.sparse import hstack, csr_matrix
from nltk.corpus import stopwords 
import numpy as np
tfidf_para = {
    "analyzer": 'word',
    "token_pattern": r'\w{1,}',
    "sublinear_tf": True,
    "dtype": np.float32,
    "norm": 'l2',
    "smooth_idf":False
}
import pandas as pd

df = pd.read_csv('eiga_score_texts.csv')

def get_col(col_name): return lambda x: x[col_name]
##I added to the max_features of the description. It did not change my score much but it may be worth investigating
vectorizer = FeatureUnion([
        ('texts',TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=10000,
            **tfidf_para,
            preprocessor=get_col('texts'))),
    ])

vectorizer.fit(df.to_dict('records'))

ready_df = vectorizer.transform(df.to_dict('records'))
tfvocab  = vectorizer.get_feature_names()

print('finish tfidf')
import pickle
import dill
pickle.dump( (ready_df, tfvocab), open('vars/tfidf.saprse', 'wb'))
dill.dump( vectorizer, open('vars/vectorizer.dill', 'wb'))

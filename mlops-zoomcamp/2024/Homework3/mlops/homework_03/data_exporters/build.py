import pandas as pd
from sklearn.feature_extraction import DictVectorizer
if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export(df, **kwargs):
    features = ['PULocationID', 'DOLocationID']
    target = kwargs.get('target')
    train_dict = df[features].to_dict(orient='records')
    dv = DictVectorizer()
    X = dv.fit_transform(train_dict)
    y = df[target].values
    
    return X, y, dv
    



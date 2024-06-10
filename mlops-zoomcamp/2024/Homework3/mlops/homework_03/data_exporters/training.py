import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression
import mlflow
if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

mlflow.set_tracking_uri("http://mlflow:5000")
mlflow.set_experiment("mlops-zoomcamp-homework3-Q6")

@data_exporter
def export_data(df, *args, **kwargs):

    mlflow.sklearn.autolog(log_datasets=False)
    with mlflow.start_run():
        features = ['PULocationID', 'DOLocationID']
        target = kwargs.get('target')
        train_dict = df[features].to_dict(orient='records')
        dv = DictVectorizer()
        X = dv.fit_transform(train_dict)
        y = df[target].values
        model = LinearRegression()
        model.fit(X, y)
        print(model.intercept_)

    return dv, model
    



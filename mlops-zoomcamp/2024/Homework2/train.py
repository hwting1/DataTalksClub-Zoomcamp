import os
import pickle
import click

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import root_mean_squared_error
import mlflow

def load_pickle(filename: str):
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("mlops-zoomcamp-homework2-Q3")

@click.command()
@click.option(
    "--data_path",
    default="./output",
    help="Location where the processed NYC taxi trip data was saved"
)
def run_train(data_path: str):

    mlflow.sklearn.autolog(log_datasets=False)
    with mlflow.start_run():

        X_train, y_train = load_pickle(os.path.join(data_path, "train.pkl"))
        X_val, y_val = load_pickle(os.path.join(data_path, "val.pkl"))

        # mlflow.log_param("train-data-path", os.path.join(data_path, "train.pkl"))
        # mlflow.log_param("valid-data-path", os.path.join(data_path, "val.pkl"))

        params = {"max_depth": 10, "random_state": 0}
        # mlflow.log_params(params)
        rf = RandomForestRegressor(**params)
        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_val)
        mlflow.log_metric("rmse", root_mean_squared_error(y_val, y_pred))

        # mlflow.sklearn.log_model(rf, artifact_path="models")

if __name__ == '__main__':
    run_train()

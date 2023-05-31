import os
import pickle
import click
import mlflow

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

from hyperopt import fmin, tpe, hp, STATUS_OK, Trials


mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("random-forest-autlog-experiment")


def load_pickle(filename: str):
    """Load the pickle file from filepath."""
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)


@click.command()
@click.option(
    "--data_path",
    default="./output",
    help="Location where the processed NYC taxi trip data was saved"
)
def run_train(data_path: str):
    """Run the training dataset with mlflow client."""
    train_data_path = os.path.join(data_path, "train.pkl")
    validation_path = os.path.join(data_path, "val.pkl")

    X_train, y_train = load_pickle(train_data_path)
    X_val, y_val = load_pickle(validation_path)

    with mlflow.start_run():
        mlflow.log_param("train_data_path", train_data_path)
        mlflow.log_param("validation_data_path", validation_path)

        mlflow.set_tag("model", "RandomForestAggressor")

        mlflow.sklearn.autolog()

        rf = RandomForestRegressor(max_depth=10, random_state=0)
        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_val)

        rmse = mean_squared_error(y_val, y_pred, squared=False)

        mlflow.log_metric("rmse", rmse)

    return {'loss': rmse, 'status': STATUS_OK}


if __name__ == '__main__':
    run_train()

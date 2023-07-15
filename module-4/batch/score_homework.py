#!/usr/bin/env python
# coding: utf-8
import sys
import os
import pickle
import uuid
import pandas as pd

import mlflow

from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

from sklearn.pipeline import make_pipeline


def generate_uuids(n):
    ride_ids = []
    for idx in range(n):
        ride_ids.append(str(uuid.uuid4()))
    return ride_ids


def read_dataframe(filename: str):
    df = pd.read_parquet(filename)

    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df.duration = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)]

    df['ride_id'] = generate_uuids(len(df))

    return df


def prepare_dictionaries(df: pd.DataFrame):

    categorical = ['PULocationID', 'DOLocationID']
    df[categorical] = df[categorical].astype(str)

    df['PU_DO'] = df['PULocationID'] + '_' + df['DOLocationID']
    categorical = ['PU_DO']
    numerical = ['trip_distance']
    dicts = df[categorical + numerical].to_dict(orient='records')

    return dicts


def load_model(run_id):
    logged_model = f's3://mlflow-artifacts-remote-amogh/10/{run_id}/artifacts/module-4/'
    model = mlflow.pyfunc.load_model(logged_model)
    return model


def apply_model(input_file, run_id, output_file):

    df = read_dataframe(input_file)
    print(f'Input file read = {input_file}')
    dicts = prepare_dictionaries(df)

    model = load_model(run_id)
    print(f'Model Loaded = {model}')
    y_pred = model.predict(dicts)

    df_result = pd.DataFrame()

    df_result['ride_id'] = df['ride_id']
    df_result['tpep_pickup_datetime'] = df['tpep_pickup_datetime']
    df_result['PULocationID'] = df['PULocationID']
    df_result['DOLocationID'] = df['DOLocationID']
    df_result['actual_duration'] = df['duration']
    df_result['predicted_duration'] = y_pred
    df_result['diff'] = df_result['actual_duration'] - df_result['predicted_duration']
    df_result['model_version'] = run_id

    df_result.to_parquet(
        output_file,
        engine='pyarrow',
        compression=None,
        index=False
    )
    print(f"predicted_duration_mean = {df_result['predicted_duration'].mean()}")


def ride_duration_prediction():
    year = int(sys.argv[1])  # 2022
    month = int(sys.argv[2])  # 2
    taxi_type = sys.argv[3]  # 'yellow'

    input_file = f'https://d37ci6vzurychx.cloudfront.net/trip-data/{taxi_type}_tripdata_{year:04d}-{month:02d}.parquet'
    output_file = f'output/{taxi_type}/{year:04d}-{month:02d}.parquet'

    RUN_ID = os.getenv('RUN_ID','00b0567f62f248a689ccede5fb2bc156')

    apply_model(input_file=input_file, run_id=RUN_ID, output_file=output_file)


if __name__ == '__main__':
    ride_duration_prediction()

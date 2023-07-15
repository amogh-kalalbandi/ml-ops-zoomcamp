#!/usr/bin/env python
# coding: utf-8
import sys
import os
import pickle
import uuid
import pandas as pd
import numpy as np

# import mlflow

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


def load_model(use_local_model: bool, run_id):
    if use_local_model:
        with open('/app/model.bin', 'rb') as f_in:
            dv, model = pickle.load(f_in)
        return dv, model
    else:
        logged_model = f's3://mlflow-artifacts-remote-amogh/10/{run_id}/artifacts/module-4/'
        model = mlflow.pyfunc.load_model(logged_model)
        return None, model


def apply_model(input_file, run_id, output_file, use_local_model, taxi_type):

    df = read_dataframe(input_file)
    df_chunk_1 = df.iloc[:, :500000].copy()
    df_chunk_2 = df.iloc[:, 500000:].copy()
    print(f'Input file read = {input_file}')

    dv, model = load_model(use_local_model, run_id)
    print(f'Model Loaded = {model}')

    dicts_1 = prepare_dictionaries(df_chunk_1)
    dicts_2 = prepare_dictionaries(df_chunk_2)
    dicts_1 = dv.transform(dicts_1)
    dicts_2 = dv.transform(dicts_2)

    y_pred_1 = model.predict(dicts_1)
    y_pred_2 = model.predict(dicts_2)

    y_pred = np.concatenate((y_pred_1, y_pred_2), axis=0)
    df_result = pd.DataFrame()

    df_result['ride_id'] = df['ride_id']
    df_result['tpep_pickup_datetime'] = df['tpep_pickup_datetime']
    df_result['PULocationID'] = df['PULocationID']
    df_result['DOLocationID'] = df['DOLocationID']
    df_result['actual_duration'] = df['duration']
    df_result['predicted_duration'] = y_pred
    df_result['diff'] = df_result['actual_duration'] - df_result['predicted_duration']
    df_result['model_version'] = run_id

    if not os.path.exists('./output'):
        os.makedirs('./output')
    if not os.path.exists(f'./output/{taxi_type}'):
        os.makedirs(f'./output/{taxi_type}')

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
    use_local_model = bool(sys.argv[4])

    input_file = f'https://d37ci6vzurychx.cloudfront.net/trip-data/{taxi_type}_tripdata_{year:04d}-{month:02d}.parquet'
    output_file = f'output/{taxi_type}/{year:04d}-{month:02d}.parquet'

    # RUN_ID = os.getenv('RUN_ID','00b0567f62f248a689ccede5fb2bc156')
    run_id = '00b0567f62f248a689ccede5fb2bc156'

    apply_model(
        input_file=input_file,
        run_id=run_id,
        output_file=output_file,
        use_local_model=use_local_model,
        taxi_type=taxi_type
    )


if __name__ == '__main__':
    ride_duration_prediction()

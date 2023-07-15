#!/usr/bin/env python
# coding: utf-8
import os
import sys
import pickle
import pandas as pd


def prepare_data(df, categorical):
    """Prepare dataframe with duration column."""
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')

    return df


def get_s3_options(S3_ENDPOINT_URL):
    options = {'client_kwargs': {'endpoint_url': S3_ENDPOINT_URL}}
    return options


def save_data(df, S3_ENDPOINT_URL, output_file):
    """Save data back to S3 bucket."""
    s3_options = get_s3_options(S3_ENDPOINT_URL)
    df.to_parquet(
        output_file,
        engine='pyarrow',
        compression=None,
        index=False,
        storage_options=s3_options,
    )


def read_data(filename, S3_ENDPOINT_URL):
    s3_options = get_s3_options(S3_ENDPOINT_URL)

    if S3_ENDPOINT_URL:
        df = pd.read_parquet(filename, storage_options=s3_options)
    else:
        df = pd.read_parquet(filename)

    return df


def get_input_path(year, month):
    default_input_pattern = 'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet'
    input_pattern = os.getenv('INPUT_FILE_PATTERN', default_input_pattern)
    return input_pattern.format(year=year, month=month)


def get_output_path(year, month):
    default_output_pattern = 's3://nyc-duration-prediction-alexey/taxi_type=fhv/year={year:04d}/month={month:02d}/predictions.parquet'
    output_pattern = os.getenv('OUTPUT_FILE_PATTERN', default_output_pattern)
    return output_pattern.format(year=year, month=month)


def main(year, month, S3_ENDPOINT_URL):
    # input_file = f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet'
    input_file = get_input_path(year, month)
    output_file = get_output_path(year, month)

    with open('../model.bin', 'rb') as f_in:
        dv, lr = pickle.load(f_in)

    print('Loading ML model')

    categorical = ['PULocationID', 'DOLocationID']
    df = read_data(input_file, S3_ENDPOINT_URL)
    df = prepare_data(df, categorical)
    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')

    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = lr.predict(X_val)

    print('predicted mean duration:', y_pred.mean())

    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['predicted_duration'] = y_pred

    sum_predicted_duration = df_result['predicted_duration'].sum()
    print(f'predicted duration sum = {sum_predicted_duration}')
    output_file = get_output_path(year, month)
    print('Saving file to s3...')
    save_data(df_result, S3_ENDPOINT_URL, output_file)


if __name__ == '__main__':
    year = int(sys.argv[1])
    month = int(sys.argv[2])
    print(f'Year passed = {year}, Month passed = {month}')
    S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL', 'http://localhost:4566')
    main(year, month, S3_ENDPOINT_URL)

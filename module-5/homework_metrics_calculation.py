import time
import random
import logging
import uuid
import pytz
import joblib
import pandas as pd
import psycopg
from datetime import datetime, timedelta

from evidently.report import Report
from evidently import ColumnMapping
from evidently.metrics import (
    ColumnDriftMetric,
    DatasetDriftMetric,
    DatasetMissingValuesMetric,
    ColumnQuantileMetric
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

SEND_TIMEOUT = 10
rand = random.Random()

create_table = """
    DROP TABLE IF EXISTS homework_metrics;
    CREATE TABLE homework_metrics (
        timestamp timestamp,
        prediction_drift integer,
        num_drifted_columns varchar,
        share_missing_values float,
        mean_quantile_metric_value float
    );
"""

reference_data = pd.read_parquet('data/reference.parquet')
with open('models/lin_reg.bin', 'rb') as f_in:
    model = joblib.load(f_in)

raw_data = pd.read_parquet('data/green_tripdata_2023-03.parquet')
begin = datetime(2023, 3, 1, 0, 0, 0)

logging.info('Predicting column quantile metric.')

num_features = ['passenger_count', 'trip_distance', 'fare_amount', 'total_amount']
cat_features = ['PULocationID', 'DOLocationID']
column_mapping = ColumnMapping(
    prediction='prediction',
    numerical_features=num_features,
    categorical_features=cat_features,
    target=None
)

report = Report(metrics=[
    ColumnDriftMetric(column_name='prediction'),
    DatasetDriftMetric(),
    DatasetMissingValuesMetric(),
    ColumnQuantileMetric(column_name='fare_amount', quantile=0.5)
])


def prep_db():
    with psycopg.connect("host=db port=5432 user=postgres password=example", autocommit=True) as conn:
        res = conn.execute("SELECT 1 FROM pg_database WHERE datname='test'")
        if len(res.fetchall()) == 0:
            conn.execute("create database test;")
        with psycopg.connect("host=db port=5432 user=postgres password=example", autocommit=True) as conn:
            conn.execute(create_table)
            logging.info('Table created.')


def calculate_metrics_postgresql(curr, i):
    current_data = raw_data[
        (raw_data.lpep_pickup_datetime >= (begin + timedelta(i))) &
        (raw_data.lpep_pickup_datetime < (begin + timedelta(i + 1)))
    ]

    # current_data.fillna(0, inplace=True)
    current_data['prediction'] = model.predict(current_data[num_features + cat_features].fillna(0))

    report.run(
        reference_data=reference_data,
        current_data=current_data,
        column_mapping=column_mapping
    )

    result = report.as_dict()

    prediction_drift = result['metrics'][0]['result']['drift_score']
    num_drifted_columns = result['metrics'][1]['result']['number_of_drifted_columns']
    share_missing_values = result['metrics'][2]['result']['current']['share_of_missing_values']
    quantile_mean_value = result['metrics'][3]['result']['current']['value']
    timestamp_value = begin + timedelta(i)

    insert_statement = f"""
        insert into homework_metrics(
            timestamp,
            prediction_drift,
            num_drifted_columns,
            share_missing_values,
            mean_quantile_metric_value
        ) values (
            '{timestamp_value}',
            {prediction_drift},
            '{num_drifted_columns}',
            {share_missing_values},
            {quantile_mean_value}
        )
    """

    curr.execute(insert_statement)


def batch_monitoring_backfill():
    prep_db()
    last_send = datetime.now() - timedelta(seconds=10)
    with psycopg.connect("host=db port=5432 user=postgres password=example", autocommit=True) as conn:
        for i in range(0, 20):
            with conn.cursor() as curr:
                calculate_metrics_postgresql(curr, i)

            new_send = datetime.now()
            seconds_elapsed = (new_send - last_send).total_seconds()
            if seconds_elapsed < SEND_TIMEOUT:
                time.sleep(SEND_TIMEOUT - seconds_elapsed)
            while last_send < new_send:
                last_send = last_send + timedelta(seconds=10)
            logging.info("data sent")


if __name__ == '__main__':
    batch_monitoring_backfill()

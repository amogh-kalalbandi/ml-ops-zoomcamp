import os
import boto3
import pandas as pd

from test_batch import create_test_dataframe


def test_integration_of_simple_storage():
    S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL', 'http://localhost:4566')
    options = {'client_kwargs': {'endpoint_url': S3_ENDPOINT_URL}}
    df = create_test_dataframe()
    year = 2022
    month = 1
    input_file = f's3://nyc-duration/in/{year:04d}-{month:02d}.parquet'

    df.to_parquet(
        input_file,
        engine='pyarrow',
        compression=None,
        index=False,
        storage_options=options,
    )

    os.system("python batch.py 2022 1")


if __name__ == '__main__':
    test_integration_of_simple_storage()

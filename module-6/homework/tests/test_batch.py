import os
import pandas as pd
from datetime import datetime

from batch import read_data, prepare_data


def dt(hour, minute, second=0):
    return datetime(2022, 1, 1, hour, minute, second)


def create_test_dataframe():
    data = [
        (None, None, dt(1, 2), dt(1, 10)),
        (1, None, dt(1, 2), dt(1, 10)),
        (1, 2, dt(2, 2), dt(2, 3)),
        (None, 1, dt(1, 2, 0), dt(1, 2, 50)),
        (2, 3, dt(1, 2, 0), dt(1, 2, 59)),
        (3, 4, dt(1, 2, 0), dt(2, 2, 1)),
    ]

    columns = [
        'PULocationID',
        'DOLocationID',
        'tpep_pickup_datetime',
        'tpep_dropoff_datetime',
    ]
    df = pd.DataFrame(data, columns=columns)

    return df


def test_read_data_method():
    """Test read data method of batch.py file."""
    df = create_test_dataframe()

    categorical = ['PULocationID', 'DOLocationID']
    transformed_df = prepare_data(df, categorical)

    expected_data = [
        (-1, -1, dt(1, 2), dt(1, 10), 8.0),
        (1, -1, dt(1, 2), dt(1, 10), 8.0),
        (1, 2, dt(2, 2), dt(2, 3), 1.0),
    ]

    columns = [
        'PULocationID',
        'DOLocationID',
        'tpep_pickup_datetime',
        'tpep_dropoff_datetime',
        'duration',
    ]
    expected_df = pd.DataFrame(expected_data, columns=columns)
    expected_df['PULocationID'] = expected_df['PULocationID'].astype(str)
    expected_df['DOLocationID'] = expected_df['DOLocationID'].astype(str)

    final_df = transformed_df == expected_df
    result_list = [final_df.all()[each_column] for each_column in columns]

    assert True is all(result_list)

import lambda_function


class ModelMock:
    def __init__(self, value):
        self.value = value

    def predict(self, X):
        n = len(X)
        return [self.value] * n


def test_prepare_features():
    ride = {
        'PULocationID': 130,
        'DOLocationID': 205,
        'trip_distance': 3.66,
    }

    actual_features = lambda_function.prepare_features(ride)

    expected_features = {
        'PU_DO': '130_205',
        'trip_distance': 3.66,
    }

    assert actual_features == expected_features


def test_predict():
    actual_features = {
        'PU_DO': '130_205',
        'trip_distance': 3.66,
    }

    model = ModelMock(10.0)
    actual_prediction = lambda_function.predict(actual_features)

    X = [1]
    expected_prediction = model.predict(X)[0]

    assert expected_prediction == actual_prediction

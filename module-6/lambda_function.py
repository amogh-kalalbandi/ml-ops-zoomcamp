def prepare_features(ride):
    features = {}
    features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
    features['trip_distance'] = ride['trip_distance']
    return features


def predict(features):
    """Return linear regression precitions."""
    # preds = model.predict(features)
    return float(10.0)
    # return float(preds[0])


def lambda_handler(event, context):
    ride = event['ride']
    ride_id = event['ride_id']

    features = prepare_features(ride)
    prediction = predict(features)
    # print(json.dumps(event))

    return {
        'ride_duration': prediction,
        'ride_id': ride_id,
    }

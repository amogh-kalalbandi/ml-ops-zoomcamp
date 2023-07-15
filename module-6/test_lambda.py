import json
import lambda_function

event_dict = {
    'ride': {
        'PULocationID': 130,
        'DOLocationID': 205,
        'trip_distance': 3.66,
    },
    'ride_id': 123,
}

print(json.dumps(lambda_function.lambda_handler(event_dict, None)))

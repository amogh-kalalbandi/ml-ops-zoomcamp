import json
import requests
from deepdiff import DeepDiff

with open('event.json', 'r', encoding='utf-8') as f_open:
    event_dict = json.loads(f_open.read())

LAMBDA_URL = 'http://localhost:8080/2015-03-31/functions/function/invocations'
actual_response = requests.post(
    LAMBDA_URL, json=event_dict
).json()  # pylint: disable=missing-timeout
print(actual_response)

expected_response = {
    'ride_duration': 10.0,
    'ride_id': 123,
}

diff = DeepDiff(actual_response, expected_response, significant_digits=1)
print(f'diff={diff}')

assert 'type_changes' not in diff
assert 'values_changed' not in diff

import json
import lambda_function

with open('event.json', 'r', encoding='utf-8') as f_open:
    event_dict = json.loads(f_open.read())

print(json.dumps(lambda_function.lambda_handler(event_dict, None)))

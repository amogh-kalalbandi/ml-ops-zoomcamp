import requests
import json

ride = {
    'PULocationID': '72',
    'DOLocationID': '260',
    'trip_distance': 10
}

url = 'http://localhost:9696/predict'

response = requests.post(url, json=ride)
print(response.json())

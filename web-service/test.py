#import predict
import pandas as pd

import requests


ride = {
    'PULocationID': 43,
    'DOLocationID': 215,
    'datetime': '2021-01-01 00:15:56',
    'trip_distance': 14
}

url = 'http://localhost:9696/endpoint_predict'
response = requests.post(url, json=ride)
print(response.json())

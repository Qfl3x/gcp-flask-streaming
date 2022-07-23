import os
import requests
import subprocess
import base64
import json

from pathlib import Path

from requests.packages.urllib3.util.retry import Retry


def test_framework():

    ride = {
    'PULocationID': 43,
    'DOLocationID': 215,
    'datetime': '2021-01-01 00:15:56',
    'trip_distance': 14
}

    port = 8898
    ride_json = json.dumps(ride)
    encoded_ride = base64.b64encode(ride_json.encode('utf-8')).decode('utf-8')

    pubsub_message = {
        'data' : {'data': encoded_ride}
    }

    current_path = Path(os.path.dirname(__file__))

    parent_path = current_path.parent
    process = subprocess.Popen(
      [
        'functions-framework',
        '--target', 'predict_duration',
        '--signature-type', 'event',
        '--port', str(port)
      ],
      cwd=parent_path,
      stdout=subprocess.PIPE
    )

    url = f'http://localhost:{port}/'

    retry_policy = Retry(total=6, backoff_factor=1)
    retry_adapter = requests.adapters.HTTPAdapter(
      max_retries=retry_policy)

    session = requests.Session()
    session.mount(url, retry_adapter)

    response = session.post(url, json=pubsub_message)

    assert response.status_code == 200

    # Stop the functions framework process
    process.kill()
    process.wait()
    out, err = process.communicate()

    print(out, err, response.content)

    assert 'duration_final' in str(out)


def test_framework_second_proc():

    ride = {
    'PULocationID': 43,
    'DOLocationID': 215,
    'datetime': '2021-01-01 00:15:56',
    'trip_distance': 14
}

    port = 8898
    ride_json = json.dumps(ride)
    encoded_ride = base64.b64encode(ride_json.encode('utf-8')).decode('utf-8')

    pubsub_message = {
        'data' : {'data': encoded_ride}
    }

    current_path = Path(os.path.dirname(__file__))

    parent_path = current_path.parent
    process = subprocess.Popen(
      [
        'functions-framework',
        '--target', 'predict_duration',
        '--signature-type', 'event',
        '--port', str(port)
      ],
      cwd=parent_path,
      stdout=subprocess.PIPE
    )

    url = f'http://localhost:{port}/'

    retry_policy = Retry(total=6, backoff_factor=1)
    retry_adapter = requests.adapters.HTTPAdapter(
      max_retries=retry_policy)

    session = requests.Session()
    session.mount(url, retry_adapter)

    response = session.post(url, json=pubsub_message)

    assert response.status_code == 200

    response2 = session.post(url, json=pubsub_message)

    assert response2.status_code == 200

    # Stop the functions framework process
    process.kill()
    process.wait()
    out, err = process.communicate()

    print(out, err, response.content)

    assert 'reinitiated: True' in str(out)
    assert 'reinitiated: False' in str(out)

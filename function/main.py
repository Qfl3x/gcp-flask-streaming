import os

import base64
import warnings
warnings.filterwarnings('ignore')
import json


import pickle

import xgboost as xgb

from google.cloud import pubsub_v1
from google.cloud import storage

publisher = pubsub_v1.PublisherClient()
PROJECT_ID = os.getenv("PROJECT_ID")
TOPIC_NAME = os.getenv("BACKEND_PULL_STREAM")
MODEL_BUCKET = os.getenv("MODEL_BUCKET")

def download_files():

    storage_client = storage.Client()

    bucket = storage_client.bucket(MODEL_BUCKET)

    preprocessor_blob = bucket.blob("model/preprocessor.py")
    dv_blob = bucket.blob("model/dv.pkl")
    model_blob = bucket.blob("model/model.xgb")

    preprocessor_blob.download_to_filename("/tmp/preprocessor.py")
    dv_blob.download_to_filename("/tmp/dv.pkl")
    model_blob.download_to_filename("/tmp/model.xgb")

    print("SUCCESS")
    
    preprocessor_full_blob = bucket.get_blob("model/preprocessor.py")
    model_full_blob = bucket.get_blob("model/model.xgb")

    preprocessor_modif_date = preprocessor_full_blob.updated
    model_modif_date = model_full_blob.updated

    last_modif = min(preprocessor_modif_date, model_modif_date)
    return last_modif

def get_last_modif():

    storage_client = storage.Client()

    bucket = storage_client.bucket(MODEL_BUCKET)

    preprocessor_full_blob = bucket.get_blob("model/preprocessor.py")
    model_full_blob = bucket.get_blob("model/model.xgb")

    preprocessor_modif_date = preprocessor_full_blob.updated
    model_modif_date = model_full_blob.updated

    last_modif = max(preprocessor_modif_date, model_modif_date)
    return last_modif


files_date_init = download_files()
import sys

sys.path.insert(0,'/tmp/')
from preprocessor import preprocess_dict

def send(message_json):
        
        topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)

        message_bytes = message_json.encode('utf-8')
        print(message_bytes)
    
        try:
            publish_future = publisher.publish(topic_path, data=message_bytes)
            publish_future.result()  # Verify the publish succeeded

            return 'Message published.'
        except Exception as e:
            print(e)
            return (e,500)


def vectorize(D):
    
    with open('/tmp/dv.pkl', 'rb') as f_in:
        dv = pickle.load(f_in)

    return dv.transform(D)

def predict(X):

    booster = xgb.Booster({'verbosity':0, 'silent':True})
    booster.load_model('/tmp/model.xgb')
    
    X_predict = xgb.DMatrix(X)
    return booster.predict(X_predict)[0]

def predict_duration(event, context):

    last_modif = get_last_modif()
    
    global initiated
    global files_date

    try:
        initiated
        last_modif = get_last_modif()
        if last_modif > files_date:
            last_modif = download_files()
            
            import sys
            sys.path.insert(0, '/tmp')
            from preprocessor import preprocess_dict
            files_date = last_modif
    except:
        initiated = True
        files_date = files_date_init
        import sys
        sys.path.insert(0, '/tmp')
        from preprocessor import preprocess_dict
 

    ride = base64.b64decode(event['data']).decode('utf-8')
    ride = json.loads(ride)

    D = preprocess_dict(ride)
    X = vectorize(ride)
    predicted_duration = round(predict(X))
    return_dict = {'duration_final': predicted_duration}
    send(json.dumps(return_dict))

if __name__ == "__main__":

    ride = {'datetime': '2022-06-23 11:36:42',
            'PULocationID': 34,
            'DOLocationID': 56,
            'trip_distance': 12
            }
    D = preprocess_dict(ride)
    X = vectorize(D)
    print(predict(X))
    

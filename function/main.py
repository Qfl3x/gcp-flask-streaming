import base64
import warnings
warnings.filterwarnings('ignore')
import json

from preprocess_complex_green import preprocess_dict

import pickle

import xgboost as xgb

from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()
PROJECT_ID = os.getenv("PROJECT_ID")
TOPIC_NAME = os.getenv("BACKEND_PUSH_STREAM")

topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)

def send(message_json):
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
    
    with open('dv_xgboost.pkl', 'rb') as f_in:
        dv = pickle.load(f_in)

    return dv.transform(D)

def predict(X):

    booster = xgb.Booster({'verbosity':0, 'silent':True})
    booster.load_model('model.xgb')
    
    X_predict = xgb.DMatrix(X)
    return booster.predict(X_predict)[0]

def predict_duration(event, context):
    ride = base64.b64decode(event['data']).decode('utf-8')
    print(ride)
    ride = json.loads(ride)
    D = preprocess_dict(ride)
    X = vectorize(ride)
    predicted_duration = round(predict(X))
    return_dict = {'duration_final': predicted_duration}
    print(return_dict)
    send(json.dumps(return_dict))
    print("SENT")

if __name__ == "__main__":

    ride = {'datetime': '2022-06-23 11:36:42',
            'PULocationID': 34,
            'DOLocationID': 56,
            'trip_distance': 12
            }
    D = preprocess_dict(ride)
    X = vectorize(D)
    print(predict(X))
    

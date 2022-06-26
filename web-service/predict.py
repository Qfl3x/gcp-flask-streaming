import base64
import pandas as pd

import pickle

from sklearn.linear_model import LinearRegression
from sklearn.feature_extraction import DictVectorizer

from preprocess_simple_green import preprocess_dict

import json
from google.cloud import pubsub_v1


PROJECT_ID = 'mlops-zoomcamp-352510'
publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()

PUBLISHER_TOPIC_NAME = "duration-stream"
SUBSCRIPTION_ID = "prediction-stream-sub"

timeout = 20.

publisher_path = publisher.topic_path(PROJECT_ID, PUBLISHER_TOPIC_NAME)
subscriber_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)


def send_to_stream(message_json):
    message_bytes = message_json.encode('utf-8')

    try:
        publish_future = publisher.publish(publisher_path, data=message_bytes)
        publish_future.result()

        return 'Message published.'
    except Exception as e:
        print(e)
        return(e,500)

def receive_from_stream():
   # def callback(message: pubsub_v1.subscriber.message.Message) -> None:
   #     print(f"Received {message.data!r}.")
   #     if message.attributes:
   #         print("Attributes:")
   #         for key in message.attributes:
   #             value = message.attributes.get(key)
   #             print(f"{key}: {value}")
   #     message.ack()

   # streaming_pull_future = subscriber.subscribe(subscriber_path, callback=callback)
   # print(f"Listening for messages on {subscriber_path}..\n")

   # with subscriber:
   #         try:
   #             result = streaming_pull_future.result(timeout=timeout)
   #             print(result)
   #             return result
   #             
   #         except TimeoutError:
   #             streaming_pull_future.cancel()  # Trigger the shutdown.
   #             streaming_pull_future.result()  # Block until the shutdown is complete.
   # return 0
    
    response = subscriber.pull(
        request={
            "subscription": subscriber_path,
            "max_messages": 1,
        }
    )
    msg = response.received_messages[0]
    ack_id = msg.ack_id
    subscriber.acknowledge(
            request={
                "subscription": subscriber_path,
                "ack_ids": [ack_id]
            }
    )
    data = msg.message.data
    print(data)
    data = json.loads(data)
    print(data)
    return data
    
                                                                
with open('dv_simple_linreg.pkl', 'rb') as f_in:
    dv = pickle.load(f_in)

with open('model.pkl', 'rb') as f_in:
    lr = pickle.load(f_in)
   
    
def predict(features):
    X = dv.transform(features)

    return round(lr.predict(X)[0])


from flask import Flask, request, jsonify

app = Flask('duration_predict')

@app.route('/endpoint_predict',methods=['POST','GET'])

def endpoint_predict():
    ride = request.get_json()

    features = preprocess_dict(ride)

    #return features
    pred_init = predict(features)
    print("Finished backend prediction")
    #Send data to the prediction stream
    print(ride)
    print(type(ride))
    message_bytes = json.dumps(ride)
    print("SERIALIZED")
    send_to_stream(message_bytes)
    print("SENT")
    #Receive data from  the output stream
    pred_final = receive_from_stream()['duration_final']

    return_dict = {'duration_init': pred_init,
                   'duration_fin': pred_final}

    return jsonify(return_dict)
    
if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=9696)

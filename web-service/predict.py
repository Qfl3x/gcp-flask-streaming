import base64
import json
import os
import pickle

import pandas as pd
from dotenv import load_dotenv
from google.cloud import pubsub_v1
from preprocess_simple_green import preprocess_dict
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()

PUBLISHER_TOPIC_NAME = os.getenv("BACKEND_PUSH_STREAM")
SUBSCRIPTION_ID = os.getenv("BACKEND_PULL_SUBSCRIBER_ID")

timeout = 20.0

print(PUBLISHER_TOPIC_NAME)

publisher_path = publisher.topic_path(PROJECT_ID, PUBLISHER_TOPIC_NAME)
subscriber_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)


def send_to_stream(message_json):
    message_bytes = message_json.encode("utf-8")

    try:
        publish_future = publisher.publish(publisher_path, data=message_bytes)
        publish_future.result()

        return "Message published."
    except Exception as e:
        print(e)
        return (e, 500)


def receive():

    response = subscriber.pull(
        request={
            "subscription": subscriber_path,
            "max_messages": 1,
        }
    )
    msg = response.received_messages[0]
    ack_id = msg.ack_id
    subscriber.acknowledge(  # Acknowledge reception
        request={"subscription": subscriber_path, "ack_ids": [ack_id]}
    )
    data = msg.message.data
    data = json.loads(data)
    return data


with open("dv_simple_linreg.pkl", "rb") as f_in:
    dv = pickle.load(f_in)

with open("model.pkl", "rb") as f_in:
    lr = pickle.load(f_in)


def predict(features):
    X = dv.transform(features)

    return round(lr.predict(X)[0])


from flask import Flask, jsonify, request

app = Flask("duration_predict")


@app.route("/endpoint_predict", methods=["POST", "GET"])
def endpoint_predict():
    ride = request.get_json()

    features = preprocess_dict(ride)

    # return features
    pred_init = predict(features)
    print("Finished backend prediction")

    # Send data to the prediction stream
    message_bytes = json.dumps(ride)
    send_to_stream(message_bytes)

    # Receive data from  the output stream
    pred_final = receive()["duration_final"]

    return_dict = {"duration_init": pred_init, "duration_fin": pred_final}

    return jsonify(return_dict)


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=9696)

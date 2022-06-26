import os
import json
import base64

from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()
PROJECT_ID = os.getenv("PROJECT_ID")
TOPIC_NAME = os.getenv("BACKEND_PUSH_STREAM")

topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)

def send(message_json):
        message_bytes = message_json.encode('utf-8')
        print(message_bytes)
        encoded_message = base64.b64encode(message_bytes)
        print(encoded_message)
        try:
            publish_future = publisher.publish(topic_path, data=message_bytes)
            publish_future.result()  # Verify the publish succeeded

            return 'Message published.'
        except Exception as e:
            print(e)
            return (e,500)

ride = {'datetime':'2022-06-23 11:36:42',
        'PULocationID': 34,
        'DOLocationID': 56,
        'trip_distance': 12
        }
ride = json.dumps(ride)
send(ride)

""" main.py
Main file to be uploaded to GCP Functions; Function to be imported: predict_duration..
"""
import base64
import json

# pylint: disable=C0413, E0401, E0118, W0621, E0601, W0601, invalid-name
import os
import pickle
import sys
import warnings

warnings.filterwarnings("ignore")
import xgboost as xgb
from dotenv import load_dotenv
from google.cloud import pubsub_v1, storage

load_dotenv()

publisher = pubsub_v1.PublisherClient()
PROJECT_ID = os.getenv("PROJECT_ID")
TOPIC_NAME = os.getenv("BACKEND_PULL_STREAM")
MODEL_BUCKET = os.getenv("MODEL_BUCKET")


def download_files():
    """
    Download Files from GS Bucket"""
    storage_client = storage.Client()

    bucket = storage_client.bucket(MODEL_BUCKET)

    preprocessor_blob = bucket.blob("model/preprocessor.py")
    dv_blob = bucket.blob("model/dv.pkl")
    model_blob = bucket.blob("model/model.xgb")

    preprocessor_blob.download_to_filename("/tmp/preprocessor.py")
    dv_blob.download_to_filename("/tmp/dv.pkl")
    model_blob.download_to_filename("/tmp/model.xgb")

    preprocessor_full_blob = bucket.get_blob("model/preprocessor.py")
    model_full_blob = bucket.get_blob("model/model.xgb")

    preprocessor_modif_date = preprocessor_full_blob.updated
    model_modif_date = model_full_blob.updated

    last_modif = min(preprocessor_modif_date, model_modif_date)
    return last_modif


def get_last_modif():
    """
    Get last modification date on the files, outputs most recent modification"""
    storage_client = storage.Client()

    bucket = storage_client.bucket(MODEL_BUCKET)

    preprocessor_full_blob = bucket.get_blob("model/preprocessor.py")
    model_full_blob = bucket.get_blob("model/model.xgb")

    preprocessor_modif_date = preprocessor_full_blob.updated
    model_modif_date = model_full_blob.updated

    last_modif = max(preprocessor_modif_date, model_modif_date)
    return last_modif


files_date_init = download_files()

sys.path.insert(0, "/tmp/")
# pylint: disable=W0611
from preprocessor import preprocess_dict

# pylint: enable=W0611


def send(message_json):
    """
    Sends message to the Pull stream"""
    topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)

    message_bytes = message_json.encode("utf-8")
    print(message_bytes)
    # pylint: disable=W0703, C0103
    try:
        publish_future = publisher.publish(topic_path, data=message_bytes)
        publish_future.result()  # Verify the publish succeeded

        return "Message published."
    except Exception as e:
        print(e)
        return (e, 500)
    # pylint: enable=W0703, C0103


def vectorize(preprocessed_dict):
    """
    vectorize the preprocessed dictionary"""
    with open("/tmp/dv.pkl", "rb") as f_in:
        dict_vectorizer = pickle.load(f_in)

    return dict_vectorizer.transform(preprocessed_dict)


def predict(model_features):
    """
    Predict the features from vectorize"""
    booster = xgb.Booster({"verbosity": 0, "silent": True})
    booster.load_model("/tmp/model.xgb")
    # pylint: disable=C0103
    model_features_DMatrix = xgb.DMatrix(model_features)
    return booster.predict(model_features_DMatrix)[0]


# pylint: disable=W0613
def update_files(initiated, files_date):
    """
    Function to update the files incase they are modified"""
    last_modif = get_last_modif()
    if last_modif > files_date:
        last_modif = download_files()
        files_date = last_modif

    return files_date


def predict_duration(event, context):
    """
    Main function to be exported.
    Takes the event and outputs the prediction and sends it to the Pull stream"""

    global INITIATED
    global FILES_DATE

    # Make sure the files are always the most recent ones witout redownloading every time
    try:
        FILES_DATE = update_files(INITIATED, FILES_DATE)
        reinitiated = False
    except NameError:
        # global INITIATED
        # global FILES_DATE

        INITIATED = True
        FILES_DATE = files_date_init
        reinitiated = True

    sys.path.insert(0, "/tmp")
    # pylint: disable=W0404, C0415
    from preprocessor import preprocess_dict

    ride = base64.b64decode(event["data"]).decode("utf-8")
    ride = json.loads(ride)

    preprocessed_dict = preprocess_dict(ride)
    model_features = vectorize(preprocessed_dict)
    predicted_duration = round(predict(model_features))
    return_dict = {"duration_final": predicted_duration}
    print(f"duration_final: {predicted_duration}")
    print(f"reinitiated: {reinitiated}")
    send(json.dumps(return_dict))

import pickle

import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_squared_error


def read_dataframe(filepath):
    df = pd.read_parquet(filepath)

    df["duration"] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime
    df.duration = df.duration.apply(lambda td: td.total_seconds() / 60)

    df = df[(df.duration >= 1) & (df.duration <= 60)]

    categorical = ["PULocationID", "DOLocationID"]
    df[categorical] = df[categorical].astype(str)

    return df


def preprocess(filepath):  # Simple Preprocessor for Green data
    df = read_dataframe(filepath)

    print(len(df))

    df["PU_DO"] = df["PULocationID"] + "_" + df["DOLocationID"]

    return df


def preprocess_df(df):

    df["PU_DO"] = df["PULocationID"] + "_" + df["DOLocationID"]
    return df


def preprocess_dict(D):

    features = {}
    features["PU_DO"] = f"{D['PULocationID']}_{D['DOLocationID']}"
    features["trip_distance"] = D["trip_distance"]

    return features


categorical = ["PU_DO"]
numerical = ["trip_distance"]
target = "duration"

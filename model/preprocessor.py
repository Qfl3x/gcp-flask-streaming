import pickle

import holidays
import numpy as np
import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_squared_error


def preprocess(filepath, floor=True):
    data = pd.read_parquet(filepath)
    data["time"] = data.lpep_dropoff_datetime - data.lpep_pickup_datetime
    if floor:  # Floor or not Floor, the data is skewed. Check next cell.
        data["duration"] = np.floor(data.time.dt.total_seconds() / 60)
    else:
        data["duration"] = data.time.dt.total_seconds() / 60

    data = data.loc[data.duration >= 4].loc[
        data.duration <= 60
    ]  # I've used 4 minutes as the cutoff as it appears the distribution
    # is Highly erroneous for any time less than that. Could also bundle all times
    # less than 5 minutes under one label.

    us_holidays = holidays.US()
    data["date"] = data.lpep_dropoff_datetime.dt.date
    data["holiday"] = data.date.apply(
        lambda date: us_holidays.get(date)
    )  # Get holidays for each date.

    data["dayofweek"] = data.lpep_dropoff_datetime.dt.dayofweek
    data["departure_hour"] = data.lpep_dropoff_datetime.dt.hour

    data.drop(
        data.columns.difference(
            [
                "duration",
                "trip_distance",
                "PULocationID",
                "DOLocationID",
                "holiday",
                "dayofweek",
                "departure_hour",
            ]
        ),
        axis=1,
        inplace=True,
    )

    data["holiday_bin"] = (
        data.holiday != "None"
    )  # Treat all holidays the same. Necessary as our datasets are within 2 different months.
    # A better analysis would involve the entire year.
    data.drop("holiday", axis=1, inplace=True)

    categorical = [
        "PULocationID",
        "DOLocationID",
        "holiday_bin",
        "dayofweek",
        "departure_hour",
    ]
    numerical = ["trip_distance"]

    data[categorical] = data[categorical].astype("str")
    data["PU_DO"] = data.PULocationID + data.DOLocationID

    categorical = [
        "PU_DO",
        "PULocationID",
        "DOLocationID",
        "holiday_bin",
        "dayofweek",
        "departure_hour",
    ]

    return data


categorical = [
    "PU_DO",
    "PULocationID",
    "DOLocationID",
    "holiday_bin",
    "dayofweek",
    "departure_hour",
]
numerical = ["trip_distance"]
target = "duration"


def preprocess_dict(D):

    features = {}
    for feature in [
        "PULocationID",
        "DOLocationID",
    ]:  # Categorical Features that don't change
        features[feature] = str(D[feature])
    features["trip_distance"] = D["trip_distance"]

    # Simple date operations
    datetime = pd.to_datetime(D["datetime"], format="%Y-%m-%d %H:%M:%S")
    date = datetime.date()
    features["dayofweek"] = str(datetime.dayofweek)
    features["departure_hour"] = str(datetime.hour)

    # Holidays
    us_holidays = holidays.US()
    holiday = us_holidays.get(date)
    features["holiday_bin"] = str(holiday != None)

    # PU_DO encoding
    features["PU_DO"] = f"{features['PULocationID']}_{features['DOLocationID']}"
    return features


if __name__ == "__main__":
    ride = {
        "datetime": "2022-03-06 11:17:34",
        "PULocationID": 35,
        "DOLocationID": 12,
        "trip_distance": 12,
    }
    print(preprocess_dict(ride))

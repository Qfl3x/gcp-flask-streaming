import os
import sys

from dotenv import load_dotenv

sys.path.append("../")

from function import main

load_dotenv()


def test_prediction():

    ride = {
        "PULocationID": 43,
        "DOLocationID": 215,
        "datetime": "2021-01-01 00:15:56",
        "trip_distance": 14,
    }

    main.download_files()

    sys.path.insert(0, "/tmp")
    from preprocessor import preprocess_dict

    D = preprocess_dict(ride)
    X = main.vectorize(ride)
    predicted_duration = round(main.predict(X))

    assert predicted_duration == 36

    # PROJECT_ID = os.environ.get("PROJECT_ID")
    # assert False, f"{PROJECT_ID}"


if __name__ == "__main__":
    test_prediction()

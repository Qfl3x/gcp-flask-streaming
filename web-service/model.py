import pandas as pd
import numpy as np

import pickle

import holidays

from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Lasso
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error

def process_data(data, floor=True):
    data = data.copy()
    data['time'] = data.lpep_dropoff_datetime - data.lpep_pickup_datetime
    if floor: #Floor or not Floor, the data is skewed. Check next cell.
        data['time_minutes'] = np.floor(data.time.dt.total_seconds() / 60 )
    else:
        data['time_minutes'] = data.time.dt.total_seconds() / 60 
    
    data = data.loc[data.time_minutes >= 4].loc[data.time_minutes <= 60] #I've used 4 minutes as the cutoff as it appears the distribution
                                                                         #is Highly erroneous for any time less than that. Could also bundle all times
                                                                         #less than 5 minutes under one label.

    
    us_holidays = holidays.US()
    data['date'] = data.lpep_dropoff_datetime.dt.date
    data['holiday'] = data.date.apply(lambda date: us_holidays.get(date)) #Get holidays for each date.
    
    data['dayofweek'] = data.lpep_dropoff_datetime.dt.dayofweek
    data['departure_hour'] = data.lpep_dropoff_datetime.dt.hour
    
    data.drop(data.columns.difference(['time_minutes','trip_distance', 'PULocationID','DOLocationID', 'holiday', 'dayofweek', 'departure_hour']), axis=1, inplace=True)
    
    data['holiday_bin'] = data.holiday != 'None' #Treat all holidays the same. Necessary as our datasets are within 2 different months.
                                                 #A better analysis would involve the entire year.
    data.drop('holiday', axis=1, inplace=True)
    
    categorical = ['PULocationID','DOLocationID', 'holiday_bin', 'dayofweek', 'departure_hour']
    numerical =['trip_distance']

    data[categorical] = data[categorical].astype('str')
    data['PU_DO'] = data.PULocationID + data.DOLocationID
    
    categorical = ['PU_DO', 'PULocationID', 'DOLocationID', 'holiday_bin', 'dayofweek', 'departure_hour']
    data_dict = data[categorical + numerical].to_dict(orient='records')
    
    return data, data_dict, data['time_minutes']

class TimePredictionModel: #Class containing all our model.
    def __init__(self, model=LinearRegression(), transform=None, reverse_transform=None, round_=False):
        self.model = model
        self.transform = transform #Transform function, could be log for example
        self.reverse_transform = reverse_transform #Reverse Transform, Both Transform and Reverse Transform MUST be defined to transform the data.
        self.dictvectorizer = DictVectorizer()
        
        self.model_trained = False
        self.round = round_ #Whether to round the result or not. I've found that the data is highly skewed towards whole minute
    def fit(self, train_dict, y_train):
        assert  not self.model_trained, "Model already trained"
            
        X_train = self.dictvectorizer.fit_transform(train_dict)
        
        if self.transform == None or self.reverse_transform == None:
            self.model.fit(X_train, y_train)
        else:
            self.model.fit(X_train, self.transform(y_train))
        self.model_trained = True
        
    def predict(self, test_dict):
        assert self.model_trained, "Model Not yet trained, train with model.fit"
        X_test = self.dictvectorizer.transform(test_dict)
        
        if self.transform == None or self.reverse_transform == None:
            if self.round:
                return np.round(self.model.predict(X_test))
            else:
                return self.model.predict(X_test)
        else:
            if self.round:
                return np.round(self.reverse_transform(self.model.fit(X_test)))
            else:
                return self.reverse_transform(self.model.fit(X_test))
        
    def transform(self, test_dict):
        assert self.model_trained, "Model Not yet trained, train with model.fit"
        
        return self.dictvectorizer.transform(test_dict)
        
if __name__ == "__main__":
    
#     #Please download data and change the path
    data_jan = pd.read_parquet("data/green_tripdata_2021-01.parquet")
    data_feb = pd.read_parquet("data/green_tripdata_2021-02.parquet")
    
    _, train_dict, y_train = process_data(data_jan)

    Model = TimePredictionModel(round_=True)
    Model.fit(train_dict, y_train)

    with open("models/linreg.bin", 'wb') as f_out:
        pickle.dump(Model, f_out)
    
    
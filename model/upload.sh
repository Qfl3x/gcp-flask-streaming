#!/bin/sh


gsutil cp dv.pkl model.xgb preprocessor.py  gs://$MODEL_BUCKET/model/
#gsutil cp model.xgb gs://$MODEL_BUCKET/model/
#gsutil cp preprocessor.py gs://$MODEL_BUCKET/model/

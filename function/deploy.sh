#!/usr/bin/bash

gcloud functions deploy predict-duration --trigger-topic $BACKEND_PUSH_STREAM --runtime python39

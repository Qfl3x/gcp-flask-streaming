#!/bin/bash

gcloud functions deploy predict_duration \
       	--trigger-topic $BACKEND_PUSH_STREAM \
	--set-env-vars BACKEND_PULL_STREAM=$BACKEND_PULL_STREAM \
	--set-env-vars PROJECT_ID=$PROJECT_ID \
	--set-env-vars MODEL_BUCKET=$MODEL_BUCKET \
       	--runtime python39

#!/usr/bin/env bash

export GOOGLE_APPLICATION_CREDENTIALS="./service-account.json"
cd function/ && pipenv run pytest

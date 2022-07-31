FROM python:3.9-slim


ARG PROJECT_ID
ARG BACKEND_PUSH_STREAM
ARG BACKEND_PULL_SUBSCRIBER_ID

RUN pip install -U pip
RUN pip install pipenv
WORKDIR /app
COPY ["Pipfile", "Pipfile.lock", "predict.py", "preprocess_simple_green.py" , ".env", "./"]
RUN pipenv install --deploy --system
COPY ["model.pkl", "dv_simple_linreg.pkl", "service-account.json", "./"]
EXPOSE 9696

ENV PROJECT_ID=$PROJECT_ID
ENV BACKEND_PUSH_STREAM=$BACKEND_PUSH_STREAM
ENV BACKEND_PULL_SUBSCRIBER_ID=$BACKEND_PULL_SUBSCRIBER_ID
ENV GOOGLE_APPLICATION_CREDENTIALS="./service-account.json"

ENTRYPOINT ["gunicorn", "--bind=0.0.0.0:9696", "predict:app"]

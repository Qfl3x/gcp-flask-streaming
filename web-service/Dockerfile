FROM python:3.9-slim

RUN pip install -U pip
RUN pip install pipenv
WORKDIR /app
COPY ["Pipfile", "Pipfile.lock", "predict.py", "preprocess_simple_green.py" , "./"]
RUN pipenv install --deploy --system
COPY ["model.pkl", "dv_simple_linreg.pkl", "mlops-zoomcamp-352510-e2c35c9e4acf.json", "./"]
EXPOSE 9696
ENTRYPOINT ["gunicorn", "--bind=0.0.0.0:9696", "predict:app"]

# Example of a Backend Flask server calling a Google Cloud Function through a Google PubSub Stream


**web-service:** contains the web-service that will call the GC function

**function:** contains the function itself

**function/infrastructure:** Terraform infrastructure for initiating everything


**Note:** To run Pytest, make sure that the test bucket (`taxi-streaming-model` in this case) is up and contains the necessary files. Also make sure that the env variable `MODEL_BUCKET` corresponds to said bucket.

resource null_resource "zip_function_files" {
  provisioner "local-exec" {
    command = "touch function.zip && rm function.zip && zip -urj function.zip ../main.py ../requirements.txt ../service-account.json"
  }
}

resource "google_storage_bucket_object" "function_archive"{
  name = "function.zip"
  bucket = var.model_bucket_name
  source = "./function.zip"
  depends_on = [ null_resource.zip_function_files ]
}


resource "google_cloudfunctions_function" "function" {
  name = "${var.prefix}-duration-prediction"
  runtime = "python39"

  entry_point = "predict_duration"

  source_archive_bucket = var.model_bucket_name
  source_archive_object = google_storage_bucket_object.function_archive.name

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource = var.backend_push_stream_name
  }

  environment_variables = {
    PROJECT_ID = var.project_id
    MODEL_BUCKET = var.model_bucket_name
    BACKEND_PULL_STREAM = var.backend_pull_stream_name
    GOOGLE_APPLICATION_CREDENTIALS = "./service-account.json"
  }
}

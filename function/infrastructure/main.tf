terraform {
  required_version = ">=1.0"
  backend "gcs" {
    bucket = "mlops-terraform-state"
    prefix = "tfstate-stg"
    #credentials = "terraform-account.json"
  }
  required_providers {
    google = {
      source = "hashicorp/google"
  }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = "europe-west3"
  zone    = "europe-west3-c"
  #credentials = var.gcp_credentials
}

module "backend_push_stream" {
  source = "./modules/pubsub-topic"
  topic_name = "${var.prefix}-${var.backend_push_stream_name}"
  service-account = var.service-account
}

module "backend_pull_stream" {
  source = "./modules/pubsub-topic"
  topic_name = "${var.prefix}-${var.backend_pull_stream_name}"
  service-account = var.service-account
}

module "subscriber" {
  source = "./modules/pubsub-subscriber"
  subscriber_name = "${var.prefix}-${var.subscriber_name}"
  topic = module.backend_pull_stream.topic_name
  service-account = var.service-account
}

module "bucket" {
  source = "./modules/gs"
  bucket_name = "${var.prefix}-${var.bucket_name}"
  service-account = var.service-account
}


module "function" {
  source = "./modules/function"
  prefix = var.prefix
  backend_pull_stream_name = module.backend_pull_stream.topic_name
  backend_push_stream_name = module.backend_push_stream.topic_name
  project_id = var.gcp_project_id
  model_bucket_name = module.bucket.bucket_name
  depends_on = [ module.bucket ]
}
# Write .env file for the Flask backend
resource "local_file" "env_file" {

  content = <<EOT
PROJECT_ID=${var.gcp_project_id}
BACKEND_PUSH_STREAM=${var.prefix}-${var.backend_push_stream_name}
BACKEND_PULL_STREAM=${var.prefix}-${var.backend_pull_stream_name}
BACKEND_PULL_SUBSCRIBER_ID=${var.prefix}-${var.subscriber_name}
MODEL_BUCKET=${var.prefix}-${var.bucket_name}
GOOGLE_APPLICATION_CREDENTIALS=./service-account.json
EOT

  filename = "../../.env"
}

resource null_resource "copy_env_file" {
  provisioner "local-exec" {
    command = "cp ../../.env ../../web-service/"
  }
  depends_on = [local_file.env_file]
}

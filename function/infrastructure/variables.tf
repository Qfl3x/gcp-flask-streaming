variable "gcp_region" {
  description = "Region in GCP"
  default = "eu-west3"
}

variable "gcp_project_id" {
  description = "Project ID in GCP"
  default = "mlops-zoomcamp-352510"
}

variable "gcp_credentials" {
  default = "./terraform-account.json"
}
variable "prefix" {
  description = "Prefix for the services"
  default = "terraform-mlops"
}

variable "credentials" {
  default = "./terraform-account.json"
}

variable "backend_push_stream_name" {
  default = "backend-push-stream"
}

variable "backend_pull_stream_name" {
  default = "backend-pull-stream"
}

variable "subscriber_name" {
  default = "backend-pull-stream-sub"
}

variable "service-account" {
  default = "publisher@mlops-zoomcamp-352510.iam.gserviceaccount.com"
}

variable "bucket_name" {
  default = "taxi-model-bucket"
}

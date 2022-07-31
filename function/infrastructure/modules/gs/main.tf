resource "google_storage_bucket" "model_bucket" {
  name          = var.bucket_name
  location      = "EU"
  force_destroy = true

  provisioner "local-exec" {
    command = "cd ../../model && ./upload.sh"

    environment = {
    MODEL_BUCKET = var.bucket_name
    }
  }
}

output "bucket_name" {
  value = google_storage_bucket.model_bucket.name
}

resource "google_storage_bucket_iam_member" "member" {
  bucket        = google_storage_bucket.model_bucket.name
  role          = "roles/storage.objectViewer"
  member        = "serviceAccount:${var.service-account}"
}

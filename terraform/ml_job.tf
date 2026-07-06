# ---------------------------------------------------------------------------
# ML training pipeline — Cloud Run Job, weekly schedule
# ---------------------------------------------------------------------------

# Artifact Registry repo for ML job container images
resource "google_artifact_registry_repository" "ml_job" {
  location      = var.region
  repository_id = "spotify-ml-job"
  format        = "DOCKER"
  description   = "Container images for the ML training pipeline (Cloud Run Job)"
}

# Service account for the ML job
resource "google_service_account" "ml_job" {
  account_id   = "spotify-ml-job"
  display_name = "Spotify ML Training Job"
}

# IAM: allow ML job to write to marts
resource "google_bigquery_dataset_iam_member" "ml_job_bq_write" {
  dataset_id = google_bigquery_dataset.marts.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.ml_job.email}"
}

# IAM: allow ML job to read from raw (for training data)
resource "google_bigquery_dataset_iam_member" "ml_job_bq_read_raw" {
  dataset_id = google_bigquery_dataset.raw.dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = "serviceAccount:${google_service_account.ml_job.email}"
}

# Cloud Run Job — runs the ML training pipeline
resource "google_cloud_run_v2_job" "ml_training" {
  name         = "spotify-ml-training"
  location     = var.region
  template {
    task_count = 1

    template {
      max_retries     = 0
      timeout         = "600s"
      service_account = google_service_account.ml_job.email

      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.ml_job.repository_id}/ml-job:latest"

        env {
          name  = "BIGQUERY_PROJECT"
          value = var.project_id
        }
        env {
          name  = "BIGQUERY_DATASET"
          value = google_bigquery_dataset.marts.dataset_id
        }

        resources {
          limits = {
            cpu    = "2"
            memory = "1Gi"
          }
        }
      }
    }
  }

  depends_on = [google_project_service.services]
}

# Cloud Scheduler — runs ML training weekly (Sunday 6am UTC)
resource "google_cloud_scheduler_job" "ml_training_trigger" {
  name        = "spotify-ml-training-trigger"
  description = "Triggers ML training Cloud Run Job every Sunday at 06:00 UTC"
  schedule    = "0 6 * * 0"
  time_zone   = "Etc/UTC"

  retry_config {
    retry_count = 1
  }

  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.ml_training.name}:run"
    oauth_token {
      service_account_email = google_service_account.ml_job.email
    }
  }

  depends_on = [google_project_service.services]
}

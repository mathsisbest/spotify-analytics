# Cloud Run Job that runs dbt build against BigQuery
resource "google_cloud_run_v2_job" "dbt_build" {
  name     = "resonance-dbt-build"
  location = var.region

  template {
    task_count = 1
    template {
      max_retries     = 1
      timeout         = "900s"
      service_account = google_service_account.dbt_runner.email

      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.dbt_runner.repository_id}/dbt-runner:latest"

        env {
          name  = "GCP_PROJECT_ID"
          value = var.project_id
        }
        env {
          name  = "DBT_TARGET"
          value = "prod"
        }

        resources {
          limits = {
            cpu    = "1"
            memory = "512Mi"
          }
        }
      }
    }
  }
  depends_on = [google_project_service.services]
}

# Service account for dbt runner
resource "google_service_account" "dbt_runner" {
  account_id   = "resonance-dbt-runner"
  display_name = "Resonance dbt Build Runner"
}

# IAM: read raw + staging, write marts
resource "google_bigquery_dataset_iam_member" "dbt_read_raw" {
  dataset_id = google_bigquery_dataset.raw.dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = "serviceAccount:${google_service_account.dbt_runner.email}"
}

resource "google_bigquery_dataset_iam_member" "dbt_write_marts" {
  dataset_id = google_bigquery_dataset.marts.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.dbt_runner.email}"
}

resource "google_bigquery_dataset_iam_member" "dbt_write_staging" {
  dataset_id = google_bigquery_dataset.staging.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.dbt_runner.email}"
}

# Artifact Registry repo for the dbt runner image
resource "google_artifact_registry_repository" "dbt_runner" {
  location      = var.region
  repository_id = "resonance-dbt-runner"
  format        = "DOCKER"
  description   = "Container images for the dbt build runner"
}

# Cloud Scheduler — run dbt build every 6 hours
resource "google_cloud_scheduler_job" "dbt_build_trigger" {
  name        = "resonance-dbt-build-trigger"
  description = "Triggers dbt build Cloud Run Job every 6 hours"
  schedule    = "0 */6 * * *"
  time_zone   = "Etc/UTC"

  retry_config {
    retry_count = 1
  }

  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.dbt_build.name}:run"
    oauth_token {
      service_account_email = google_service_account.dbt_runner.email
    }
  }
}

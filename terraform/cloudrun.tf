# ---------------------------------------------------------------------------
# Cloud Run — Streamlit dashboard service
# ---------------------------------------------------------------------------
# Public ingress with IAM. Scales to 0 when idle (free tier).

# Artifact Registry repo for the dashboard container image
resource "google_artifact_registry_repository" "dashboard" {
  location      = var.region
  repository_id = "spotify-dashboard"
  format        = "DOCKER"
  description   = "Container images for the Streamlit dashboard"
}

# Service account for the Cloud Run service
resource "google_service_account" "dashboard" {
  account_id   = "spotify-dashboard"
  display_name = "Spotify Dashboard Service"
}

# IAM: allow dashboard to read BigQuery marts
resource "google_bigquery_dataset_iam_member" "dashboard_bq_read" {
  dataset_id = google_bigquery_dataset.marts.dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = "serviceAccount:${google_service_account.dashboard.email}"
}

resource "google_bigquery_dataset_iam_member" "dashboard_bq_read_raw" {
  dataset_id = google_bigquery_dataset.raw.dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = "serviceAccount:${google_service_account.dashboard.email}"
}

# Cloud Run service
resource "google_cloud_run_v2_service" "dashboard" {
  name         = "spotify-dashboard"
  location     = var.region
  description  = "Streamlit BI dashboard for Spotify listening analytics"
  ingress      = "INGRESS_TRAFFIC_ALL"
  launch_stage = "GA"

  template {
    scaling {
      min_instance_count = 0
      max_instance_count = 1
    }

    service_account = google_service_account.dashboard.email

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.dashboard.repository_id}/dashboard:latest"

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      env {
        name  = "BIGQUERY_PROJECT"
        value = var.project_id
      }
      env {
        name  = "BIGQUERY_DATASET"
        value = google_bigquery_dataset.marts.dataset_id
      }
    }
  }

  depends_on = [google_project_service.services]
}

# Allow public (unauthenticated) access to the dashboard
resource "google_cloud_run_v2_service_iam_member" "dashboard_public" {
  name     = google_cloud_run_v2_service.dashboard.name
  location = google_cloud_run_v2_service.dashboard.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

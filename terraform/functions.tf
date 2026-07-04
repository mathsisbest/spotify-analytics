# ---------------------------------------------------------------------------
# Cloud Function (gen2) — Polls Spotify Recently Played + Audio Features
# ---------------------------------------------------------------------------
# Triggered by Pub/Sub topic (fired by Cloud Scheduler every 2 minutes).
# Source code lives in ./functions/ at the repo root.

# Pub/Sub topic that triggers the function
resource "google_pubsub_topic" "ingestion_trigger" {
  name = "spotify-ingestion-trigger"
}

# Service account for the Cloud Function
resource "google_service_account" "ingestion_fn" {
  account_id   = "spotify-ingestion"
  display_name = "Spotify Ingestion Function"
}

# IAM: allow function to insert into BigQuery raw dataset
resource "google_bigquery_dataset_iam_member" "ingestion_bq_insert" {
  dataset_id = google_bigquery_dataset.raw.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.ingestion_fn.email}"
}

resource "google_bigquery_dataset_iam_member" "ingestion_bq_read_staging" {
  dataset_id = google_bigquery_dataset.staging.dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = "serviceAccount:${google_service_account.ingestion_fn.email}"
}

resource "google_bigquery_dataset_iam_member" "ingestion_bq_read_marts" {
  dataset_id = google_bigquery_dataset.marts.dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = "serviceAccount:${google_service_account.ingestion_fn.email}"
}

# IAM: allow function to read secrets (refresh token, client credentials)
resource "google_secret_manager_secret_iam_member" "ingestion_secret_refresh" {
  secret_id = google_secret_manager_secret.spotify_refresh_token.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.ingestion_fn.email}"
}

# Cloud Function (gen2) source code reference
resource "google_storage_bucket" "function_source" {
  name                        = "${var.project_id}-spotify-ingestion-source"
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true
}

# The Cloud Function itself
resource "google_cloudfunctions2_function" "ingestion" {
  name        = "spotify-ingestion"
  location    = var.region
  description = "Polls Spotify Recently Played API and loads results into BigQuery"

  build_config {
    runtime     = "python311"
    entry_point = "main" # function name in src/spotify_analytics/ingest.py
    source {
      storage_source {
        bucket = google_storage_bucket.function_source.name
        object = google_storage_bucket_object.function_source_zip.name
      }
    }
  }

  service_config {
    max_instance_count    = 1
    min_instance_count    = 0
    available_memory      = "128M"
    timeout_seconds       = 60
    service_account_email = google_service_account.ingestion_fn.email

    environment_variables = {
      SPOTIFY_CLIENT_ID       = var.spotify_client_id
      BIGQUERY_PROJECT        = var.project_id
      BIGQUERY_RAW_DATASET    = google_bigquery_dataset.raw.dataset_id
      BIGQUERY_MARTS_DATASET  = google_bigquery_dataset.marts.dataset_id
      BIGQUERY_STAGING_DATASET = google_bigquery_dataset.staging.dataset_id
    }

    secret_environment_variables {
      key        = "SPOTIFY_CLIENT_SECRET"
      project_id = var.project_id
      secret     = google_secret_manager_secret.spotify_client_secret.secret_id
      version    = "latest"
    }

    secret_environment_variables {
      key        = "SPOTIFY_REFRESH_TOKEN"
      project_id = var.project_id
      secret     = google_secret_manager_secret.spotify_refresh_token.secret_id
      version    = "latest"
    }
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.ingestion_trigger.id
    retry_policy   = "RETRY_POLICY_RETRY"
  }

  depends_on = [
    google_project_service.services,
    google_storage_bucket_object.function_source_zip,
  ]
}

# Zip up the functions source directory
resource "google_storage_bucket_object" "function_source_zip" {
  name   = "function-source-${data.archive_file.function_source.output_md5}.zip"
  bucket = google_storage_bucket.function_source.name
  source = data.archive_file.function_source.output_path
}

data "archive_file" "function_source" {
  type        = "zip"
  source_dir  = "${path.module}/../src/spotify_analytics"
  output_path = "${path.module}/.terraform/function-source.zip"

  excludes = ["__pycache__", "*.pyc", ".pytest_cache"]
}

# ── Spotify Client Secret (needed by function, also managed here) ──
resource "google_secret_manager_secret" "spotify_client_secret" {
  secret_id = "SPOTIFY_CLIENT_SECRET"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "spotify_client_secret_version" {
  secret      = google_secret_manager_secret.spotify_client_secret.id
  secret_data = var.spotify_client_secret
}

# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------

output "project_id" {
  description = "GCP project ID"
  value       = var.project_id
}

output "cloud_run_url" {
  description = "Cloud Run service URL for the Streamlit dashboard"
  value       = google_cloud_run_v2_service.dashboard.uri
}

output "scheduler_job_name" {
  description = "Cloud Scheduler job name"
  value       = google_cloud_scheduler_job.ingestion_trigger.name
}

output "function_name" {
  description = "Cloud Function (gen2) name"
  value       = google_cloudfunctions2_function.ingestion.name
}

output "bigquery_datasets" {
  description = "Map of dataset names to dataset IDs"
  value = {
    raw     = google_bigquery_dataset.raw.dataset_id
    staging = google_bigquery_dataset.staging.dataset_id
    marts   = google_bigquery_dataset.marts.dataset_id
  }
}

output "artifact_registry_repo" {
  description = "Artifact Registry repository for dashboard images"
  value       = google_artifact_registry_repository.dashboard.name
}

output "ml_job_name" {
  description = "Cloud Run Job name for ML training"
  value       = google_cloud_run_v2_job.ml_training.name
}

output "ml_scheduler_job_name" {
  description = "Cloud Scheduler job name for ML training trigger"
  value       = google_cloud_scheduler_job.ml_training_trigger.name
}

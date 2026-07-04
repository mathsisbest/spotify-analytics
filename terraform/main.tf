# GCP provider + enabled APIs + backend config
# terraform apply provisions the entire platform

terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }
  # Local backend for now; switch to GCS when team/CI requires state locking
  backend "local" {}
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required GCP service APIs
resource "google_project_service" "services" {
  for_each = toset([
    "bigquery.googleapis.com",
    "cloudfunctions.googleapis.com",
    "cloudscheduler.googleapis.com",
    "run.googleapis.com",
    "secretmanager.googleapis.com",
    "artifactregistry.googleapis.com",
    "pubsub.googleapis.com",
    "cloudbuild.googleapis.com",
  ])
  service            = each.key
  disable_on_destroy = false
}

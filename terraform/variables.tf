# ---------------------------------------------------------------------------
# Terraform variables for spotify-analytics
# ---------------------------------------------------------------------------
# Sensitive values (client_secret, refresh_token) should be supplied via
# environment variable or a .tfvars file that is *not* checked into VCS.

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for all resources"
  type        = string
  default     = "us-central1"
}

variable "spotify_client_id" {
  description = "Spotify Developer App client ID"
  type        = string
  sensitive   = false
}

variable "spotify_client_secret" {
  description = "Spotify Developer App client secret"
  type        = string
  sensitive   = true
}

variable "spotify_refresh_token" {
  description = "Spotify OAuth refresh token (obtained via manual one-time auth flow)"
  type        = string
  sensitive   = true
}

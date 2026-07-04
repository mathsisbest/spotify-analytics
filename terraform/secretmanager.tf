# ---------------------------------------------------------------------------
# Secret Manager — Spotify refresh token placeholder
# ---------------------------------------------------------------------------
# The refresh token is required for non-interactive OAuth. Obtain it via the
# manual one-time auth flow, then set in terraform.tfvars or environment.

resource "google_secret_manager_secret" "spotify_refresh_token" {
  secret_id = "SPOTIFY_REFRESH_TOKEN"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "spotify_refresh_token_version" {
  secret      = google_secret_manager_secret.spotify_refresh_token.id
  secret_data = var.spotify_refresh_token
}

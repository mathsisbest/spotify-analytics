# ---------------------------------------------------------------------------
# Cloud Scheduler — triggers the ingestion function every 2 minutes
# ---------------------------------------------------------------------------
# Publishes a message to the Pub/Sub topic every 2 minutes; the gen2 Cloud
# Function is subscribed to that topic and runs on each message.

resource "google_cloud_scheduler_job" "ingestion_trigger" {
  name        = "spotify-ingestion-trigger"
  description = "Triggers Spotify ingestion Cloud Function every 2 minutes"
  schedule    = "*/2 * * * *"
  time_zone   = "Etc/UTC"

  pubsub_target {
    topic_name = google_pubsub_topic.ingestion_trigger.id
    data       = base64encode("{}")
  }

  depends_on = [google_project_service.services]
}

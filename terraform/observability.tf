# Cloud Monitoring Notification Channel (Email)
resource "google_monitoring_notification_channel" "email" {
  display_name = "Resonance DevOps Email Alerts"
  type         = "email"
  labels = {
    email_address = var.alert_email
  }
}

# Cloud Monitoring Log-Based Metric for Ingestion Failures
resource "google_logging_metric" "ingestion_failures" {
  name        = "spotify_ingestion_error_count"
  description = "Count of ingestion execution errors logged by Spotify ingestion function"
  filter      = "resource.type=\"cloud_run_revision\" AND textPayload:\"ERROR\""
  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
  }
}

# Alert Policy for Ingestion Failures
resource "google_monitoring_alert_policy" "ingestion_error_alert" {
  display_name = "Resonance - Spotify Ingestion Failure Alert"
  combiner     = "OR"
  conditions {
    display_name = "Ingestion error count > 0"
    condition_threshold {
      filter          = "metric.type=\"logging.googleapis.com/user/${google_logging_metric.ingestion_failures.name}\" AND resource.type=\"cloud_run_revision\""
      duration        = "60s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }
  notification_channels = [google_monitoring_notification_channel.email.name]
}

# Uptime Check for Cloud Run Dashboard Endpoint
resource "google_monitoring_uptime_check_config" "dashboard_uptime" {
  display_name = "Resonance Dashboard Uptime Check"
  timeout      = "10s"
  period       = "300s"

  http_check {
    path         = "/_stcore/health"
    port         = 443
    use_ssl      = true
    validate_ssl = true
  }

  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = "${google_cloud_run_v2_service.dashboard.name}-${var.project_id}.${var.region}.run.app"
    }
  }
}

# ---------------------------------------------------------------------------
# BigQuery — three medallion datasets with sensible default table expirations
# ---------------------------------------------------------------------------

# ── Raw ingestion layer (data as-received from Spotify API) ──
resource "google_bigquery_dataset" "raw" {
  dataset_id                  = "raw"
  friendly_name               = "Spotify Raw Ingestion"
  description                 = "Raw ingestion layer — Spotify API responses as-is"
  location                    = var.region
  default_table_expiration_ms = 30 * 24 * 60 * 60 * 1000 # 30 days
  labels = {
    layer = "raw"
  }
}

resource "google_bigquery_table" "streaming_history" {
  dataset_id = google_bigquery_dataset.raw.dataset_id
  table_id   = "streaming_history"
  schema     = jsonencode([
    { name = "track_id",       type = "STRING", mode = "REQUIRED" },
    { name = "track_name",     type = "STRING", mode = "REQUIRED" },
    { name = "artist_name",    type = "STRING", mode = "REQUIRED" },
    { name = "artist_ids",     type = "STRING", mode = "REPEATED" },
    { name = "album_name",     type = "STRING", mode = "NULLABLE" },
    { name = "album_id",       type = "STRING", mode = "NULLABLE" },
    { name = "played_at",      type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "context",        type = "STRING", mode = "NULLABLE" },
    { name = "ingested_at",    type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "duration_ms",    type = "INTEGER", mode = "NULLABLE" },
    { name = "is_playing",     type = "BOOL", mode = "NULLABLE" },
  ])
  clustering = ["track_id", "played_at"]
  labels = {
    layer = "raw"
  }
}

resource "google_bigquery_table" "track_features" {
  dataset_id = google_bigquery_dataset.raw.dataset_id
  table_id   = "track_features"
  schema     = jsonencode([
    { name = "track_id",          type = "STRING",  mode = "REQUIRED" },
    { name = "danceability",      type = "FLOAT64", mode = "NULLABLE" },
    { name = "energy",            type = "FLOAT64", mode = "NULLABLE" },
    { name = "key",               type = "INTEGER", mode = "NULLABLE" },
    { name = "loudness",          type = "FLOAT64", mode = "NULLABLE" },
    { name = "mode",              type = "INTEGER", mode = "NULLABLE" },
    { name = "speechiness",       type = "FLOAT64", mode = "NULLABLE" },
    { name = "acousticness",      type = "FLOAT64", mode = "NULLABLE" },
    { name = "instrumentalness",  type = "FLOAT64", mode = "NULLABLE" },
    { name = "liveness",          type = "FLOAT64", mode = "NULLABLE" },
    { name = "valence",           type = "FLOAT64", mode = "NULLABLE" },
    { name = "tempo",             type = "FLOAT64", mode = "NULLABLE" },
    { name = "time_signature",    type = "INTEGER", mode = "NULLABLE" },
    { name = "fetched_at",        type = "TIMESTAMP", mode = "REQUIRED" },
  ])
  clustering = ["track_id"]
  labels = {
    layer = "raw"
  }
}

resource "google_bigquery_table" "ingestion_runs" {
  dataset_id = google_bigquery_dataset.raw.dataset_id
  table_id   = "ingestion_runs"
  schema     = jsonencode([
    { name = "run_id",         type = "STRING",   mode = "REQUIRED" },
    { name = "started_at",     type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "finished_at",    type = "TIMESTAMP", mode = "NULLABLE" },
    { name = "status",         type = "STRING",   mode = "REQUIRED" },
    { name = "tracks_ingested", type = "INTEGER", mode = "NULLABLE" },
    { name = "features_fetched", type = "INTEGER", mode = "NULLABLE" },
    { name = "error_message",  type = "STRING",   mode = "NULLABLE" },
  ])
  labels = {
    layer = "raw"
  }
}

# ── Staging layer (cleaned/typed views for dbt) ──
resource "google_bigquery_dataset" "staging" {
  dataset_id                  = "staging"
  friendly_name               = "dbt Staging"
  description                 = "Staging layer — cleaned, typed views over raw data"
  location                    = var.region
  default_table_expiration_ms = 7 * 24 * 60 * 60 * 1000 # 7 days
  labels = {
    layer = "staging"
  }
}

# ── Marts layer (analytical models for dashboard and ML) ──
resource "google_bigquery_dataset" "marts" {
  dataset_id                  = "marts"
  friendly_name               = "dbt Marts"
  description                 = "Marts layer — analytical fact/dimension tables"
  location                    = var.region
  default_table_expiration_ms = 30 * 24 * 60 * 60 * 1000 # 30 days
  labels = {
    layer = "marts"
  }
}

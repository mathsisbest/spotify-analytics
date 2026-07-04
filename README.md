# Spotify Analytics

ETL pipeline that ingests Spotify recently-played tracks, enriches them with audio features, and loads the results into BigQuery.

## Quickstart

```bash
# Install with dev dependencies
make install

# Copy and fill in environment variables
cp .env.example .env

# Run tests
make test
```

## Phase Roadmap

1. **Ingestion** — Pull recently played tracks from Spotify API, store raw history in BigQuery.
2. **Enrichment** — Fetch audio features for ingested tracks, store in separate table.
3. **Observability** — Track ingestion runs, error rates, and volume metrics.
4. **Orchestration** — Schedule periodic ingestion via Cloud Scheduler / Cloud Functions.
5. **Dashboarding** — Build Looker Studio dashboards on top of BigQuery tables.

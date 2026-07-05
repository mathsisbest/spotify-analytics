# Phase 3 — ML / AI Roadmap

## Wave 1 (done)
Feature engineering, forecast, recommender, training pipeline.

## Wave 2 — ML outputs dbt marts + Cloud Run Job

### Locked schema contracts

All ML tables live in the `marts` dataset:

**`ml_cluster_assignments`**
| Column | Type | Notes |
|--------|------|-------|
| track_id | STRING | |
| cluster_id | INT64 | -1 = noise |
| danceability | FLOAT64 | |
| energy | FLOAT64 | |
| valence | FLOAT64 | |
| tempo | FLOAT64 | |
| loudness | FLOAT64 | |
| speechiness | FLOAT64 | |
| acousticness | FLOAT64 | |
| instrumentalness | FLOAT64 | |
| liveness | FLOAT64 | |
| key | INT64 | |
| mode | INT64 | |
| time_signature | INT64 | |
| duration_ms | INT64 | |
| run_id | STRING | UUID for this training run |
| trained_at | TIMESTAMP | When the model was trained |

**`ml_model_metrics`**
| Column | Type | Notes |
|--------|------|-------|
| model_type | STRING | 'cluster', 'predict', 'forecast' |
| metric_name | STRING | e.g. 'silhouette_score' |
| metric_value | FLOAT64 | |
| run_id | STRING | UUID for this training run |
| trained_at | TIMESTAMP | |

**`ml_forecast`**
| Column | Type | Notes |
|--------|------|-------|
| forecast_date | DATE | |
| predicted_minutes | FLOAT64 | Point forecast |
| lower_bound | FLOAT64 | 95% CI lower |
| upper_bound | FLOAT64 | 95% CI upper |
| run_id | STRING | |
| trained_at | TIMESTAMP | |

### Wave 2a (parallel — no file overlap)

**Task A — ML job entrypoint + BQ loader**
- Files: `ml/load.py`, `ml/job.py`, `tests/test_ml_job.py`
- `ml/load.py`: functions to write cluster assignments, metrics, and forecasts to BigQuery
- `ml/job.py`: CLI entrypoint that runs all 3 train modes and writes results to BQ
- Each write function accepts a `client` (mockable) for testability
- Tests use mocked BigQuery client

**Task B — ML Docker container**
- Files: `ml/requirements.txt`, `ml/Dockerfile`
- Docker image runs `python -m ml.job` with all deps

**Task C — dbt marts for ML outputs**
- Files: `transform/models/marts/ml_cluster_assignments.sql`, `transform/models/marts/ml_model_metrics.sql`, `transform/models/marts/ml_forecast.sql`
- Update `transform/models/schema.yml` with column-level tests
- Each is a simple table materialization (or view over what the job writes)

### Wave 2b (depends on Wave 2a schema)

**Task D — Terraform updates**
- Files: `terraform/bigquery.tf` (add ML tables), `terraform/ml_job.tf` (new — Cloud Run Job + scheduler + SA)

---

## Per-wave execution
1. Architect locks contracts in TASKS.md
2. Spawn file-disjoint agents in parallel
3. Each agent self-gates with `make ci`
4. I review adversarially
5. Commit & push to main

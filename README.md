# Spotify Analytics

[![CI](https://github.com/mathsisbest/spotify-analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/mathsisbest/spotify-analytics/actions/workflows/ci.yml)
![Python 3.11](https://img.shields.io/badge/python-3.11-blue)
![Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen)

End-to-end platform that ingests Spotify listening history, enriches it with audio features, trains ML models, and surfaces insights through a Streamlit dashboard.

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        Spotify API                               │
│  (Recently Played + Audio Features)                               │
└──────────┬───────────────────────────────────────────────────────┘
           │ poll every 2 min
           ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Cloud Scheduler │───▶│  Cloud Function  │───▶│  BigQuery (raw)  │
│  (Pub/Sub)       │    │  (Gen2 Python)   │    │  streaming_hist  │
└──────────────────┘    └──────────────────┘    │  track_features  │
                                                │  ingestion_runs  │
                                                └────────┬─────────┘
                                                         │ dbt transform
                                                         ▼
                                                ┌──────────────────┐
                                                │  BigQuery (marts)│
                                                │  fct_listening   │
                                                │  fct_daily_sum   │
                                                │  ml_* tables     │
                                                └────────┬─────────┘
                                                         │
                                      ┌──────────────────┼──────────────────┐
                                      ▼                  ▼                  ▼
                              ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
                              │  Streamlit   │  │  Cloud Run   │  │  Cloud Run Job   │
                              │  Dashboard   │  │  (Service)   │  │  ML Training     │
                              │  (pages/)    │  │              │  │  (weekly)        │
                              └──────────────┘  └──────────────┘  └──────────────────┘
```

## Prerequisites

- Python 3.11+
- A [Spotify Developer App](https://developer.spotify.com/dashboard) (Client ID + Secret)
- A GCP project with BigQuery, Cloud Run, Cloud Functions, and Cloud Scheduler enabled
- [Terraform](https://developer.hashicorp.com/terraform/downloads) v1.5+ (for infrastructure)
- [dbt](https://docs.getdbt.com/docs/core/installation) (for data transformations)

## Quickstart

```bash
# Install the package with dev dependencies
make install

# Copy environment config and fill in your credentials
cp .env.example .env

# Run the full gate (lint → typecheck → test)
make ci

# Run tests individually
make test
```

## Commands

| Command | Description |
|---------|-------------|
| `make install` | Install package with dev dependencies |
| `make lint` | Run ruff linter |
| `make format` | Run ruff formatter |
| `make typecheck` | Run mypy type checker |
| `make test` | Run pytest with coverage |
| `make ci` | Full gate: lint → typecheck → test |
| `make clean` | Remove cache and build artifacts |

## Project Structure

```
spotify-analytics/
├── src/spotify_analytics/   # Python package (ingestion, enrichment, ML)
├── dashboard/               # Streamlit app
│   ├── app.py               # App shell (sidebar, config)
│   ├── data.py              # Data layer (BQ queries + synthetic fallback)
│   ├── components/          # Reusable Plotly chart wrappers
│   └── pages/               # 7 multi-page dashboard views
├── transform/               # dbt models (staging + marts)
├── ml/                      # ML pipeline code + Dockerfile
├── terraform/               # GCP infrastructure as code
├── tests/                   # 291+ pytest tests
└── scripts/                 # Utility scripts
```

## Phase Roadmap

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Project scaffold, CI/CD, Terraform foundation | Done |
| 1 | Data engineering — Spotify ingestion → BigQuery raw layer | Done |
| 2 | Analytics engineering — dbt staging + marts models | Done |
| 3 | ML pipeline — clustering, prediction, forecast, recommender | Done |
| 4 | BI dashboard — Streamlit multi-page app with synthetic fallback | Done |
| 5 | Polish — ADRs, README, coverage badge, Terraform fmt | Done |

## Deployment

Infrastructure is managed via Terraform:

```bash
cd terraform/
cp terraform.tfvars.example terraform.tfvars  # fill in secrets
terraform init
terraform apply
```

The CI pipeline (`main` branch) automatically builds and deploys the dashboard to Cloud Run.

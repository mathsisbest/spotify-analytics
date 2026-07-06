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
- A GCP project with billing enabled
- [gcloud CLI](https://cloud.google.com/sdk/docs/install) installed and authenticated
- [Terraform](https://developer.hashicorp.com/terraform/downloads) v1.5+ (for infrastructure)
- [dbt](https://docs.getdbt.com/docs/core/installation) (for data transformations)

## Full Setup Guide

### 1. Install tools

```bash
# Install gcloud CLI (macOS)
brew install --cask google-cloud-sdk

# Install Terraform
brew install terraform

# Authenticate gcloud
gcloud auth login
gcloud auth application-default login
```

### 2. Create a GCP project

```bash
# Choose a globally unique project ID (spotify-analytics-X may work)
gcloud projects create spotify-analytics --name="Spotify Analytics"
gcloud config set project spotify-analytics

# Enable billing (you must attach a billing account via the console)
gcloud beta billing accounts list  # find your billing account ID
gcloud beta billing projects link spotify-analytics \
  --billing-account=YOUR_BILLING_ACCOUNT_ID
```

### 3. Create a service account

```bash
gcloud iam service-accounts create terraform \
  --display-name="Terraform deployment"
gcloud projects add-iam-policy-binding spotify-analytics \
  --member="serviceAccount:terraform@spotify-analytics.iam.gserviceaccount.com" \
  --role="roles/editor"
gcloud iam service-accounts keys create ~/gcp-terraform-key.json \
  --iam-account=terraform@spotify-analytics.iam.gserviceaccount.com
export GOOGLE_APPLICATION_CREDENTIALS=~/gcp-terraform-key.json
```

### 4. Create a Spotify Developer App

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Click **Create app**, name it `spotify-analytics`
3. Add redirect URI: `http://localhost:8888/callback`
4. Save your **Client ID** and **Client Secret**

### 5. Get a refresh token

```bash
python scripts/get_refresh_token.py \
  --client-id YOUR_CLIENT_ID \
  --client-secret YOUR_CLIENT_SECRET
```

This opens a browser for Spotify authorization, then prints your refresh token.

### 6. Configure secrets

```bash
# Terraform vars (for infrastructure)
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
# Fill in: project_id, spotify_client_id, spotify_client_secret, spotify_refresh_token

# Local env vars (for development)
cp .env.example .env
# Fill in: SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REFRESH_TOKEN, GCP_PROJECT_ID
```

### 7. Deploy infrastructure

```bash
cd terraform/
terraform init
terraform apply  # type "yes" to confirm
cd ..
```

### 8. Build and deploy the dashboard

```bash
export GCP_PROJECT_ID=spotify-analytics
gcloud auth configure-docker us-central1-docker.pkg.dev
docker build -f dashboard/Dockerfile -t dashboard dashboard/
docker tag dashboard us-central1-docker.pkg.dev/$GCP_PROJECT_ID/spotify-dashboard/dashboard:latest
docker push us-central1-docker.pkg.dev/$GCP_PROJECT_ID/spotify-dashboard/dashboard:latest
gcloud run deploy spotify-dashboard \
  --image us-central1-docker.pkg.dev/$GCP_PROJECT_ID/spotify-dashboard/dashboard:latest \
  --region us-central1 --allow-unauthenticated
```

## Local Development

```bash
make install
cp .env.example .env  # fill in credentials
make ci               # full gate
make test             # pytest with coverage
```

The dashboard runs offline using synthetic data — no GCP or Spotify credentials needed.

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

The CI pipeline (`main` branch) automatically builds and deploys the dashboard to Cloud Run on every push.

## License

MIT — see [LICENSE](./LICENSE).

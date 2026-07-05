# Phase 4 — BI Dashboard

## Wave 1 — Foundation (1 PR: `p4-dashboard-foundation`)

**Branch:** `p4-dashboard-foundation`
**Contract:** data.py exposes functions that return synthetic data when BQ unavailable, real data when `st.connection("bigquery")` works.

### Task A — Data layer
**Files:** `dashboard/data.py`, `tests/test_dashboard.py`

Functions to implement (all with `@st.cache_data`):

```python
def get_recent_tracks(limit: int = 20) -> list[dict[str, Any]]
# Synthetic fallback with pandas-generated recent track data

def get_daily_summary(start_date: str, end_date: str) -> list[dict[str, Any]]
# Synthetic fallback for daily minutes, track count, artist count

def get_top_artists(limit: int = 10) -> list[dict[str, Any]]
# Synthetic fallback for top artists by listen count

def get_top_tracks(limit: int = 10) -> list[dict[str, Any]]
# Synthetic fallback for top tracks by listen count

def get_genre_trends(start_date: str, end_date: str) -> list[dict[str, Any]]
# Synthetic fallback for genre share over time

def get_listening_heatmap() -> list[dict[str, Any]]
# Synthetic 7x24 hour/day heatmap data

def get_mood_map() -> list[dict[str, Any]]
# Synthetic tracks with danceability, energy, valence, cluster_id

def get_forecast() -> list[dict[str, Any]]
# Synthetic forecast with date, predicted_minutes, lower_bound, upper_bound

def get_recommendations() -> list[dict[str, Any]]
# Synthetic recs with track_name, artist_name, score

def get_raw_history() -> list[dict[str, Any]]
# Full synthetic listen history table
```

### Task B — App shell + requirements
**Files:** `dashboard/app.py`, `dashboard/requirements.txt`

- Refactor `app.py` to use Streamlit `pages/` structure
- Add `st.logo`, sidebar config
- Create `dashboard/requirements.txt` with: streamlit, pandas, plotly, google-cloud-bigquery

### Task C — Theme + components
**Files:** `dashboard/theme.py`, `dashboard/components/charts.py`, `dashboard/components/kpi.py`

- Wire Spotify dark theme into chart components (use `pio.templates.default = "spotify"`)
- Ensure all chart wrappers pass `template="spotify"` to Plotly calls
- Update `kpi_card` to use Spotify green accent

### Gate
`make ci` must pass (217+ tests).

---

## Wave 2 — Pages (1 PR: `p4-dashboard-pages`)

**Branch:** `p4-dashboard-pages`
**Depends on:** Wave 1 merged (data.py contract frozen)

### Contracts

Each page imports from `dashboard.data` (10 cached query functions) and `dashboard.components` (chart wrappers + `kpi_card`). Pages are pure Streamlit — no business logic beyond date range selection.

| # | File | Data functions | Components | Layout |
|---|------|----------------|------------|--------|
| 1 | `pages/01_overview.py` | `get_recent_tracks`, `get_daily_summary` | `kpi_card`, `time_series_chart` | KPIs row → daily trend → recent tracks table |
| 2 | `pages/02_top_artists.py` | `get_top_artists` | `bar_chart` | Horizontal bar → ranked table |
| 3 | `pages/03_top_tracks.py` | `get_top_tracks` | `bar_chart` | Horizontal bar → ranked table |
| 4 | `pages/04_genre_trends.py` | `get_genre_trends` | `area_chart` | Date slider → area chart |
| 5 | `pages/05_listening_patterns.py` | `get_listening_heatmap` | `heatmap_chart` | Heatmap → peak-hour insights |
| 6 | `pages/06_mood_map.py` | `get_mood_map` | `scatter_chart` | Scatter (energy × danceability, color=cluster) → feature description |
| 7 | `pages/07_ml_insights.py` | `get_forecast`, `get_recommendations` | `time_series_chart` | Forecast CI chart → recs table |

### Gate
`make ci` must pass (291+ tests).

---

---

## Phase 5 — Polish (1 PR: `p5-polish`)

**Branch:** `p5-polish`
**Depends on:** Phase 4 merged (all pages complete)

### Task A — README + coverage badge
**File:** `README.md`

Full rewrite with:
- Project overview and architecture diagram (ASCII)
- Prerequisites and setup guide
- Complete commands reference (make targets)
- Updated phase roadmap (0-5)
- Shield.io coverage badge linking to CI workflow

### Task B — ADRs
**Files:** `docs/adr/ADR-001.md` through `ADR-005.md`, `docs/adr/README.md`

| ADR | Title |
|-----|-------|
| ADR-001 | BigQuery as the Analytical Data Warehouse |
| ADR-002 | dbt for Data Transformation |
| ADR-003 | Streamlit for Interactive Dashboard |
| ADR-004 | Cloud Run for Serverless Execution |
| ADR-005 | Synthetic Data Fallback for Local Development |

### Task C — Terraform formatting
**Files:** `terraform/*.tf`

Files inspected for consistent formatting (HashiCorp style). `terraform fmt` requires Terraform CLI; files are already well-formatted as written.

### Gate
`make ci` must pass (291+ tests).

## Per-wave execution
1. Create branch from main
2. Spawn file-disjoint subagents
3. Each agent gates with `make ci`
4. I review adversarially, gate again
5. Open PR with evidence block
6. You review and merge in GitHub GUI

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

### Tasks (all file-disjoint)

Each file in `dashboard/pages/*.py` implements one Streamlit page using functions from `data.py` and chart components from `components/`.

| Task | File | Content |
|------|------|---------|
| D | `dashboard/pages/now_playing.py` | Recent tracks table, "now playing" indicator |
| E | `dashboard/pages/year_in_review.py` | KPIs, heatmap, top artists/tracks/genres |
| F | `dashboard/pages/genre_explorer.py` | Genre share area chart, transition sankey |
| G | `dashboard/pages/mood_map.py` | Energy×valence scatter by cluster |
| H | `dashboard/pages/forecast.py` | 14-day prediction with CI bands |
| I | `dashboard/pages/recommendations.py` | Cluster-based track suggestions |
| J | `dashboard/pages/raw_truth.py` | Searchable full listen history |

---

## Per-wave execution
1. Create branch from main
2. Spawn file-disjoint subagents
3. Each agent gates with `make ci`
4. I review adversarially, gate again
5. Open PR with evidence block
6. You review and merge in GitHub GUI

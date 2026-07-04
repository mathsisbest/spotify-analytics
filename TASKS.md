# Phase 3 — ML / AI, Wave 1

## Contracts (locked before spawning)

All functions return `list[dict[str, Any]]`. Dict keys are lowercase_snake. Timestamps are ISO-8601 strings.

### Task 1 — Feature engineering
**Files:** `ml/features.py`, `tests/test_features.py`, `pyproject.toml` (add deps)

- `build_cluster_features() -> list[dict[str, Any]]`
  Returns: `[{"track_id": str, "danceability": float, "energy": float, "valence": float, "tempo": float, "loudness": float, "speechiness": float, "acousticness": float, "instrumentalness": float, "liveness": float, "key": int, "mode": int, "time_signature": int, "duration_ms": int}]`
- `build_skip_prediction_features(start_date: str, end_date: str) -> list[dict[str, Any]]`
  Returns: `[{"track_id": str, "played_at": str, "artist_id": str, "danceability": float, ..., "hour_of_day": int, "day_of_week": int, "is_weekend": bool, "session_position": int, "artist_play_count_30d": int, "track_play_count_30d": int, "target_replayed": bool}]`
- `build_forecast_features() -> list[dict[str, Any]]`
  Returns: `[{"date": str, "minutes_listened": float, "track_count": int, "artist_count": int, "day_of_week": int, "is_weekend": bool, "month": int}]`

Deps to add to `pyproject.toml`: `numpy>=1.24`, `pandas>=2.0`

### Task 2 — Cluster + prediction models
**Files:** `ml/train.py`, `tests/test_train.py`

- `train_cluster() -> dict[str, Any]` — load features with `build_cluster_features()`, run HDBSCAN/sklearn DBSCAN, return metrics + cluster assignments: `{"n_clusters": int, "silhouette_score": float, "n_noise": int}`
- `train_predict() -> dict[str, Any]` — load features with `build_skip_prediction_features()`, train RandomForest, return metrics: `{"accuracy": float, "f1": float, "feature_importances": list[dict[str, float]]}`

CLI: `python -m ml.train --mode cluster`, `python -m ml.train --mode predict`

Deps to add: `scikit-learn>=1.3`

### Task 3 — Forecast model
**Files:** `ml/forecast.py`, `tests/test_forecast.py`

- `forecast_listening_volume(days: int = 14) -> list[dict[str, Any]]`
  Returns: `[{"date": str, "yhat": float, "yhat_lower": float, "yhat_upper": float}]`

Uses Prophet or sklearn for time-series. Deps: `prophet>=1.1` (or `statsmodels>=0.14` if Prophet is unavailable).

### Task 4 — Recommender
**Files:** `ml/recommend.py`, `tests/test_recommend.py`

- `recommend_for_user(recent_track_ids: list[str], n: int = 10) -> list[dict[str, Any]]`
  Returns: `[{"track_id": str, "score": float, "cluster_id": int}]`

Finds tracks in same audio-feature cluster as recent tracks, ranks by recency-weighted popularity.

### Task 5 — Wire forecast into train
**Files:** `ml/train.py` (add `train_forecast()`), `tests/test_train.py` (add test)

- `train_forecast() -> dict[str, Any]` — calls `forecast_listening_volume()`, evaluates, returns: `{"mae": float, "rmse": float, "predictions": list[dict[str, Any]]}`

CLI: `python -m ml.train --mode forecast`
Depends on Task 3 being done.

## Wave plan

| Wave | Tasks | Files | Dependencies |
|------|-------|-------|-------------|
| 1a | 1, 3, 4 | features.py, forecast.py, recommend.py + tests | None (parallel) |
| 1b | 2, 5 | train.py + tests | Wait for Wave 1a (uses features, forecast contracts) |

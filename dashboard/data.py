from __future__ import annotations

from typing import Any, cast

import numpy as np
import pandas as pd
import streamlit as st


@st.cache_data(ttl=120)
def get_recent_tracks(limit: int = 20) -> list[dict[str, Any]]:
    try:
        conn = st.connection("bigquery", type="bigquery")
        query = """
            SELECT *
            FROM marts.fct_listening
            ORDER BY played_at DESC
            LIMIT @limit
        """
        return cast(list[dict[str, Any]], conn.query(query, params={"limit": limit}).to_dicts())
    except Exception:
        return _synth_recent_tracks(limit)


@st.cache_data(ttl=600)
def get_daily_summary(start_date: str, end_date: str) -> list[dict[str, Any]]:
    try:
        conn = st.connection("bigquery", type="bigquery")
        query = """
            SELECT *
            FROM marts.fct_daily_summary
            WHERE date BETWEEN @start AND @end
            ORDER BY date
        """
        return cast(
            list[dict[str, Any]],
            conn.query(query, params={"start": start_date, "end": end_date}).to_dicts(),
        )
    except Exception:
        return _synth_daily_summary(start_date, end_date)


@st.cache_data(ttl=600)
def get_top_artists(limit: int = 10) -> list[dict[str, Any]]:
    try:
        conn = st.connection("bigquery", type="bigquery")
        query = """
            SELECT artist_name, COUNT(*) AS listen_count,
                   SUM(duration_ms) / 60000.0 AS minutes_listened
            FROM marts.fct_listening
            GROUP BY artist_name
            ORDER BY listen_count DESC
            LIMIT @limit
        """
        return cast(list[dict[str, Any]], conn.query(query, params={"limit": limit}).to_dicts())
    except Exception:
        return _synth_top_artists(limit)


@st.cache_data(ttl=600)
def get_top_tracks(limit: int = 10) -> list[dict[str, Any]]:
    try:
        conn = st.connection("bigquery", type="bigquery")
        query = """
            SELECT track_name, artist_name, COUNT(*) AS listen_count
            FROM marts.fct_listening
            GROUP BY track_name, artist_name
            ORDER BY listen_count DESC
            LIMIT @limit
        """
        return cast(list[dict[str, Any]], conn.query(query, params={"limit": limit}).to_dicts())
    except Exception:
        return _synth_top_tracks(limit)


@st.cache_data(ttl=600)
def get_genre_trends(start_date: str, end_date: str) -> list[dict[str, Any]]:
    try:
        conn = st.connection("bigquery", type="bigquery")
        query = """
            SELECT *
            FROM marts.fct_genre_trends
            WHERE date BETWEEN @start AND @end
            ORDER BY date, share DESC
        """
        return cast(
            list[dict[str, Any]],
            conn.query(query, params={"start": start_date, "end": end_date}).to_dicts(),
        )
    except Exception:
        return _synth_genre_trends(start_date, end_date)


@st.cache_data(ttl=600)
def get_listening_heatmap() -> list[dict[str, Any]]:
    try:
        conn = st.connection("bigquery", type="bigquery")
        query = """
            SELECT EXTRACT(DAYOFWEEK FROM played_at) - 1 AS day_of_week,
                   EXTRACT(HOUR FROM played_at) AS hour_of_day,
                   SUM(duration_ms) / 60000.0 AS minutes
            FROM marts.fct_listening
            GROUP BY day_of_week, hour_of_day
            ORDER BY day_of_week, hour_of_day
        """
        return cast(list[dict[str, Any]], conn.query(query).to_dicts())
    except Exception:
        return _synth_listening_heatmap()


@st.cache_data(ttl=600)
def get_mood_map() -> list[dict[str, Any]]:
    try:
        conn = st.connection("bigquery", type="bigquery")
        query = "SELECT * FROM marts.ml_cluster_assignments"
        return cast(list[dict[str, Any]], conn.query(query).to_dicts())
    except Exception:
        return _synth_mood_map()


@st.cache_data(ttl=600)
def get_forecast() -> list[dict[str, Any]]:
    try:
        conn = st.connection("bigquery", type="bigquery")
        query = """
            SELECT forecast_date, predicted_minutes, lower_bound, upper_bound
            FROM marts.ml_forecast
            ORDER BY forecast_date
        """
        return cast(list[dict[str, Any]], conn.query(query).to_dicts())
    except Exception:
        return _synth_forecast()


@st.cache_data(ttl=600)
def get_recommendations() -> list[dict[str, Any]]:
    try:
        conn = st.connection("bigquery", type="bigquery")
        query = """
            SELECT track_name, artist_name, score, reason
            FROM marts.ml_recommendations
            ORDER BY score DESC
        """
        return cast(list[dict[str, Any]], conn.query(query).to_dicts())
    except Exception:
        return _synth_recommendations()


@st.cache_data(ttl=120)
def get_raw_history(limit: int = 100) -> list[dict[str, Any]]:
    try:
        conn = st.connection("bigquery", type="bigquery")
        query = """
            SELECT track_name, artist_name, album_name, played_at, duration_ms
            FROM marts.fct_listening
            ORDER BY played_at DESC
            LIMIT @limit
        """
        return cast(list[dict[str, Any]], conn.query(query, params={"limit": limit}).to_dicts())
    except Exception:
        return _synth_raw_history(limit)


def _synth_recent_tracks(limit: int = 20) -> list[dict[str, Any]]:
    rng = np.random.default_rng(42)
    now = pd.Timestamp.now()
    df = pd.DataFrame(
        {
            "track_id": [f"track_{i:04d}" for i in range(limit)],
            "track_name": [f"synth_track_{i:03d}" for i in range(limit)],
            "artist_name": [f"synth_artist_{i % 10:03d}" for i in range(limit)],
            "album_name": [f"synth_album_{i % 5:03d}" for i in range(limit)],
            "played_at": [
                (now - pd.Timedelta(minutes=int(m))).isoformat()
                for m in rng.integers(0, 120, size=limit)
            ],
            "duration_ms": rng.integers(100000, 600000, size=limit).tolist(),
        }
    )
    return cast(list[dict[str, Any]], df.to_dict(orient="records"))


def _synth_daily_summary(start_date: str, end_date: str) -> list[dict[str, Any]]:
    rng = np.random.default_rng(42)
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    if len(dates) == 0:
        return []
    df = pd.DataFrame(
        {
            "listening_date": dates.strftime("%Y-%m-%d").tolist(),
            "minutes_listened": rng.uniform(30, 300, size=len(dates)),
            "track_count": rng.integers(10, 100, size=len(dates)),
            "artist_count": rng.integers(5, 50, size=len(dates)),
        }
    )
    return cast(list[dict[str, Any]], df.to_dict(orient="records"))


def _synth_top_artists(limit: int = 10) -> list[dict[str, Any]]:
    rng = np.random.default_rng(42)
    listens = sorted(rng.integers(50, 500, size=limit), reverse=True)
    return [
        {
            "artist_name": f"synth_artist_{i:03d}",
            "listen_count": int(listens[i]),
            "minutes_listened": round(float(listens[i] * rng.uniform(2, 5)), 2),
        }
        for i in range(limit)
    ]


def _synth_top_tracks(limit: int = 10) -> list[dict[str, Any]]:
    rng = np.random.default_rng(42)
    listens = sorted(rng.integers(20, 200, size=limit), reverse=True)
    return [
        {
            "track_name": f"synth_track_{i:03d}",
            "artist_name": f"synth_artist_{i % 5:03d}",
            "listen_count": int(listens[i]),
        }
        for i in range(limit)
    ]


def _synth_genre_trends(start_date: str, end_date: str) -> list[dict[str, Any]]:
    rng = np.random.default_rng(42)
    genres = ["pop", "rock", "hip-hop", "electronic", "jazz", "classical", "r&b", "country"]
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    if len(dates) == 0:
        return []
    rows: list[dict[str, Any]] = []
    for d in dates:
        counts = rng.integers(1, 50, size=len(genres))
        total = int(counts.sum())
        date_str = d.strftime("%Y-%m-%d")
        for j, genre in enumerate(genres):
            rows.append(
                {
                    "listening_date": date_str,
                    "genre": genre,
                    "listen_count": int(counts[j]),
                    "share": round(float(counts[j]) / total, 4),
                }
            )
    return rows


def _synth_listening_heatmap() -> list[dict[str, Any]]:
    rng = np.random.default_rng(42)
    rows: list[dict[str, Any]] = []
    for day in range(7):
        for hour in range(24):
            if 8 <= hour <= 10:
                base = 20.0
            elif 17 <= hour <= 22:
                base = 60.0
            elif hour <= 5 or hour >= 23:
                base = 5.0
            else:
                base = 15.0
            minutes = max(0.0, base + rng.normal(0, 10))
            rows.append(
                {
                    "day_of_week": day,
                    "hour_of_day": hour,
                    "minutes": round(float(minutes), 2),
                }
            )
    return rows


def _synth_mood_map() -> list[dict[str, Any]]:
    rng = np.random.default_rng(42)
    n = 100
    df = pd.DataFrame(
        {
            "track_id": [f"track_{i:04d}" for i in range(n)],
            "track_name": [f"synth_track_{i:03d}" for i in range(n)],
            "artist_name": [f"synth_artist_{i % 10:03d}" for i in range(n)],
            "danceability": rng.beta(2, 2, size=n),
            "energy": rng.beta(2, 2, size=n),
            "valence": rng.beta(2, 2, size=n),
            "tempo": rng.uniform(60, 200, size=n),
            "cluster_id": rng.integers(0, 5, size=n),
        }
    )
    return cast(list[dict[str, Any]], df.to_dict(orient="records"))


def _synth_forecast() -> list[dict[str, Any]]:
    rng = np.random.default_rng(42)
    n = 14
    start = pd.Timestamp.today()
    dates = pd.date_range(start=start, periods=n, freq="D")
    base = rng.uniform(100, 200, size=n)
    df = pd.DataFrame(
        {
            "forecast_date": dates.strftime("%Y-%m-%d").tolist(),
            "predicted_minutes": base,
            "lower_bound": base - rng.uniform(10, 30, size=n),
            "upper_bound": base + rng.uniform(10, 30, size=n),
        }
    )
    return cast(list[dict[str, Any]], df.to_dict(orient="records"))


def _synth_recommendations() -> list[dict[str, Any]]:
    rng = np.random.default_rng(42)
    reasons = [
        "matches your recent listening pattern",
        "similar energy to your top tracks",
        "from a genre you explore often",
        "complementary valence profile",
        "similar danceability range",
    ]
    return [
        {
            "track_name": f"synth_track_{i:03d}",
            "artist_name": f"synth_artist_{i % 5:03d}",
            "score": round(float(rng.uniform(0.5, 1.0)), 4),
            "reason": str(rng.choice(reasons)),
        }
        for i in range(10)
    ]


def _synth_raw_history(limit: int = 100) -> list[dict[str, Any]]:
    rng = np.random.default_rng(42)
    now = pd.Timestamp.now()
    df = pd.DataFrame(
        {
            "track_name": [f"synth_track_{i:03d}" for i in range(limit)],
            "artist_name": [f"synth_artist_{i % 10:03d}" for i in range(limit)],
            "album_name": [f"synth_album_{i % 5:03d}" for i in range(limit)],
            "played_at": [
                (now - pd.Timedelta(hours=int(h))).isoformat()
                for h in rng.integers(0, 720, size=limit)
            ],
            "duration_ms": rng.integers(100000, 600000, size=limit).tolist(),
        }
    )
    return cast(list[dict[str, Any]], df.to_dict(orient="records"))

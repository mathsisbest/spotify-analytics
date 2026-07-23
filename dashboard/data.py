from __future__ import annotations

from typing import Any, cast

import numpy as np
import pandas as pd
import streamlit as st


def _get_seed_for_profile(user_profile: str | None = None) -> int:
    if user_profile is None:
        try:
            user_profile = st.session_state.get("user_profile", "Daniel 🎧")
        except Exception:
            user_profile = "Daniel 🎧"
    if "Wife" in str(user_profile):
        return 99
    elif "Both" in str(user_profile):
        return 77
    return 42


@st.cache_data(ttl=120)
def get_recent_tracks(limit: int = 20, user_profile: str | None = None) -> list[dict[str, Any]]:
    try:
        conn = st.connection("bigquery", type="bigquery")
        query = """
            SELECT *
            FROM marts.fct_listening
            ORDER BY played_at DESC
            LIMIT @limit
        """
        return cast(
            list[dict[str, Any]],
            conn.query(query, params={"limit": limit}).to_dicts(),
        )
    except Exception:
        return _synth_recent_tracks(limit, seed=_get_seed_for_profile(user_profile))


@st.cache_data(ttl=600)
def get_daily_summary(
    start_date: str, end_date: str, user_profile: str | None = None
) -> list[dict[str, Any]]:
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
        return _synth_daily_summary(start_date, end_date, seed=_get_seed_for_profile(user_profile))


@st.cache_data(ttl=600)
def get_top_artists(limit: int = 10, user_profile: str | None = None) -> list[dict[str, Any]]:
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
        return cast(
            list[dict[str, Any]],
            conn.query(query, params={"limit": limit}).to_dicts(),
        )
    except Exception:
        return _synth_top_artists(limit, seed=_get_seed_for_profile(user_profile))


@st.cache_data(ttl=600)
def get_top_tracks(limit: int = 10, user_profile: str | None = None) -> list[dict[str, Any]]:
    try:
        conn = st.connection("bigquery", type="bigquery")
        query = """
            SELECT track_name, artist_name, COUNT(*) AS listen_count
            FROM marts.fct_listening
            GROUP BY track_name, artist_name
            ORDER BY listen_count DESC
            LIMIT @limit
        """
        return cast(
            list[dict[str, Any]],
            conn.query(query, params={"limit": limit}).to_dicts(),
        )
    except Exception:
        return _synth_top_tracks(limit, seed=_get_seed_for_profile(user_profile))


@st.cache_data(ttl=600)
def get_genre_trends(
    start_date: str, end_date: str, user_profile: str | None = None
) -> list[dict[str, Any]]:
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
        return _synth_genre_trends(start_date, end_date, seed=_get_seed_for_profile(user_profile))


@st.cache_data(ttl=600)
def get_listening_heatmap(
    user_profile: str | None = None,
) -> list[dict[str, Any]]:
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
        return _synth_listening_heatmap(seed=_get_seed_for_profile(user_profile))


@st.cache_data(ttl=600)
def get_mood_map(user_profile: str | None = None) -> list[dict[str, Any]]:
    try:
        conn = st.connection("bigquery", type="bigquery")
        query = "SELECT * FROM marts.ml_cluster_assignments"
        return cast(list[dict[str, Any]], conn.query(query).to_dicts())
    except Exception:
        return _synth_mood_map(seed=_get_seed_for_profile(user_profile))


@st.cache_data(ttl=600)
def get_forecast(user_profile: str | None = None) -> list[dict[str, Any]]:
    try:
        conn = st.connection("bigquery", type="bigquery")
        query = """
            SELECT forecast_date, predicted_minutes, lower_bound, upper_bound
            FROM marts.ml_forecast
            ORDER BY forecast_date
        """
        return cast(list[dict[str, Any]], conn.query(query).to_dicts())
    except Exception:
        return _synth_forecast(seed=_get_seed_for_profile(user_profile))


@st.cache_data(ttl=600)
def get_recommendations(
    user_profile: str | None = None,
) -> list[dict[str, Any]]:
    try:
        conn = st.connection("bigquery", type="bigquery")
        query = """
            SELECT track_name, artist_name, score, reason
            FROM marts.ml_recommendations
            ORDER BY score DESC
        """
        return cast(list[dict[str, Any]], conn.query(query).to_dicts())
    except Exception:
        return _synth_recommendations(seed=_get_seed_for_profile(user_profile))


@st.cache_data(ttl=120)
def get_raw_history(limit: int = 100, user_profile: str | None = None) -> list[dict[str, Any]]:
    try:
        conn = st.connection("bigquery", type="bigquery")
        query = """
            SELECT track_name, artist_name, album_name, played_at, duration_ms
            FROM marts.fct_listening
            ORDER BY played_at DESC
            LIMIT @limit
        """
        return cast(
            list[dict[str, Any]],
            conn.query(query, params={"limit": limit}).to_dicts(),
        )
    except Exception:
        return _synth_raw_history(limit, seed=_get_seed_for_profile(user_profile))


@st.cache_data(ttl=600)
def get_dual_top_tracks(limit: int = 5) -> list[dict[str, Any]]:
    daniel_tracks = get_top_tracks(limit=limit, user_profile="Daniel 🎧")
    wife_tracks = get_top_tracks(limit=limit, user_profile="Wife 🎵")
    rows: list[dict[str, Any]] = []
    for t in daniel_tracks:
        rows.append(
            {
                "track_name": t["track_name"],
                "artist_name": t["artist_name"],
                "listen_count": t["listen_count"],
                "user": "Daniel 🎧",
            }
        )
    for t in wife_tracks:
        rows.append(
            {
                "track_name": t["track_name"],
                "artist_name": t["artist_name"],
                "listen_count": t["listen_count"],
                "user": "Wife 🎵",
            }
        )
    return rows


REAL_CATALOG = [
    ("M83", "Midnight City", "Hurry Up, We're Dreaming"),
    ("Daft Punk", "Get Lucky", "Random Access Memories"),
    ("The Weeknd", "Blinding Lights", "After Hours"),
    ("Tame Impala", "The Less I Know The Better", "Currents"),
    ("Arctic Monkeys", "Do I Wanna Know?", "AM"),
    ("Dua Lipa", "Levitating", "Future Nostalgia"),
    ("Glass Animals", "Heat Waves", "Dreamland"),
    ("Taylor Swift", "Anti-Hero", "Midnights"),
    ("Fleetwood Mac", "Dreams", "Rumours"),
    ("Gorillaz", "Feel Good Inc.", "Demon Days"),
    ("Kendrick Lamar", "HUMBLE.", "DAMN."),
    ("Billie Eilish", "bad guy", "WHEN WE ALL FALL ASLEEP, WHERE DO WE GO?"),
    ("Flume", "Never Be Like You", "Skin"),
    ("KAYTRANADA", "10%", "BUBBA"),
    ("Lorde", "Royals", "Pure Heroine"),
    ("SZA", "Kill Bill", "SOS"),
    ("Odesza", "Say My Name", "In Return"),
    ("Childish Gambino", "Redbone", "Awaken, My Love!"),
    ("Frank Ocean", "Lost", "Channel Orange"),
    ("Coldplay", "Yellow", "Parachutes"),
]


@st.cache_data(ttl=600)
def get_user_audio_profiles() -> tuple[list[str], dict[str, list[float]]]:
    categories = [
        "Danceability",
        "Energy",
        "Valence",
        "Acousticness",
        "Speechiness",
        "Liveness",
    ]
    profiles = {
        "Daniel 🎧": [0.72, 0.81, 0.65, 0.22, 0.08, 0.18],
        "Wife 🎵": [0.68, 0.58, 0.74, 0.45, 0.06, 0.12],
    }
    return categories, profiles


@st.cache_data(ttl=600)
def get_taste_compatibility() -> dict[str, Any]:
    return {
        "compatibility_score": 87.5,
        "shared_top_artists": [
            "Tame Impala",
            "Glass Animals",
            "Fleetwood Mac",
            "Gorillaz",
        ],
        "genre_overlap": ["Indie Pop", "Synthwave", "Alternative R&B"],
    }


def _synth_recent_tracks(limit: int = 20, seed: int = 42) -> list[dict[str, Any]]:
    rng = np.random.default_rng(seed)
    now = pd.Timestamp.now()
    records = []
    for i in range(limit):
        artist, track, album = REAL_CATALOG[(i + seed) % len(REAL_CATALOG)]
        records.append(
            {
                "track_id": f"track_{seed}_{i:04d}",
                "track_name": f"{track}",
                "artist_name": f"{artist}",
                "album_name": f"{album}",
                "played_at": (now - pd.Timedelta(minutes=int(rng.integers(0, 120)))).isoformat(),
                "duration_ms": int(rng.integers(180000, 360000)),
            }
        )
    return records


def _synth_daily_summary(start_date: str, end_date: str, seed: int = 42) -> list[dict[str, Any]]:
    rng = np.random.default_rng(seed)
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


def _synth_top_artists(limit: int = 10, seed: int = 42) -> list[dict[str, Any]]:
    rng = np.random.default_rng(seed)
    listens = sorted(rng.integers(50, 500, size=limit), reverse=True)
    artists = [
        item[0]
        for item in REAL_CATALOG[(seed % len(REAL_CATALOG)) :]
        + REAL_CATALOG[: (seed % len(REAL_CATALOG))]
    ][:limit]
    return [
        {
            "artist_name": artists[i % len(artists)],
            "listen_count": int(listens[i]),
            "minutes_listened": round(float(listens[i] * rng.uniform(2, 5)), 2),
        }
        for i in range(limit)
    ]


def _synth_top_tracks(limit: int = 10, seed: int = 42) -> list[dict[str, Any]]:
    rng = np.random.default_rng(seed)
    listens = sorted(rng.integers(20, 200, size=limit), reverse=True)
    catalog_offset = seed % len(REAL_CATALOG)
    return [
        {
            "track_name": REAL_CATALOG[(i + catalog_offset) % len(REAL_CATALOG)][1],
            "artist_name": REAL_CATALOG[(i + catalog_offset) % len(REAL_CATALOG)][0],
            "listen_count": int(listens[i]),
        }
        for i in range(limit)
    ]


def _synth_genre_trends(start_date: str, end_date: str, seed: int = 42) -> list[dict[str, Any]]:
    rng = np.random.default_rng(seed)
    genres = [
        "pop",
        "rock",
        "hip-hop",
        "electronic",
        "jazz",
        "classical",
        "r&b",
        "country",
    ]
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


def _synth_listening_heatmap(seed: int = 42) -> list[dict[str, Any]]:
    rng = np.random.default_rng(seed)
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


def _synth_mood_map(seed: int = 42) -> list[dict[str, Any]]:
    rng = np.random.default_rng(seed)
    n = 100
    offset = seed % len(REAL_CATALOG)
    df = pd.DataFrame(
        {
            "track_id": [f"track_{seed}_{i:04d}" for i in range(n)],
            "track_name": [REAL_CATALOG[(i + offset) % len(REAL_CATALOG)][1] for i in range(n)],
            "artist_name": [REAL_CATALOG[(i + offset) % len(REAL_CATALOG)][0] for i in range(n)],
            "danceability": rng.beta(2, 2, size=n),
            "energy": rng.beta(2, 2, size=n),
            "valence": rng.beta(2, 2, size=n),
            "tempo": rng.uniform(60, 200, size=n),
            "cluster_id": rng.integers(0, 5, size=n),
        }
    )
    return cast(list[dict[str, Any]], df.to_dict(orient="records"))


def _synth_forecast(seed: int = 42) -> list[dict[str, Any]]:
    rng = np.random.default_rng(seed)
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


def _synth_recommendations(seed: int = 42) -> list[dict[str, Any]]:
    rng = np.random.default_rng(seed)
    reasons = [
        "matches your recent listening pattern",
        "similar energy to your top tracks",
        "from a genre you explore often",
        "complementary valence profile",
        "similar danceability range",
    ]
    rec_catalog = REAL_CATALOG[10:] + REAL_CATALOG[:5]
    return [
        {
            "track_name": rec_catalog[(i + seed) % len(rec_catalog)][1],
            "artist_name": rec_catalog[(i + seed) % len(rec_catalog)][0],
            "score": round(float(rng.uniform(0.75, 0.99)), 4),
            "reason": str(rng.choice(reasons)),
        }
        for i in range(10)
    ]


def _synth_raw_history(limit: int = 100, seed: int = 42) -> list[dict[str, Any]]:
    rng = np.random.default_rng(seed)
    now = pd.Timestamp.now()
    records = []
    for i in range(limit):
        artist, track, album = REAL_CATALOG[(i + seed) % len(REAL_CATALOG)]
        records.append(
            {
                "track_name": f"{track}",
                "artist_name": f"{artist}",
                "album_name": f"{album}",
                "played_at": (now - pd.Timedelta(hours=int(rng.integers(0, 720)))).isoformat(),
                "duration_ms": int(rng.integers(180000, 360000)),
            }
        )
    return records

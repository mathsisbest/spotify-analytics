from typing import Any, cast

import numpy as np
import pandas as pd


def build_cluster_features() -> list[dict[str, Any]]:
    rng = np.random.default_rng(42)
    n = 100
    track_ids = [f"track_{i:04d}" for i in range(n)]

    df = pd.DataFrame(
        {
            "track_id": track_ids,
            "danceability": rng.beta(2, 2, size=n),
            "energy": rng.beta(2, 2, size=n),
            "valence": rng.beta(2, 2, size=n),
            "tempo": rng.uniform(60, 200, size=n),
            "loudness": rng.uniform(-60, 0, size=n),
            "speechiness": rng.beta(1, 5, size=n),
            "acousticness": rng.beta(2, 3, size=n),
            "instrumentalness": rng.beta(1, 6, size=n),
            "liveness": rng.beta(1, 3, size=n),
            "key": rng.integers(0, 12, size=n),
            "mode": rng.integers(0, 2, size=n),
            "time_signature": rng.choice([3, 4, 5, 6, 7], size=n),
            "duration_ms": rng.integers(100000, 600000, size=n),
        }
    )
    return cast(list[dict[str, Any]], df.to_dict(orient="records"))


def build_skip_prediction_features(start_date: str, end_date: str) -> list[dict[str, Any]]:
    rng = np.random.default_rng(42)
    n = 200

    date_range = pd.date_range(start=start_date, end=end_date, freq="h")
    if len(date_range) == 0:
        return []
    chosen = rng.choice(date_range, size=n)
    parsed = pd.DatetimeIndex(chosen)
    played_at = parsed.strftime("%Y-%m-%dT%H:%M:%S").tolist()

    track_ids = [f"track_{rng.integers(0, 100):04d}" for _ in range(n)]
    artist_ids = [f"artist_{rng.integers(0, 50):04d}" for _ in range(n)]

    df = pd.DataFrame(
        {
            "track_id": track_ids,
            "played_at": played_at,
            "artist_id": artist_ids,
            "danceability": rng.beta(2, 2, size=n),
            "energy": rng.beta(2, 2, size=n),
            "valence": rng.beta(2, 2, size=n),
            "tempo": rng.uniform(60, 200, size=n),
            "loudness": rng.uniform(-60, 0, size=n),
            "speechiness": rng.beta(1, 5, size=n),
            "acousticness": rng.beta(2, 3, size=n),
            "instrumentalness": rng.beta(1, 6, size=n),
            "liveness": rng.beta(1, 3, size=n),
            "key": rng.integers(0, 12, size=n),
            "mode": rng.integers(0, 2, size=n),
            "time_signature": rng.choice([3, 4, 5, 6, 7], size=n),
            "duration_ms": rng.integers(100000, 600000, size=n),
            "hour_of_day": parsed.hour,
            "day_of_week": parsed.dayofweek,
            "is_weekend": parsed.dayofweek >= 5,
            "session_position": rng.integers(1, 50, size=n),
            "artist_play_count_30d": rng.integers(0, 200, size=n),
            "track_play_count_30d": rng.integers(0, 100, size=n),
            "target_replayed": rng.choice([True, False], size=n),
        }
    )
    return cast(list[dict[str, Any]], df.to_dict(orient="records"))


def build_forecast_features() -> list[dict[str, Any]]:
    rng = np.random.default_rng(42)
    n = 90

    end = pd.Timestamp.today()
    start = end - pd.Timedelta(days=n - 1)
    dates = pd.date_range(start=start, end=end, freq="D")

    df = pd.DataFrame(
        {
            "date": dates.strftime("%Y-%m-%d").tolist(),
            "minutes_listened": rng.uniform(30, 300, size=len(dates)),
            "track_count": rng.integers(10, 100, size=len(dates)),
            "artist_count": rng.integers(5, 50, size=len(dates)),
            "day_of_week": dates.dayofweek,
            "is_weekend": dates.dayofweek >= 5,
            "month": dates.month,
        }
    )
    return cast(list[dict[str, Any]], df.to_dict(orient="records"))

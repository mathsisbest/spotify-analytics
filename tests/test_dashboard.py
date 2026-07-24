from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pandas as pd
import pytest
import streamlit as st

from dashboard.data import (
    get_daily_summary,
    get_forecast,
    get_genre_trends,
    get_listening_heatmap,
    get_mood_map,
    get_raw_history,
    get_recent_tracks,
    get_recommendations,
    get_top_artists,
    get_top_tracks,
    get_user_audio_profiles,
)

RECENT_KEYS = {"track_id", "track_name", "artist_name", "album_name", "played_at", "duration_ms"}
DAILY_KEYS = {"date", "minutes_listened", "track_count", "unique_artists"}
TOP_ARTIST_KEYS = {"artist_name", "listen_count", "minutes_listened"}
TOP_TRACK_KEYS = {"track_name", "artist_name", "listen_count"}
GENRE_TREND_KEYS = {"date", "genre", "listen_count"}
HEATMAP_KEYS = {"day", "hour", "listen_count"}
MOOD_MAP_KEYS = {"track_name", "artist_name", "valence", "energy", "danceability"}
FORECAST_KEYS = {"date", "predicted_minutes", "lower_bound", "upper_bound"}
RECOMMENDATION_KEYS = {"track_name", "artist_name", "score", "reason"}
RAW_HISTORY_KEYS = {
    "track_id",
    "track_name",
    "artist_name",
    "album_name",
    "played_at",
    "duration_ms",
}


@pytest.fixture(autouse=True)
def _mock_bq(mocker: Any) -> None:
    st.cache_data.clear()

    mock_client = mocker.MagicMock()

    def _mock_query(query: str, job_config: Any = None) -> Any:
        mock_job = mocker.MagicMock()
        query_upper = query.upper()

        limit = 100
        if job_config and job_config.query_parameters:
            for p in job_config.query_parameters:
                if p.name == "limit":
                    limit = p.value

        data: list[dict[str, Any]] = []
        if "RAW.STREAMING_HISTORY" in query_upper:
            if "DAYOFWEEK" in query_upper:
                # heatmap
                data = [
                    {
                        "day_of_week": d,
                        "hour_of_day": h,
                        "listen_count": 5,
                        "minutes": 15.0,
                    }
                    for d in range(1, 8)
                    for h in range(24)
                ]
            elif "DATE(PLAYED_AT)" in query_upper:
                if "GROUP BY 1, 2" in query_upper or "GENRE" in query_upper:
                    # genre trends
                    data = [
                        {"date": "2025-01-01", "genre": f"Genre {i}", "listen_count": 10 - i}
                        for i in range(1, 6)
                    ]
                else:
                    # daily summary
                    base = datetime(2025, 1, 1).date()
                    data = [
                        {
                            "date": (base + timedelta(days=i)).strftime("%Y-%m-%d"),
                            "track_count": 20,
                            "minutes_listened": 60.0,
                            "unique_artists": 10,
                        }
                        for i in range(30)
                    ]
            elif "VALENCE" in query_upper:
                # mood map or audio profiles
                if "AVG(" in query_upper:
                    data = [
                        {
                            "valence": 0.6,
                            "energy": 0.7,
                            "danceability": 0.65,
                            "acousticness": 0.3,
                            "liveness": 0.2,
                        }
                    ]
                else:
                    data = [
                        {
                            "track_name": f"Track {i}",
                            "artist_name": f"Artist {i}",
                            "valence": 0.5,
                            "energy": 0.6,
                            "danceability": 0.7,
                        }
                        for i in range(1, 21)
                    ]
            elif (
                "GROUP BY TRACK_NAME, ARTIST_NAME" in query_upper
                or "GROUP BY TRACK_NAME" in query_upper
            ):
                # top tracks
                data = [
                    {
                        "track_name": f"Track {i}",
                        "artist_name": f"Artist {i}",
                        "listen_count": 100 - i,
                    }
                    for i in range(1, 101)
                ][:limit]
            elif "GROUP BY ARTIST_NAME" in query_upper:
                # top artists
                data = [
                    {
                        "artist_name": f"Artist {i}",
                        "listen_count": 200 - i,
                        "minutes_listened": 600.0 - i * 3,
                    }
                    for i in range(1, 101)
                ][:limit]
            else:
                # recent tracks
                base_time = datetime(2025, 1, 1, 12, 0, 0)
                data = [
                    {
                        "track_id": f"track_{i}",
                        "track_name": f"Track {i}",
                        "artist_name": f"Artist {i}",
                        "album_name": f"Album {i}",
                        "played_at": (base_time - timedelta(minutes=i * 10)).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "duration_ms": 200000,
                    }
                    for i in range(limit)
                ]
        elif "ML_FORECAST" in query_upper:
            base = datetime(2025, 1, 1).date()
            data = [
                {
                    "forecast_date": (base + timedelta(days=i)).strftime("%Y-%m-%d"),
                    "predicted_minutes": 100.0,
                    "lower_bound": 80.0,
                    "upper_bound": 120.0,
                }
                for i in range(14)
            ]
        else:
            data = []

        mock_df = pd.DataFrame(data)
        mock_job.to_dataframe.return_value = mock_df
        return mock_job

    mock_client.query.side_effect = _mock_query
    mocker.patch("dashboard.data.get_bq_client", return_value=mock_client)


class TestGetRecentTracks:
    def test_returns_list_of_dicts(self) -> None:
        result = get_recent_tracks(limit=20)
        assert isinstance(result, list)
        assert len(result) == 20
        assert all(isinstance(row, dict) for row in result)

    def test_has_all_keys(self) -> None:
        result = get_recent_tracks(limit=20)
        for row in result:
            assert set(row.keys()) == RECENT_KEYS

    def test_correct_types(self) -> None:
        result = get_recent_tracks(limit=20)
        for row in result:
            assert isinstance(row["track_id"], str)
            assert isinstance(row["track_name"], str)
            assert isinstance(row["artist_name"], str)
            assert isinstance(row["album_name"], str)
            assert isinstance(row["played_at"], str)
            assert isinstance(row["duration_ms"], int)

    def test_values_in_expected_ranges(self) -> None:
        result = get_recent_tracks(limit=20)
        for row in result:
            assert 100000 <= row["duration_ms"] <= 600000

    def test_deterministic_output(self) -> None:
        assert get_recent_tracks(limit=20) == get_recent_tracks(limit=20)

    def test_respects_limit(self) -> None:
        assert len(get_recent_tracks(limit=5)) == 5
        assert len(get_recent_tracks(limit=100)) == 100

    def test_track_ids_unique(self) -> None:
        result = get_recent_tracks(limit=20)
        ids = [r["track_id"] for r in result]
        assert len(ids) == len(set(ids))


class TestGetDailySummary:
    def test_returns_list_of_dicts(self) -> None:
        result = get_daily_summary("2025-01-01", "2025-01-07")
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(row, dict) for row in result)

    def test_has_all_keys(self) -> None:
        result = get_daily_summary("2025-01-01", "2025-01-07")
        for row in result:
            assert DAILY_KEYS.issubset(set(row.keys()))

    def test_correct_types(self) -> None:
        result = get_daily_summary("2025-01-01", "2025-01-07")
        for row in result:
            assert isinstance(row["date"], str)
            assert isinstance(row["minutes_listened"], float)
            assert isinstance(row["track_count"], int)
            assert isinstance(row["unique_artists"], int)


class TestGetTopArtists:
    def test_returns_list_of_dicts(self) -> None:
        result = get_top_artists(limit=10)
        assert isinstance(result, list)
        assert len(result) == 10

    def test_has_all_keys(self) -> None:
        result = get_top_artists(limit=10)
        for row in result:
            assert TOP_ARTIST_KEYS.issubset(set(row.keys()))


class TestGetTopTracks:
    def test_returns_list_of_dicts(self) -> None:
        result = get_top_tracks(limit=10)
        assert isinstance(result, list)
        assert len(result) == 10

    def test_has_all_keys(self) -> None:
        result = get_top_tracks(limit=10)
        for row in result:
            assert TOP_TRACK_KEYS.issubset(set(row.keys()))


class TestGetGenreTrends:
    def test_returns_list_of_dicts(self) -> None:
        result = get_genre_trends()
        assert isinstance(result, list)

    def test_has_all_keys(self) -> None:
        result = get_genre_trends()
        for row in result:
            assert GENRE_TREND_KEYS.issubset(set(row.keys()))


class TestGetListeningHeatmap:
    def test_returns_heatmap(self) -> None:
        result = get_listening_heatmap()
        assert isinstance(result, list)
        assert len(result) == 168
        for row in result:
            assert HEATMAP_KEYS.issubset(set(row.keys()))


class TestGetMoodMap:
    def test_returns_mood_map(self) -> None:
        result = get_mood_map()
        assert isinstance(result, list)
        for row in result:
            assert set(row.keys()) == MOOD_MAP_KEYS


class TestGetForecast:
    def test_returns_forecast(self) -> None:
        result = get_forecast()
        assert isinstance(result, list)


class TestGetRecommendations:
    def test_returns_recommendations(self) -> None:
        result = get_recommendations()
        assert isinstance(result, list)
        for row in result:
            assert set(row.keys()) == RECOMMENDATION_KEYS


class TestGetRawHistory:
    def test_returns_raw_history(self) -> None:
        result = get_raw_history(limit=10)
        assert isinstance(result, list)
        assert len(result) == 10
        for row in result:
            assert set(row.keys()) == RAW_HISTORY_KEYS


class TestUserProfileSupport:
    def test_user_audio_profiles(self) -> None:
        profiles = get_user_audio_profiles()
        assert "Shylla" in profiles
        assert "valence" in profiles["Shylla"]

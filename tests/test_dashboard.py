from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pytest

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
)

RECENT_KEYS = {"track_id", "track_name", "artist_name", "album_name", "played_at", "duration_ms"}
DAILY_KEYS = {"listening_date", "minutes_listened", "track_count", "artist_count"}
TOP_ARTIST_KEYS = {"artist_name", "listen_count", "minutes_listened"}
TOP_TRACK_KEYS = {"track_name", "artist_name", "listen_count"}
GENRE_TREND_KEYS = {"listening_date", "genre", "listen_count", "share"}
HEATMAP_KEYS = {"day_of_week", "hour_of_day", "minutes"}
MOOD_MAP_KEYS = {
    "track_id",
    "track_name",
    "artist_name",
    "danceability",
    "energy",
    "valence",
    "tempo",
    "cluster_id",
}
FORECAST_KEYS = {"forecast_date", "predicted_minutes", "lower_bound", "upper_bound"}
RECOMMENDATION_KEYS = {"track_name", "artist_name", "score", "reason"}
RAW_HISTORY_KEYS = {"track_name", "artist_name", "album_name", "played_at", "duration_ms"}


@pytest.fixture(autouse=True)
def _mock_bq(mocker: Any) -> None:
    mocker.patch("streamlit.connection", side_effect=Exception("no BQ available"))


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
            datetime.fromisoformat(row["played_at"])

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
            assert set(row.keys()) == DAILY_KEYS

    def test_correct_types(self) -> None:
        result = get_daily_summary("2025-01-01", "2025-01-07")
        for row in result:
            assert isinstance(row["listening_date"], str)
            assert isinstance(row["minutes_listened"], float)
            assert isinstance(row["track_count"], int)
            assert isinstance(row["artist_count"], int)

    def test_values_in_expected_ranges(self) -> None:
        result = get_daily_summary("2025-01-01", "2025-01-07")
        for row in result:
            assert 30 <= row["minutes_listened"] <= 300
            assert 10 <= row["track_count"] <= 99
            assert 5 <= row["artist_count"] <= 49

    def test_dates_are_consecutive(self) -> None:
        result = get_daily_summary("2025-01-01", "2025-01-07")
        dates = [row["listening_date"] for row in result]
        expected = [f"2025-01-{d:02d}" for d in range(1, 8)]
        assert dates == expected

    def test_deterministic_output(self) -> None:
        assert get_daily_summary("2025-01-01", "2025-01-07") == get_daily_summary(
            "2025-01-01", "2025-01-07"
        )

    def test_empty_date_range_returns_empty_list(self) -> None:
        assert get_daily_summary("2025-12-31", "2025-01-01") == []

    def test_date_format(self) -> None:
        result = get_daily_summary("2025-01-01", "2025-01-07")
        for row in result:
            datetime.strptime(row["listening_date"], "%Y-%m-%d")


class TestGetTopArtists:
    def test_returns_list_of_dicts(self) -> None:
        result = get_top_artists(limit=10)
        assert isinstance(result, list)
        assert len(result) == 10
        assert all(isinstance(row, dict) for row in result)

    def test_has_all_keys(self) -> None:
        result = get_top_artists(limit=10)
        for row in result:
            assert set(row.keys()) == TOP_ARTIST_KEYS

    def test_correct_types(self) -> None:
        result = get_top_artists(limit=10)
        for row in result:
            assert isinstance(row["artist_name"], str)
            assert isinstance(row["listen_count"], int)
            assert isinstance(row["minutes_listened"], float)

    def test_values_in_expected_ranges(self) -> None:
        result = get_top_artists(limit=10)
        for row in result:
            assert row["listen_count"] >= 0
            assert row["minutes_listened"] >= 0.0

    def test_deterministic_output(self) -> None:
        assert get_top_artists(limit=10) == get_top_artists(limit=10)

    def test_respects_limit(self) -> None:
        assert len(get_top_artists(limit=5)) == 5
        assert len(get_top_artists(limit=25)) == 25

    def test_sorted_descending(self) -> None:
        result = get_top_artists(limit=10)
        counts = [r["listen_count"] for r in result]
        assert counts == sorted(counts, reverse=True)


class TestGetTopTracks:
    def test_returns_list_of_dicts(self) -> None:
        result = get_top_tracks(limit=10)
        assert isinstance(result, list)
        assert len(result) == 10
        assert all(isinstance(row, dict) for row in result)

    def test_has_all_keys(self) -> None:
        result = get_top_tracks(limit=10)
        for row in result:
            assert set(row.keys()) == TOP_TRACK_KEYS

    def test_correct_types(self) -> None:
        result = get_top_tracks(limit=10)
        for row in result:
            assert isinstance(row["track_name"], str)
            assert isinstance(row["artist_name"], str)
            assert isinstance(row["listen_count"], int)

    def test_values_in_expected_ranges(self) -> None:
        result = get_top_tracks(limit=10)
        for row in result:
            assert row["listen_count"] >= 0

    def test_deterministic_output(self) -> None:
        assert get_top_tracks(limit=10) == get_top_tracks(limit=10)

    def test_respects_limit(self) -> None:
        assert len(get_top_tracks(limit=5)) == 5
        assert len(get_top_tracks(limit=25)) == 25

    def test_sorted_descending(self) -> None:
        result = get_top_tracks(limit=10)
        counts = [r["listen_count"] for r in result]
        assert counts == sorted(counts, reverse=True)


class TestGetGenreTrends:
    def test_returns_list_of_dicts(self) -> None:
        result = get_genre_trends("2025-06-01", "2025-06-03")
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(row, dict) for row in result)

    def test_has_all_keys(self) -> None:
        result = get_genre_trends("2025-06-01", "2025-06-03")
        for row in result:
            assert set(row.keys()) == GENRE_TREND_KEYS

    def test_correct_types(self) -> None:
        result = get_genre_trends("2025-06-01", "2025-06-03")
        for row in result:
            assert isinstance(row["listening_date"], str)
            assert isinstance(row["genre"], str)
            assert isinstance(row["listen_count"], int)
            assert isinstance(row["share"], float)

    def test_share_values_sum_to_one_per_date(self) -> None:
        result = get_genre_trends("2025-06-01", "2025-06-03")
        by_date: dict[str, list[dict[str, Any]]] = {}
        for row in result:
            by_date.setdefault(row["listening_date"], []).append(row)
        for date, rows in by_date.items():
            total = sum(r["share"] for r in rows)
            assert abs(total - 1.0) < 0.01

    def test_share_in_range(self) -> None:
        result = get_genre_trends("2025-06-01", "2025-06-03")
        for row in result:
            assert 0.0 <= row["share"] <= 1.0

    def test_deterministic_output(self) -> None:
        assert get_genre_trends("2025-06-01", "2025-06-03") == get_genre_trends(
            "2025-06-01", "2025-06-03"
        )

    def test_empty_date_range_returns_empty_list(self) -> None:
        assert get_genre_trends("2025-12-31", "2025-01-01") == []

    def test_date_format(self) -> None:
        result = get_genre_trends("2025-06-01", "2025-06-03")
        for row in result:
            datetime.strptime(row["listening_date"], "%Y-%m-%d")


class TestGetListeningHeatmap:
    def test_returns_168_rows(self) -> None:
        result = get_listening_heatmap()
        assert len(result) == 168

    def test_has_all_keys(self) -> None:
        result = get_listening_heatmap()
        for row in result:
            assert set(row.keys()) == HEATMAP_KEYS

    def test_correct_types(self) -> None:
        result = get_listening_heatmap()
        for row in result:
            assert isinstance(row["day_of_week"], int)
            assert isinstance(row["hour_of_day"], int)
            assert isinstance(row["minutes"], float)

    def test_values_in_expected_ranges(self) -> None:
        result = get_listening_heatmap()
        for row in result:
            assert 0 <= row["day_of_week"] <= 6
            assert 0 <= row["hour_of_day"] <= 23
            assert row["minutes"] >= 0.0

    def test_deterministic_output(self) -> None:
        assert get_listening_heatmap() == get_listening_heatmap()

    def test_every_hour_represented(self) -> None:
        result = get_listening_heatmap()
        cells = {(r["day_of_week"], r["hour_of_day"]) for r in result}
        assert len(cells) == 168
        for day in range(7):
            for hour in range(24):
                assert (day, hour) in cells

    def test_peak_hours_have_more_minutes(self) -> None:
        result = get_listening_heatmap()
        evening = [r["minutes"] for r in result if 17 <= r["hour_of_day"] <= 22]
        morning = [r["minutes"] for r in result if 0 <= r["hour_of_day"] <= 5]
        assert sum(evening) / len(evening) > sum(morning) / len(morning)


class TestGetMoodMap:
    def test_returns_list_of_dicts(self) -> None:
        result = get_mood_map()
        assert isinstance(result, list)
        assert len(result) == 100
        assert all(isinstance(row, dict) for row in result)

    def test_has_all_keys(self) -> None:
        result = get_mood_map()
        for row in result:
            assert set(row.keys()) == MOOD_MAP_KEYS

    def test_correct_types(self) -> None:
        result = get_mood_map()
        for row in result:
            assert isinstance(row["track_id"], str)
            assert isinstance(row["track_name"], str)
            assert isinstance(row["artist_name"], str)
            assert isinstance(row["danceability"], float)
            assert isinstance(row["energy"], float)
            assert isinstance(row["valence"], float)
            assert isinstance(row["tempo"], float)
            assert isinstance(row["cluster_id"], int)

    def test_audio_feature_ranges(self) -> None:
        result = get_mood_map()
        for row in result:
            assert 0.0 <= row["danceability"] <= 1.0
            assert 0.0 <= row["energy"] <= 1.0
            assert 0.0 <= row["valence"] <= 1.0
            assert 60.0 <= row["tempo"] <= 200.0

    def test_cluster_id_in_range(self) -> None:
        result = get_mood_map()
        for row in result:
            assert 0 <= row["cluster_id"] <= 4

    def test_deterministic_output(self) -> None:
        assert get_mood_map() == get_mood_map()

    def test_track_ids_unique(self) -> None:
        result = get_mood_map()
        ids = [r["track_id"] for r in result]
        assert len(ids) == len(set(ids))


class TestGetForecast:
    def test_returns_list_of_dicts(self) -> None:
        result = get_forecast()
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(row, dict) for row in result)

    def test_has_all_keys(self) -> None:
        result = get_forecast()
        for row in result:
            assert set(row.keys()) == FORECAST_KEYS

    def test_correct_types(self) -> None:
        result = get_forecast()
        for row in result:
            assert isinstance(row["forecast_date"], str)
            assert isinstance(row["predicted_minutes"], float)
            assert isinstance(row["lower_bound"], float)
            assert isinstance(row["upper_bound"], float)

    def test_lower_less_than_predicted_less_than_upper(self) -> None:
        result = get_forecast()
        for row in result:
            assert row["lower_bound"] <= row["predicted_minutes"] <= row["upper_bound"]

    def test_values_in_expected_ranges(self) -> None:
        result = get_forecast()
        for row in result:
            assert row["predicted_minutes"] >= 0.0
            assert row["lower_bound"] >= 0.0
            assert row["upper_bound"] >= 0.0

    def test_deterministic_output(self) -> None:
        assert get_forecast() == get_forecast()

    def test_dates_are_consecutive(self) -> None:
        result = get_forecast()
        dates = [datetime.strptime(r["forecast_date"], "%Y-%m-%d") for r in result]
        for i in range(len(dates) - 1):
            assert dates[i + 1] - dates[i] == timedelta(days=1)

    def test_returns_14_rows(self) -> None:
        assert len(get_forecast()) == 14

    def test_date_format(self) -> None:
        result = get_forecast()
        for row in result:
            datetime.strptime(row["forecast_date"], "%Y-%m-%d")


class TestGetRecommendations:
    def test_returns_list_of_dicts(self) -> None:
        result = get_recommendations()
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(row, dict) for row in result)

    def test_has_all_keys(self) -> None:
        result = get_recommendations()
        for row in result:
            assert set(row.keys()) == RECOMMENDATION_KEYS

    def test_correct_types(self) -> None:
        result = get_recommendations()
        for row in result:
            assert isinstance(row["track_name"], str)
            assert isinstance(row["artist_name"], str)
            assert isinstance(row["score"], float)
            assert isinstance(row["reason"], str)

    def test_values_in_expected_ranges(self) -> None:
        result = get_recommendations()
        for row in result:
            assert 0.0 <= row["score"] <= 1.0
            assert len(row["reason"]) > 0

    def test_deterministic_output(self) -> None:
        assert get_recommendations() == get_recommendations()

    def test_returns_10_recommendations(self) -> None:
        assert len(get_recommendations()) == 10


class TestGetRawHistory:
    def test_returns_list_of_dicts(self) -> None:
        result = get_raw_history(limit=100)
        assert isinstance(result, list)
        assert len(result) == 100
        assert all(isinstance(row, dict) for row in result)

    def test_has_all_keys(self) -> None:
        result = get_raw_history(limit=100)
        for row in result:
            assert set(row.keys()) == RAW_HISTORY_KEYS

    def test_correct_types(self) -> None:
        result = get_raw_history(limit=100)
        for row in result:
            assert isinstance(row["track_name"], str)
            assert isinstance(row["artist_name"], str)
            assert isinstance(row["album_name"], str)
            assert isinstance(row["played_at"], str)
            assert isinstance(row["duration_ms"], int)

    def test_values_in_expected_ranges(self) -> None:
        result = get_raw_history(limit=100)
        for row in result:
            assert 100000 <= row["duration_ms"] <= 600000
            datetime.fromisoformat(row["played_at"])

    def test_deterministic_output(self) -> None:
        assert get_raw_history(limit=100) == get_raw_history(limit=100)

    def test_respects_limit(self) -> None:
        assert len(get_raw_history(limit=10)) == 10
        assert len(get_raw_history(limit=200)) == 200

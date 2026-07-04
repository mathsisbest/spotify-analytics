from datetime import datetime, timedelta

from ml.features import (
    build_cluster_features,
    build_forecast_features,
    build_skip_prediction_features,
)

CLUSTER_KEYS = {
    "track_id",
    "danceability",
    "energy",
    "valence",
    "tempo",
    "loudness",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "key",
    "mode",
    "time_signature",
    "duration_ms",
}

SKIP_KEYS = CLUSTER_KEYS | {
    "played_at",
    "artist_id",
    "hour_of_day",
    "day_of_week",
    "is_weekend",
    "session_position",
    "artist_play_count_30d",
    "track_play_count_30d",
    "target_replayed",
}

FORECAST_KEYS = {
    "date",
    "minutes_listened",
    "track_count",
    "artist_count",
    "day_of_week",
    "is_weekend",
    "month",
}


class TestBuildClusterFeatures:
    def test_returns_list_of_dicts(self) -> None:
        result = build_cluster_features()
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(row, dict) for row in result)

    def test_has_all_keys(self) -> None:
        result = build_cluster_features()
        for row in result:
            assert set(row.keys()) == CLUSTER_KEYS

    def test_correct_types(self) -> None:
        result = build_cluster_features()
        for row in result:
            assert isinstance(row["track_id"], str)
            assert isinstance(row["danceability"], float)
            assert isinstance(row["energy"], float)
            assert isinstance(row["valence"], float)
            assert isinstance(row["tempo"], float)
            assert isinstance(row["loudness"], float)
            assert isinstance(row["speechiness"], float)
            assert isinstance(row["acousticness"], float)
            assert isinstance(row["instrumentalness"], float)
            assert isinstance(row["liveness"], float)
            assert isinstance(row["key"], int)
            assert isinstance(row["mode"], int)
            assert isinstance(row["time_signature"], int)
            assert isinstance(row["duration_ms"], int)

    def test_values_in_expected_ranges(self) -> None:
        result = build_cluster_features()
        for row in result:
            assert 0.0 <= row["danceability"] <= 1.0
            assert 0.0 <= row["energy"] <= 1.0
            assert 0.0 <= row["valence"] <= 1.0
            assert 60.0 <= row["tempo"] <= 200.0
            assert -60.0 <= row["loudness"] <= 0.0
            assert 0.0 <= row["speechiness"] <= 1.0
            assert 0.0 <= row["acousticness"] <= 1.0
            assert 0.0 <= row["instrumentalness"] <= 1.0
            assert 0.0 <= row["liveness"] <= 1.0
            assert 0 <= row["key"] <= 11
            assert row["mode"] in (0, 1)
            assert row["time_signature"] in (3, 4, 5, 6, 7)
            assert 100000 <= row["duration_ms"] <= 600000

    def test_deterministic_output(self) -> None:
        assert build_cluster_features() == build_cluster_features()

    def test_returns_100_rows(self) -> None:
        assert len(build_cluster_features()) == 100


class TestBuildSkipPredictionFeatures:
    def test_returns_list_of_dicts(self) -> None:
        result = build_skip_prediction_features("2024-01-01", "2024-01-07")
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(row, dict) for row in result)

    def test_has_all_keys(self) -> None:
        result = build_skip_prediction_features("2024-01-01", "2024-01-07")
        for row in result:
            assert set(row.keys()) == SKIP_KEYS

    def test_correct_types(self) -> None:
        result = build_skip_prediction_features("2024-01-01", "2024-01-07")
        for row in result:
            assert isinstance(row["track_id"], str)
            assert isinstance(row["played_at"], str)
            assert isinstance(row["artist_id"], str)
            assert isinstance(row["danceability"], float)
            assert isinstance(row["energy"], float)
            assert isinstance(row["tempo"], float)
            assert isinstance(row["key"], int)
            assert isinstance(row["hour_of_day"], int)
            assert isinstance(row["day_of_week"], int)
            assert isinstance(row["is_weekend"], bool)
            assert isinstance(row["session_position"], int)
            assert isinstance(row["artist_play_count_30d"], int)
            assert isinstance(row["track_play_count_30d"], int)
            assert isinstance(row["target_replayed"], bool)

    def test_dates_within_range(self) -> None:
        start, end = "2024-01-01", "2024-01-07"
        result = build_skip_prediction_features(start, end)
        for row in result:
            date_part = row["played_at"][:10]
            assert start <= date_part <= end

    def test_temporal_features(self) -> None:
        result = build_skip_prediction_features("2024-01-01", "2024-01-07")
        for row in result:
            assert 0 <= row["hour_of_day"] <= 23
            assert 0 <= row["day_of_week"] <= 6
            assert isinstance(row["is_weekend"], bool)

    def test_behavioral_features(self) -> None:
        result = build_skip_prediction_features("2024-01-01", "2024-01-07")
        for row in result:
            assert row["session_position"] >= 1
            assert isinstance(row["artist_play_count_30d"], int)
            assert isinstance(row["track_play_count_30d"], int)
            assert isinstance(row["target_replayed"], bool)

    def test_empty_date_range_returns_empty_list(self) -> None:
        assert build_skip_prediction_features("2024-12-31", "2024-01-01") == []

    def test_deterministic_output(self) -> None:
        r1 = build_skip_prediction_features("2024-01-01", "2024-01-07")
        r2 = build_skip_prediction_features("2024-01-01", "2024-01-07")
        assert r1 == r2

    def test_played_at_iso_format(self) -> None:
        result = build_skip_prediction_features("2024-01-01", "2024-01-07")
        for row in result:
            datetime.fromisoformat(row["played_at"])

    def test_weekend_flag_matches_day(self) -> None:
        result = build_skip_prediction_features("2024-01-01", "2024-01-07")
        for row in result:
            expected = row["day_of_week"] >= 5
            assert row["is_weekend"] == expected

    def test_audio_features_in_expected_ranges(self) -> None:
        result = build_skip_prediction_features("2024-01-01", "2024-01-07")
        for row in result:
            assert 0.0 <= row["danceability"] <= 1.0
            assert 0.0 <= row["energy"] <= 1.0
            assert 60.0 <= row["tempo"] <= 200.0


class TestBuildForecastFeatures:
    def test_returns_list_of_dicts(self) -> None:
        result = build_forecast_features()
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(row, dict) for row in result)

    def test_has_all_keys(self) -> None:
        result = build_forecast_features()
        for row in result:
            assert set(row.keys()) == FORECAST_KEYS

    def test_correct_types(self) -> None:
        result = build_forecast_features()
        for row in result:
            assert isinstance(row["date"], str)
            assert isinstance(row["minutes_listened"], float)
            assert isinstance(row["track_count"], int)
            assert isinstance(row["artist_count"], int)
            assert isinstance(row["day_of_week"], int)
            assert isinstance(row["is_weekend"], bool)
            assert isinstance(row["month"], int)

    def test_values_in_expected_ranges(self) -> None:
        result = build_forecast_features()
        for row in result:
            assert row["minutes_listened"] >= 0.0
            assert row["track_count"] >= 0
            assert row["artist_count"] >= 0
            assert 0 <= row["day_of_week"] <= 6
            assert 1 <= row["month"] <= 12

    def test_dates_are_consecutive(self) -> None:
        result = build_forecast_features()
        dates = [row["date"] for row in result]
        for i in range(len(dates) - 1):
            d1 = datetime.strptime(dates[i], "%Y-%m-%d")
            d2 = datetime.strptime(dates[i + 1], "%Y-%m-%d")
            assert d2 - d1 == timedelta(days=1)

    def test_returns_90_rows(self) -> None:
        assert len(build_forecast_features()) == 90

    def test_deterministic_output(self) -> None:
        assert build_forecast_features() == build_forecast_features()

    def test_date_format(self) -> None:
        result = build_forecast_features()
        for row in result:
            datetime.strptime(row["date"], "%Y-%m-%d")

    def test_weekend_flag_matches_day(self) -> None:
        result = build_forecast_features()
        for row in result:
            expected = row["day_of_week"] >= 5
            assert row["is_weekend"] == expected

    def test_month_matches_date(self) -> None:
        result = build_forecast_features()
        for row in result:
            d = datetime.strptime(row["date"], "%Y-%m-%d")
            assert row["month"] == d.month

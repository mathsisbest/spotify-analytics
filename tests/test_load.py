from datetime import datetime
from unittest.mock import MagicMock, create_autospec, patch

import pytest
from google.cloud import bigquery

from spotify_analytics.load import BigQueryLoader, BigQueryLoaderError
from spotify_analytics.models import IngestionRun, StreamingHistoryItem, TrackFeatures


@pytest.fixture
def loader() -> BigQueryLoader:
    mock_client = create_autospec(bigquery.Client, instance=True)
    return BigQueryLoader(project_id="test-project", dataset_id="raw", client=mock_client)


class TestBigQueryLoaderInit:
    def test_sets_project_and_dataset(self, loader: BigQueryLoader) -> None:
        assert loader._project_id == "test-project"
        assert loader._dataset_id == "raw"

    def test_table_ref_format(self, loader: BigQueryLoader) -> None:
        ref = loader._table_ref("streaming_history")
        assert ref == "test-project.raw.streaming_history"


class TestBigQueryLoaderUpsertStreamingHistory:
    def test_empty_items_returns_zero(self, loader: BigQueryLoader) -> None:
        result = loader.upsert_streaming_history([])
        assert result == 0

    def test_single_item(self, loader: BigQueryLoader) -> None:
        item = StreamingHistoryItem(
            track_id="t1",
            played_at="2024-01-01T12:00:00Z",
            track_name="Test Track",
            artist_names=["Artist A"],
            album_name="Album",
            duration_ms=200000,
        )

        with patch.object(loader._client, "insert_rows_json", return_value=[]) as mock_insert:
            result = loader.upsert_streaming_history([item])

        assert result == 1
        mock_insert.assert_called_once()
        args = mock_insert.call_args[0]
        assert args[0] == "test-project.raw.streaming_history"
        rows = args[1]
        assert len(rows) == 1
        assert rows[0]["track_id"] == "t1"
        assert rows[0]["track_name"] == "Test Track"

    def test_insert_error_raises(self, loader: BigQueryLoader) -> None:
        item = StreamingHistoryItem(track_id="t1", played_at="2024-01-01T12:00:00Z")
        errors = [{"index": 0, "errors": [{"reason": "invalid"}]}]

        with (
            patch.object(loader._client, "insert_rows_json", return_value=errors),
            pytest.raises(BigQueryLoaderError, match="Insert errors"),
        ):
            loader.upsert_streaming_history([item])

    def test_multiple_items(self, loader: BigQueryLoader) -> None:
        items = [
            StreamingHistoryItem(track_id="t1", played_at="2024-01-01T12:00:00Z"),
            StreamingHistoryItem(track_id="t2", played_at="2024-01-01T13:00:00Z"),
        ]
        with patch.object(loader._client, "insert_rows_json", return_value=[]) as mock_insert:
            result = loader.upsert_streaming_history(items)

        assert result == 2
        assert len(mock_insert.call_args[0][1]) == 2


class TestBigQueryLoaderUpsertTrackFeatures:
    def test_empty_features_returns_zero(self, loader: BigQueryLoader) -> None:
        result = loader.upsert_track_features([])
        assert result == 0

    def test_single_feature(self, loader: BigQueryLoader) -> None:
        feat = TrackFeatures(track_id="t1", danceability=0.8, energy=0.9)

        with patch.object(loader._client, "insert_rows_json", return_value=[]) as mock_insert:
            result = loader.upsert_track_features([feat])

        assert result == 1
        rows = mock_insert.call_args[0][1]
        assert rows[0]["danceability"] == 0.8
        assert rows[0]["energy"] == 0.9

    def test_insert_error_raises(self, loader: BigQueryLoader) -> None:
        feat = TrackFeatures(track_id="t1")

        err_result = [{"index": 0, "errors": ["err"]}]
        with (
            patch.object(loader._client, "insert_rows_json", return_value=err_result),
            pytest.raises(BigQueryLoaderError, match="Insert errors"),
        ):
            loader.upsert_track_features([feat])


class TestBigQueryLoaderWriteIngestionRun:
    def test_writes_run_row(self, loader: BigQueryLoader) -> None:
        now = datetime.utcnow()
        run = IngestionRun(
            run_id="r1",
            started_at=now,
            finished_at=now,
            rows_ingested=10,
            rows_enriched=5,
            status="success",
            duration_seconds=2.5,
        )

        with patch.object(loader._client, "insert_rows_json", return_value=[]) as mock_insert:
            loader.write_ingestion_run(run)

        rows = mock_insert.call_args[0][1]
        assert len(rows) == 1
        assert rows[0]["run_id"] == "r1"
        assert rows[0]["status"] == "success"
        assert rows[0]["rows_ingested"] == 10

    def test_write_error_raises(self, loader: BigQueryLoader) -> None:
        now = datetime.utcnow()
        run = IngestionRun(run_id="r1", started_at=now)

        err_result = [{"error": "disk full"}]
        with (
            patch.object(loader._client, "insert_rows_json", return_value=err_result),
            pytest.raises(BigQueryLoaderError, match="Insert errors"),
        ):
            loader.write_ingestion_run(run)

    def test_failed_run_has_error_message(self, loader: BigQueryLoader) -> None:
        now = datetime.utcnow()
        run = IngestionRun(
            run_id="r1",
            started_at=now,
            status="failed",
            error_message="timeout connecting to API",
        )

        with patch.object(loader._client, "insert_rows_json", return_value=[]) as mock_insert:
            loader.write_ingestion_run(run)

        row = mock_insert.call_args[0][1][0]
        assert row["status"] == "failed"
        assert row["error_message"] == "timeout connecting to API"


class TestBigQueryLoaderGetRecentTrackIds:
    def test_returns_set_of_ids(self, loader: BigQueryLoader) -> None:
        mock_query = MagicMock()
        mock_query.__iter__.return_value = [
            MagicMock(track_id="t1"),
            MagicMock(track_id="t2"),
        ]

        with patch.object(loader._client, "query", return_value=mock_query):
            result = loader.get_recent_track_ids(limit=100)

        assert result == {"t1", "t2"}

    def test_empty_result(self, loader: BigQueryLoader) -> None:
        mock_query = MagicMock()
        mock_query.__iter__.return_value = []

        with patch.object(loader._client, "query", return_value=mock_query):
            result = loader.get_recent_track_ids()

        assert result == set()


class TestBigQueryLoaderGetTrackIdsMissingFeatures:
    def test_no_input_returns_empty(self, loader: BigQueryLoader) -> None:
        result = loader.get_track_ids_missing_features(set())
        assert result == set()

    def test_all_missing(self, loader: BigQueryLoader) -> None:
        mock_query = MagicMock()
        mock_query.__iter__.return_value = []

        with patch.object(loader._client, "query", return_value=mock_query):
            result = loader.get_track_ids_missing_features({"t1", "t2"})

        assert result == {"t1", "t2"}

    def test_some_exist(self, loader: BigQueryLoader) -> None:
        mock_query = MagicMock()
        mock_query.__iter__.return_value = [MagicMock(track_id="t1")]

        with patch.object(loader._client, "query", return_value=mock_query):
            result = loader.get_track_ids_missing_features({"t1", "t2", "t3"})

        assert result == {"t2", "t3"}

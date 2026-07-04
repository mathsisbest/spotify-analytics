import os
from unittest.mock import Mock, create_autospec, patch

import pytest
from google.cloud import bigquery

from spotify_analytics.auth import TokenStore
from spotify_analytics.client import SpotifyClientError
from spotify_analytics.ingest import Ingestor, _build_token_store, _env_or_raise, main
from spotify_analytics.load import BigQueryLoaderError
from spotify_analytics.models import (
    IngestionRun,
    StreamingHistoryItem,
    TrackFeatures,
)


class TestEnvOrRaise:
    def test_returns_value(self) -> None:
        os.environ["TEST_VAR"] = "hello"
        assert _env_or_raise("TEST_VAR") == "hello"

    def test_raises_on_missing(self) -> None:
        if "MISSING_VAR" in os.environ:
            del os.environ["MISSING_VAR"]
        with pytest.raises(ValueError, match="Missing required env var: MISSING_VAR"):
            _env_or_raise("MISSING_VAR")

    def test_raises_on_empty(self) -> None:
        os.environ["EMPTY_VAR"] = ""
        with pytest.raises(ValueError, match="Missing required env var: EMPTY_VAR"):
            _env_or_raise("EMPTY_VAR")


class TestBuildTokenStore:
    def test_creates_token_store(self) -> None:
        os.environ["SPOTIFY_CLIENT_ID"] = "test_cid"
        os.environ["SPOTIFY_CLIENT_SECRET"] = "test_csec"
        store = _build_token_store()
        assert isinstance(store, TokenStore)

    def test_missing_client_id_raises(self) -> None:
        if "SPOTIFY_CLIENT_ID" in os.environ:
            del os.environ["SPOTIFY_CLIENT_ID"]
        os.environ["SPOTIFY_CLIENT_SECRET"] = "csec"
        with pytest.raises(ValueError, match="SPOTIFY_CLIENT_ID"):
            _build_token_store()


class TestIngestorInit:
    def test_default_project_from_env(self) -> None:
        os.environ["GCP_PROJECT_ID"] = "env-project"
        os.environ["SPOTIFY_CLIENT_ID"] = "cid"
        os.environ["SPOTIFY_CLIENT_SECRET"] = "csec"
        store = TokenStore("cid", "csec")
        store.set_tokens("tok", 3600)
        mock_client = create_autospec(bigquery.Client, instance=True)
        ingestor = Ingestor(token_store=store, loader_kwargs={"client": mock_client})
        assert ingestor._project_id == "env-project"

    def test_explicit_project_overrides_env(self) -> None:
        store = TokenStore("cid", "csec")
        store.set_tokens("tok", 3600)
        mock_client = create_autospec(bigquery.Client, instance=True)
        ingestor = Ingestor(
            token_store=store,
            project_id="explicit-project",
            loader_kwargs={"client": mock_client},
        )
        assert ingestor._project_id == "explicit-project"


class TestIngestorRun:
    @pytest.fixture
    def ingestor(self) -> Ingestor:
        os.environ["GCP_PROJECT_ID"] = "test-project"
        store = TokenStore("cid", "csec")
        store.set_tokens("tok", 3600)
        mock_client = create_autospec(bigquery.Client, instance=True)
        return Ingestor(
            token_store=store,
            project_id="test-project",
            loader_kwargs={"client": mock_client},
        )

    def test_successful_run(self, ingestor: Ingestor) -> None:
        items = [
            StreamingHistoryItem(track_id="t1", played_at="2024-01-01T00:00:00Z"),
        ]
        features = [
            TrackFeatures(track_id="t1", danceability=0.5),
        ]

        with (
            patch.object(ingestor._client, "get_recently_played", return_value=items),
            patch.object(ingestor._loader, "upsert_streaming_history", return_value=1),
            patch.object(ingestor._loader, "get_track_ids_missing_features", return_value={"t1"}),
            patch.object(ingestor._client, "get_several_audio_features", return_value=features),
            patch.object(ingestor._loader, "upsert_track_features", return_value=1),
            patch.object(ingestor._loader, "write_ingestion_run") as mock_write,
        ):
            run = ingestor.run()

        assert run.rows_ingested == 1
        assert run.rows_enriched == 1
        assert run.status == "success"
        assert run.duration_seconds is not None
        assert run.duration_seconds >= 0
        mock_write.assert_called_once_with(run)

    def test_happy_path_no_new_tracks(self, ingestor: Ingestor) -> None:
        items = [
            StreamingHistoryItem(track_id="t1", played_at="2024-01-01T00:00:00Z"),
        ]

        with (
            patch.object(ingestor._client, "get_recently_played", return_value=items),
            patch.object(ingestor._loader, "upsert_streaming_history", return_value=1),
            patch.object(ingestor._loader, "get_track_ids_missing_features", return_value=set()),
            patch.object(ingestor._loader, "write_ingestion_run") as mock_write,
        ):
            run = ingestor.run()

        assert run.rows_ingested == 1
        assert run.rows_enriched == 0
        assert run.status == "success"
        mock_write.assert_called_once()

    def test_no_recent_tracks(self, ingestor: Ingestor) -> None:
        with (
            patch.object(ingestor._client, "get_recently_played", return_value=[]),
            patch.object(ingestor._loader, "upsert_streaming_history", return_value=0),
            patch.object(ingestor._loader, "write_ingestion_run") as mock_write,
        ):
            run = ingestor.run()

        assert run.rows_ingested == 0
        assert run.rows_enriched == 0
        assert run.status == "success"
        mock_write.assert_called_once()

    def test_api_error_records_failure(self, ingestor: Ingestor) -> None:
        api_err = SpotifyClientError("API unavailable")
        with (
            patch.object(ingestor._client, "get_recently_played", side_effect=api_err),
            patch.object(ingestor._loader, "write_ingestion_run") as mock_write,
            pytest.raises(SpotifyClientError),
        ):
            ingestor.run()

        mock_write.assert_called_once()
        written_run = mock_write.call_args[0][0]
        assert written_run.status == "failed"
        assert "API unavailable" in (written_run.error_message or "")

    def test_loader_error_records_failure(self, ingestor: Ingestor) -> None:
        items = [StreamingHistoryItem(track_id="t1", played_at="2024-01-01T00:00:00Z")]
        bq_err = BigQueryLoaderError("BQ unavailable")

        with (
            patch.object(ingestor._client, "get_recently_played", return_value=items),
            patch.object(ingestor._loader, "upsert_streaming_history", side_effect=bq_err),
            patch.object(ingestor._loader, "write_ingestion_run") as mock_write,
            pytest.raises(BigQueryLoaderError),
        ):
            ingestor.run()

        written_run = mock_write.call_args[0][0]
        assert written_run.status == "failed"


class TestMain:
    def test_main_success(self) -> None:
        os.environ["SPOTIFY_CLIENT_ID"] = "cid"
        os.environ["SPOTIFY_CLIENT_SECRET"] = "csec"
        os.environ["SPOTIFY_REFRESH_TOKEN"] = "rtok"
        os.environ["GCP_PROJECT_ID"] = "test-project"

        from datetime import datetime

        mock_run = IngestionRun(
            run_id="r1",
            started_at=datetime.fromisoformat("2024-01-01T00:00:00"),
            finished_at=datetime.fromisoformat("2024-01-01T00:00:01"),
            rows_ingested=5,
            rows_enriched=2,
            status="success",
            duration_seconds=1.0,
        )

        with (
            patch("spotify_analytics.ingest.Ingestor") as mock_ingestor_cls,
            patch("spotify_analytics.ingest._env_or_raise", return_value="val"),
        ):
            mock_ingestor = Mock()
            mock_ingestor.run.return_value = mock_run
            mock_ingestor_cls.return_value = mock_ingestor
            result = main({}, None)

        assert "Ingested 5 rows" in result
        assert "enriched 2" in result
        assert "status=success" in result

    def test_main_missing_env(self) -> None:
        if "SPOTIFY_CLIENT_ID" in os.environ:
            del os.environ["SPOTIFY_CLIENT_ID"]
        if "SPOTIFY_REFRESH_TOKEN" in os.environ:
            del os.environ["SPOTIFY_REFRESH_TOKEN"]

        with pytest.raises(ValueError, match="Missing required env var"):
            main({}, None)

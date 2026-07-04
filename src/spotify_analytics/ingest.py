from __future__ import annotations

import os
import uuid
from datetime import datetime
from typing import Any

from spotify_analytics.auth import TokenStore
from spotify_analytics.client import SpotifyClient, SpotifyClientError
from spotify_analytics.enrich import find_tracks_needing_features
from spotify_analytics.load import BigQueryLoader, BigQueryLoaderError
from spotify_analytics.models import IngestionRun


def _env_or_raise(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        raise ValueError(f"Missing required env var: {name}")
    return val


def _build_token_store() -> TokenStore:
    return TokenStore(
        client_id=_env_or_raise("SPOTIFY_CLIENT_ID"),
        client_secret=_env_or_raise("SPOTIFY_CLIENT_SECRET"),
    )


class Ingestor:
    def __init__(
        self,
        token_store: TokenStore,
        project_id: str | None = None,
        dataset_id: str = "raw",
        loader_kwargs: dict[str, Any] | None = None,
    ) -> None:
        self._token_store = token_store
        self._project_id = project_id or _env_or_raise("GCP_PROJECT_ID")
        self._dataset_id = dataset_id
        self._client = SpotifyClient(token_store)
        kwargs = loader_kwargs or {}
        self._loader = BigQueryLoader(self._project_id, self._dataset_id, **kwargs)

    def run(self) -> IngestionRun:
        run_id = str(uuid.uuid4())
        started_at = datetime.utcnow()
        run = IngestionRun(run_id=run_id, started_at=started_at, status="running")

        try:
            items = self._client.get_recently_played()
            rows_ingested = self._loader.upsert_streaming_history(items)

            track_ids = {i.track_id for i in items if i.track_id}
            missing = self._loader.get_track_ids_missing_features(track_ids)
            have_features = track_ids - missing
            features = find_tracks_needing_features(
                items, self._client, existing_feature_ids=have_features
            )
            rows_enriched = self._loader.upsert_track_features(features)

            finished_at = datetime.utcnow()
            run.rows_ingested = rows_ingested
            run.rows_enriched = rows_enriched
            run.finished_at = finished_at
            run.duration_seconds = (finished_at - started_at).total_seconds()
            run.status = "success"
        except (SpotifyClientError, BigQueryLoaderError, ValueError) as e:
            finished_at = datetime.utcnow()
            run.finished_at = finished_at
            run.duration_seconds = (finished_at - started_at).total_seconds()
            run.status = "failed"
            run.error_message = str(e)
            self._loader.write_ingestion_run(run)
            raise

        self._loader.write_ingestion_run(run)
        return run


def main(event: dict[str, Any] | None = None, context: Any = None) -> str:
    refresh_token = _env_or_raise("SPOTIFY_REFRESH_TOKEN")
    token_store = _build_token_store()
    token_store.set_refresh_token(refresh_token)

    ingestor = Ingestor(token_store=token_store)
    run = ingestor.run()
    return f"Ingested {run.rows_ingested} rows, enriched {run.rows_enriched}, status={run.status}"

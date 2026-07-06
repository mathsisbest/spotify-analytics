from __future__ import annotations

from datetime import datetime
from typing import Any

from google.cloud import bigquery

from spotify_analytics.models import (
    IngestionRun,
    StreamingHistoryItem,
    TrackFeatures,
)


class BigQueryLoaderError(Exception):
    pass


def _maybe_isoformat(val: datetime | str | None) -> str | None:
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.isoformat()
    return str(val)


class BigQueryLoader:
    def __init__(
        self,
        project_id: str,
        dataset_id: str = "raw",
        client: bigquery.Client | None = None,
    ) -> None:
        self._project_id = project_id
        self._dataset_id = dataset_id
        self._client = client or bigquery.Client(project=project_id)

    def _table_ref(self, table: str) -> str:
        return f"{self._project_id}.{self._dataset_id}.{table}"

    def upsert_streaming_history(self, items: list[StreamingHistoryItem]) -> int:
        if not items:
            return 0
        rows: list[dict[str, Any]] = []
        for item in items:
            rows.append(
                {
                    "track_id": item.track_id,
                    "played_at": _maybe_isoformat(item.played_at),
                    "track_name": item.track_name,
                    "artist_id": item.artist_id,
                    "artist_name": item.artist_name,
                    "artist_ids": item.artist_ids,
                    "artist_names": item.artist_names,
                    "album_name": item.album_name,
                    "album_id": item.album_id,
                    "duration_ms": item.duration_ms,
                    "context": item.context,
                    "loaded_at": datetime.utcnow().isoformat(),
                }
            )
        table = self._table_ref("streaming_history")
        errors = self._client.insert_rows_json(table, rows)
        if errors:
            raise BigQueryLoaderError(f"Insert errors: {errors}")
        return len(rows)

    def upsert_track_features(self, features: list[TrackFeatures]) -> int:
        if not features:
            return 0
        rows: list[dict[str, Any]] = []
        for feat in features:
            rows.append(
                {
                    "track_id": feat.track_id,
                    "danceability": feat.danceability,
                    "energy": feat.energy,
                    "key": feat.key,
                    "loudness": feat.loudness,
                    "mode": feat.mode,
                    "speechiness": feat.speechiness,
                    "acousticness": feat.acousticness,
                    "instrumentalness": feat.instrumentalness,
                    "liveness": feat.liveness,
                    "valence": feat.valence,
                    "tempo": feat.tempo,
                    "time_signature": feat.time_signature,
                    "duration_ms": feat.duration_ms,
                    "fetched_at": _maybe_isoformat(feat.fetched_at),
                }
            )
        table = self._table_ref("track_features")
        errors = self._client.insert_rows_json(table, rows)
        if errors:
            raise BigQueryLoaderError(f"Insert errors: {errors}")
        return len(rows)

    def write_ingestion_run(self, run: IngestionRun) -> None:
        row = {
            "run_id": run.run_id,
            "started_at": _maybe_isoformat(run.started_at),
            "finished_at": run.finished_at.isoformat() if run.finished_at else None,
            "rows_ingested": run.rows_ingested,
            "rows_enriched": run.rows_enriched,
            "status": run.status,
            "error_message": run.error_message,
            "duration_seconds": run.duration_seconds,
        }
        table = self._table_ref("ingestion_runs")
        errors = self._client.insert_rows_json(table, [row])
        if errors:
            raise BigQueryLoaderError(f"Insert errors: {errors}")

    def get_recent_track_ids(self, limit: int = 100) -> set[str]:
        query = f"""
            SELECT DISTINCT track_id
            FROM `{self._table_ref("streaming_history")}`
            ORDER BY MAX(played_at) DESC
            LIMIT @limit
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("limit", "INT64", limit),
            ]
        )
        results = self._client.query(query, job_config=job_config)
        return {row.track_id for row in results}

    def get_track_ids_missing_features(self, track_ids: set[str]) -> set[str]:
        if not track_ids:
            return set()
        quoted = [f"'{tid}'" for tid in track_ids]
        query = f"""
            SELECT DISTINCT track_id
            FROM `{self._table_ref("track_features")}`
            WHERE track_id IN ({",".join(quoted)})
        """
        results = self._client.query(query)
        existing = {row.track_id for row in results}
        return track_ids - existing

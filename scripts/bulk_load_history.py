"""
One-time script to load a Spotify extended streaming history JSON export into BigQuery.

Usage:
    python scripts/bulk_load_history.py \\
        --file ~/Downloads/Spotify Extended Streaming History/StreamingHistory*.json \\
        --project my-project \\
        --dataset raw
"""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

from google.cloud import bigquery


def transform_record(record: dict[str, object]) -> dict[str, object]:
    uri = record.get("spotify_track_uri", "")
    track_id = uri.split(":")[-1] if isinstance(uri, str) and uri else record.get("track_id", "")
    return {
        "track_id": track_id,
        "track_name": record.get("trackName") or record.get("track_name", ""),
        "artist_name": record.get("artistName") or record.get("artist_name", ""),
        "album_name": record.get("albumName") or record.get("album_name", ""),
        "played_at": record.get("ts") or record.get("played_at", ""),
        "duration_ms": record.get("msPlayed") or record.get("ms_played", 0),
        "loaded_at": datetime.utcnow().isoformat(),
    }


def load_file(
    client: bigquery.Client,
    file_path: str,
    dataset_id: str,
    table_id: str = "streaming_history",
) -> int:
    path = Path(file_path)
    records = json.loads(path.read_text())
    if isinstance(records, dict):
        records = records.get("items", records)

    transformed = [transform_record(r) for r in records]
    table_ref = f"{client.project}.{dataset_id}.{table_id}"

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        autodetect=True,
    )

    job = client.load_table_from_json(transformed, table_ref, job_config=job_config)
    job.result()
    return len(transformed)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Load Spotify extended streaming history into BigQuery",
    )
    parser.add_argument("--file", required=True, help="Path to the streaming history JSON file")
    parser.add_argument("--project", required=True, help="GCP project ID")
    parser.add_argument("--dataset", default="raw", help="BigQuery dataset (default: raw)")
    args = parser.parse_args()

    client = bigquery.Client(project=args.project)
    start = time.time()
    row_count = load_file(client, args.file, args.dataset)
    elapsed = time.time() - start

    print(f"Loaded {row_count} rows in {elapsed:.2f}s")


if __name__ == "__main__":
    main()

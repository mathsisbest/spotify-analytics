import json
from typing import Any

from pydantic import BaseModel, Field


class ExtendedStreamingHistoryItem(BaseModel):
    ts: str = Field(description="Timestamp in ISO 8601 UTC format")
    ms_played: int = Field(description="Duration played in milliseconds", ge=0)
    master_metadata_track_name: str | None = Field(default=None, description="Track title")
    master_metadata_album_artist_name: str | None = Field(default=None, description="Artist name")
    master_metadata_album_album_name: str | None = Field(default=None, description="Album name")
    spotify_track_uri: str | None = Field(default=None, description="Spotify Track URI")
    reason_start: str | None = Field(default=None, description="Playback start reason")
    reason_end: str | None = Field(default=None, description="Playback end reason")
    shuffle: bool | None = Field(default=None, description="Shuffle mode status")
    skipped: bool | None = Field(default=None, description="Track skipped flag")


def parse_extended_history_json(json_content: str) -> list[dict[str, Any]]:
    try:
        raw_data = json.loads(json_content)
    except Exception:
        return []
    if not isinstance(raw_data, list):
        return []

    parsed: list[dict[str, Any]] = []
    for item in raw_data:
        if not isinstance(item, dict):
            continue
        try:
            record = ExtendedStreamingHistoryItem(**item)
            if record.master_metadata_track_name and record.master_metadata_album_artist_name:
                parsed.append(record.model_dump())
        except Exception:
            continue
    return parsed

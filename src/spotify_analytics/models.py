from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Artist(BaseModel):
    id: str
    name: str
    genres: list[str] = Field(default_factory=list)
    popularity: int = 0
    followers_total: int = 0
    href: str = ""


class Track(BaseModel):
    id: str
    name: str
    artists: list[Artist] = Field(default_factory=list)
    duration_ms: int = 0
    popularity: int = 0
    album_name: str = ""
    album_release_date: str = ""
    href: str = ""


class TrackFeatures(BaseModel):
    track_id: str
    danceability: float = 0.0
    energy: float = 0.0
    key: int = -1
    loudness: float = -60.0
    mode: int = 0
    speechiness: float = 0.0
    acousticness: float = 0.0
    instrumentalness: float = 0.0
    liveness: float = 0.0
    valence: float = 0.0
    tempo: float = 0.0
    time_signature: int = 4
    duration_ms: int = 0
    fetched_at: datetime = Field(default_factory=datetime.utcnow)


class StreamingHistoryItem(BaseModel):
    track_id: str
    played_at: str | datetime
    track_name: str = ""
    artist_id: str = ""
    artist_name: str = ""
    artist_ids: list[str] = Field(default_factory=list)
    artist_names: list[str] = Field(default_factory=list)
    album_name: str = ""
    album_id: str = ""
    duration_ms: int = 0
    context: str | None = None


class IngestionRun(BaseModel):
    run_id: str
    started_at: datetime
    finished_at: datetime | None = None
    rows_ingested: int = 0
    rows_enriched: int = 0
    status: str = "running"
    error_message: str | None = None
    duration_seconds: float | None = None


class SpotifyTokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
    refresh_token: str | None = None
    scope: str = ""


class SpotifyRecentlyPlayedResponse(BaseModel):
    items: list[dict[str, Any]] = Field(default_factory=list)
    next: str | None = None
    cursors: dict[str, str] = Field(default_factory=dict)
    limit: int = 20
    href: str = ""

from datetime import datetime

import pytest
from pydantic import ValidationError

from spotify_analytics.models import (
    Artist,
    IngestionRun,
    SpotifyRecentlyPlayedResponse,
    SpotifyTokenResponse,
    StreamingHistoryItem,
    Track,
    TrackFeatures,
)


class TestArtistModel:
    def test_minimal(self) -> None:
        a = Artist(id="abc", name="Test Artist")
        assert a.genres == []
        assert a.popularity == 0
        assert a.followers_total == 0

    def test_full(self) -> None:
        a = Artist(
            id="abc",
            name="Test Artist",
            genres=["rock", "pop"],
            popularity=75,
            followers_total=1_000_000,
        )
        assert a.genres == ["rock", "pop"]
        assert a.popularity == 75

    def test_missing_id_raises(self) -> None:
        with pytest.raises(ValidationError):
            Artist(name="No ID")  # type: ignore[call-arg]

    def test_empty_genres_allowed(self) -> None:
        a = Artist(id="x", name="X", genres=[])
        assert a.genres == []


class TestTrackModel:
    def test_minimal(self) -> None:
        t = Track(id="t1", name="Song")
        assert t.artists == []
        assert t.duration_ms == 0
        assert t.popularity == 0

    def test_with_artists(self) -> None:
        artist = Artist(id="a1", name="Artist One")
        t = Track(id="t1", name="Song", artists=[artist])
        assert len(t.artists) == 1
        assert t.artists[0].name == "Artist One"

    def test_adversarial_empty_id(self) -> None:
        t = Track(id="", name="Empty ID")
        assert t.id == ""


class TestTrackFeaturesModel:
    def test_defaults(self) -> None:
        f = TrackFeatures(track_id="t1")
        assert f.danceability == 0.0
        assert f.energy == 0.0
        assert f.key == -1
        assert f.loudness == -60.0
        assert f.tempo == 0.0
        assert isinstance(f.fetched_at, datetime)

    def test_all_fields(self) -> None:
        f = TrackFeatures(
            track_id="t1",
            danceability=0.8,
            energy=0.9,
            key=5,
            loudness=-5.0,
            mode=1,
            speechiness=0.1,
            acousticness=0.2,
            instrumentalness=0.0,
            liveness=0.3,
            valence=0.7,
            tempo=120.0,
            time_signature=4,
            duration_ms=200000,
        )
        assert f.danceability == 0.8
        assert f.key == 5
        assert f.tempo == 120.0

    def test_adversarial_extreme_values(self) -> None:
        f = TrackFeatures(
            track_id="t1",
            danceability=-1.0,
            energy=2.0,
            key=11,
            loudness=0.0,
        )
        assert f.danceability == -1.0

    def test_missing_track_id_raises(self) -> None:
        with pytest.raises(ValidationError):
            TrackFeatures()  # type: ignore[call-arg]

    def test_fetched_at_default_is_datetime(self) -> None:
        f = TrackFeatures(track_id="t1")
        assert isinstance(f.fetched_at, datetime)


class TestStreamingHistoryItemModel:
    def test_minimal(self) -> None:
        item = StreamingHistoryItem(track_id="t1", played_at="2024-01-01T00:00:00")
        assert item.artist_names == []
        assert item.context is None

    def test_with_context(self) -> None:
        item = StreamingHistoryItem(
            track_id="t1",
            played_at="2024-01-01T00:00:00",
            track_name="Test Track",
            artist_names=["Artist A"],
            context="spotify:playlist:abc123",
        )
        assert item.context == "spotify:playlist:abc123"

    def test_context_none_by_default(self) -> None:
        item = StreamingHistoryItem(track_id="t1", played_at="2024-01-01T00:00:00")
        assert item.context is None

    def test_missing_played_at_raises(self) -> None:
        with pytest.raises(ValidationError):
            StreamingHistoryItem(track_id="t1")  # type: ignore[call-arg]


class TestIngestionRunModel:
    def test_defaults(self) -> None:
        now = datetime.utcnow()
        run = IngestionRun(run_id="r1", started_at=now)
        assert run.status == "running"
        assert run.rows_ingested == 0
        assert run.rows_enriched == 0
        assert run.error_message is None
        assert run.finished_at is None
        assert run.duration_seconds is None

    def test_full(self) -> None:
        now = datetime.utcnow()
        run = IngestionRun(
            run_id="r1",
            started_at=now,
            finished_at=now,
            rows_ingested=10,
            rows_enriched=5,
            status="success",
            duration_seconds=1.5,
        )
        assert run.status == "success"
        assert run.duration_seconds == 1.5

    def test_failed_state(self) -> None:
        now = datetime.utcnow()
        run = IngestionRun(
            run_id="r1",
            started_at=now,
            status="failed",
            error_message="Something broke",
        )
        assert run.status == "failed"
        assert run.error_message == "Something broke"


class TestSpotifyTokenResponseModel:
    def test_minimal(self) -> None:
        t = SpotifyTokenResponse(access_token="tok")
        assert t.token_type == "Bearer"
        assert t.expires_in == 3600
        assert t.refresh_token is None

    def test_with_refresh(self) -> None:
        t = SpotifyTokenResponse(access_token="tok", refresh_token="rtok")
        assert t.refresh_token == "rtok"

    def test_adversarial_zero_expires(self) -> None:
        t = SpotifyTokenResponse(access_token="tok", expires_in=0)
        assert t.expires_in == 0


class TestSpotifyRecentlyPlayedResponseModel:
    def test_defaults(self) -> None:
        r = SpotifyRecentlyPlayedResponse()
        assert r.items == []
        assert r.next is None
        assert r.cursors == {}
        assert r.limit == 20

    def test_with_items(self) -> None:
        r = SpotifyRecentlyPlayedResponse(items=[{"track": {"id": "t1"}}], limit=50)
        assert len(r.items) == 1
        assert r.limit == 50

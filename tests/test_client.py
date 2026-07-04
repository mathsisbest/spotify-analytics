from unittest.mock import Mock, call, patch

import pytest
import requests
from spotify_analytics.auth import TokenStore
from spotify_analytics.client import (
    RateLimitError,
    SpotifyClient,
    SpotifyClientError,
)
from spotify_analytics.models import (
    Artist,
    Track,
    TrackFeatures,
)


@pytest.fixture
def token_store() -> TokenStore:
    store = TokenStore(client_id="cid", client_secret="csec")
    store.set_tokens("valid_tok", 3600, "rtok")
    return store


@pytest.fixture
def client(token_store: TokenStore) -> SpotifyClient:
    return SpotifyClient(token_store)


def _mock_response(status: int, json_data: object) -> Mock:
    resp = Mock(spec=requests.Response)
    resp.status_code = status
    resp.json.return_value = json_data
    resp.headers = {}
    return resp


class TestClientInit:
    def test_headers_uses_valid_token(self, client: SpotifyClient) -> None:
        headers = client._headers()
        assert headers["Authorization"] == "Bearer valid_tok"


class TestClientRequest:
    def test_successful_request(self, client: SpotifyClient) -> None:
        mock_resp = _mock_response(200, {"key": "value"})
        with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
            result = client._request("GET", "https://api.spotify.com/v1/me")

        assert result == {"key": "value"}
        mock_req.assert_called_once()

    def test_rate_limit_raises(self, client: SpotifyClient) -> None:
        mock_resp = _mock_response(429, {})
        mock_resp.headers = {"Retry-After": "30"}
        mock_resp.text = "Rate limited"

        with (
            patch.object(client._session, "request", return_value=mock_resp),
            pytest.raises(RateLimitError) as exc,
        ):
            client._request("GET", "https://api.spotify.com/v1/me")

        assert exc.value.retry_after == 30

    def test_rate_limit_default_retry(self, client: SpotifyClient) -> None:
        mock_resp = _mock_response(429, {})
        mock_resp.headers = {}
        mock_resp.text = "Rate limited"

        with (
            patch.object(client._session, "request", return_value=mock_resp),
            pytest.raises(RateLimitError) as exc,
        ):
            client._request("GET", "https://api.spotify.com/v1/me")

        assert exc.value.retry_after == 60

    def test_unauthorized_auto_refreshes(
        self, client: SpotifyClient, token_store: TokenStore
    ) -> None:
        mock_401 = _mock_response(401, {"error": "Unauthorized"})
        mock_200 = _mock_response(200, {"key": "value"})
        mock_refresh = _mock_response(200, {"access_token": "new_tok", "expires_in": 3600})

        with (
            patch.object(client._session, "request", side_effect=[mock_401, mock_200]) as mock_req,
            patch("spotify_analytics.client.requests.post", return_value=mock_refresh),
        ):
            result = client._request("GET", "https://api.spotify.com/v1/me")

        assert result == {"key": "value"}
        mock_req.assert_has_calls(
            [
                call(
                    "GET",
                    "https://api.spotify.com/v1/me",
                    headers={"Authorization": "Bearer valid_tok"},
                    timeout=30,
                ),
                call(
                    "GET",
                    "https://api.spotify.com/v1/me",
                    headers={"Authorization": "Bearer new_tok"},
                    timeout=30,
                ),
            ]
        )

    def test_unauthorized_twice_still_raises(self, client: SpotifyClient) -> None:
        mock_401 = _mock_response(401, {"error": "Unauthorized"})
        mock_refresh = _mock_response(200, {"access_token": "new_tok", "expires_in": 3600})

        with (
            patch.object(client._session, "request", return_value=mock_401),
            patch("spotify_analytics.client.requests.post", return_value=mock_refresh),
            pytest.raises(SpotifyClientError, match="API error 401"),
        ):
            client._request("GET", "https://api.spotify.com/v1/me")

    def test_generic_api_error(self, client: SpotifyClient) -> None:
        mock_resp = _mock_response(500, {})
        mock_resp.text = "Internal server error"

        with (
            patch.object(client._session, "request", return_value=mock_resp),
            pytest.raises(SpotifyClientError, match="API error 500"),
        ):
            client._request("GET", "https://api.spotify.com/v1/me")

    def test_network_error(self, client: SpotifyClient) -> None:
        err = requests.ConnectionError("no route to host")
        with (
            patch.object(client._session, "request", side_effect=err),
            pytest.raises(requests.ConnectionError),
        ):
            client._request("GET", "https://api.spotify.com/v1/me")


class TestClientGetRecentlyPlayed:
    def test_empty_response(self, client: SpotifyClient) -> None:
        mock_resp = _mock_response(200, {"items": [], "next": None})
        with patch.object(client._session, "request", return_value=mock_resp):
            items = client.get_recently_played()

        assert items == []

    def test_single_item(self, client: SpotifyClient) -> None:
        raw = {
            "items": [
                {
                    "track": {
                        "id": "t1",
                        "name": "Test Track",
                        "artists": [{"name": "Artist A"}, {"name": "Artist B"}],
                        "album": {"name": "Album X"},
                        "duration_ms": 200000,
                    },
                    "played_at": "2024-01-01T12:00:00Z",
                    "context": {"uri": "spotify:playlist:abc"},
                }
            ]
        }
        mock_resp = _mock_response(200, raw)
        with patch.object(client._session, "request", return_value=mock_resp):
            items = client.get_recently_played()

        assert len(items) == 1
        assert items[0].track_id == "t1"
        assert items[0].track_name == "Test Track"
        assert items[0].artist_names == ["Artist A", "Artist B"]
        assert items[0].context == "spotify:playlist:abc"
        assert items[0].duration_ms == 200000

    def test_no_context(self, client: SpotifyClient) -> None:
        raw = {
            "items": [
                {
                    "track": {
                        "id": "t1",
                        "name": "Test",
                        "artists": [{"name": "A"}],
                        "album": {"name": "B"},
                        "duration_ms": 1000,
                    },
                    "played_at": "2024-01-01T12:00:00Z",
                }
            ]
        }
        mock_resp = _mock_response(200, raw)
        with patch.object(client._session, "request", return_value=mock_resp):
            items = client.get_recently_played()

        assert items[0].context is None

    def test_passes_after_timestamp(self, client: SpotifyClient) -> None:
        mock_resp = _mock_response(200, {"items": []})
        with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
            client.get_recently_played(after=1234567890)

        call_args = mock_req.call_args[1]
        assert call_args["params"]["after"] == 1234567890
        assert call_args["params"]["limit"] == 50

    def test_malformed_item_skipped(self, client: SpotifyClient) -> None:
        raw = {"items": [{"not_a_track": True}]}
        mock_resp = _mock_response(200, raw)
        with patch.object(client._session, "request", return_value=mock_resp):
            items = client.get_recently_played()

        assert len(items) == 0


class TestClientGetTrack:
    def test_success(self, client: SpotifyClient) -> None:
        raw = {
            "id": "t1",
            "name": "Test Track",
            "artists": [
                {"id": "a1", "name": "Artist One", "href": "https://api.spotify.com/v1/artists/a1"},
                {"id": "a2", "name": "Artist Two", "href": ""},
            ],
            "duration_ms": 180000,
            "popularity": 50,
            "album": {"name": "Album", "release_date": "2024-01-01"},
        }
        mock_resp = _mock_response(200, raw)
        with patch.object(client._session, "request", return_value=mock_resp):
            track = client.get_track("t1")

        assert isinstance(track, Track)
        assert track.id == "t1"
        assert track.name == "Test Track"
        assert len(track.artists) == 2
        assert track.artists[0].name == "Artist One"
        assert track.popularity == 50

    def test_adversarial_missing_album(self, client: SpotifyClient) -> None:
        raw = {"id": "t1", "name": "No Album Track", "artists": []}
        mock_resp = _mock_response(200, raw)
        with patch.object(client._session, "request", return_value=mock_resp):
            track = client.get_track("t1")

        assert track.album_name == ""
        assert track.album_release_date == ""


class TestClientGetArtist:
    def test_success(self, client: SpotifyClient) -> None:
        raw = {
            "id": "a1",
            "name": "Test Artist",
            "genres": ["rock", "indie"],
            "popularity": 70,
            "followers": {"total": 500000},
        }
        mock_resp = _mock_response(200, raw)
        with patch.object(client._session, "request", return_value=mock_resp):
            artist = client.get_artist("a1")

        assert isinstance(artist, Artist)
        assert artist.id == "a1"
        assert artist.genres == ["rock", "indie"]
        assert artist.popularity == 70
        assert artist.followers_total == 500000

    def test_no_followers_field(self, client: SpotifyClient) -> None:
        raw = {"id": "a1", "name": "Artist", "genres": []}
        mock_resp = _mock_response(200, raw)
        with patch.object(client._session, "request", return_value=mock_resp):
            artist = client.get_artist("a1")

        assert artist.followers_total == 0


class TestClientGetAudioFeatures:
    def test_success(self, client: SpotifyClient) -> None:
        raw = {
            "id": "t1",
            "danceability": 0.8,
            "energy": 0.9,
            "key": 5,
            "loudness": -5.0,
            "mode": 1,
            "speechiness": 0.05,
            "acousticness": 0.1,
            "instrumentalness": 0.0,
            "liveness": 0.2,
            "valence": 0.7,
            "tempo": 120.0,
            "time_signature": 4,
            "duration_ms": 200000,
        }
        mock_resp = _mock_response(200, raw)
        with patch.object(client._session, "request", return_value=mock_resp):
            features = client.get_audio_features("t1")

        assert isinstance(features, TrackFeatures)
        assert features.track_id == "t1"
        assert features.danceability == 0.8
        assert features.energy == 0.9
        assert features.tempo == 120.0

    def test_error_response_returns_none(self, client: SpotifyClient) -> None:
        mock_resp = _mock_response(200, {"error": "track not found"})
        with patch.object(client._session, "request", return_value=mock_resp):
            features = client.get_audio_features("invalid")
        assert features is None


class TestClientGetSeveralAudioFeatures:
    def test_success(self, client: SpotifyClient) -> None:
        raw = {
            "audio_features": [
                {"id": "t1", "danceability": 0.5, "energy": 0.5, "tempo": 100.0},
                {"id": "t2", "danceability": 0.8, "energy": 0.9, "tempo": 120.0},
            ]
        }
        mock_resp = _mock_response(200, raw)
        with patch.object(client._session, "request", return_value=mock_resp):
            features = client.get_several_audio_features(["t1", "t2"])

        assert len(features) == 2
        assert features[0].track_id == "t1"
        assert features[1].track_id == "t2"

    def test_empty_input(self, client: SpotifyClient) -> None:
        features = client.get_several_audio_features([])
        assert features == []

    def test_null_items_skipped(self, client: SpotifyClient) -> None:
        raw = {"audio_features": [None, {"id": "t2", "danceability": 0.5}]}
        mock_resp = _mock_response(200, raw)
        with patch.object(client._session, "request", return_value=mock_resp):
            features = client.get_several_audio_features(["t1", "t2"])

        assert len(features) == 1
        assert features[0].track_id == "t2"


class TestClientClose:
    def test_close(self, client: SpotifyClient) -> None:
        with patch.object(client._session, "close") as mock_close:
            client.close()
        mock_close.assert_called_once()

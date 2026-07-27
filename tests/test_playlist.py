from unittest.mock import Mock, patch

import pytest
import requests

from spotify_analytics.auth import TokenStore
from spotify_analytics.client import SpotifyClient


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


class TestPlaylistAPI:
    def test_get_current_user_id(self, client: SpotifyClient) -> None:
        mock_resp = _mock_response(200, {"id": "user123"})
        with patch.object(client._session, "request", return_value=mock_resp):
            uid = client.get_current_user_id()
        assert uid == "user123"

    def test_create_playlist(self, client: SpotifyClient) -> None:
        mock_resp = _mock_response(200, {"id": "playlist456"})
        with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
            pid = client.create_playlist(
                user_id="user123", name="My Playlist", description="Desc", public=False
            )
        assert pid == "playlist456"
        mock_req.assert_called_once_with(
            "POST",
            "https://api.spotify.com/v1/users/user123/playlists",
            headers={"Authorization": "Bearer valid_tok"},
            timeout=30,
            json={"name": "My Playlist", "description": "Desc", "public": False},
        )

    def test_add_tracks_to_playlist(self, client: SpotifyClient) -> None:
        mock_resp = _mock_response(201, {"snapshot_id": "snap789"})
        uris = ["spotify:track:t1", "spotify:track:t2"]
        with patch.object(client._session, "request", return_value=mock_resp) as mock_req:
            client.add_tracks_to_playlist("playlist456", uris)
        mock_req.assert_called_once_with(
            "POST",
            "https://api.spotify.com/v1/playlists/playlist456/tracks",
            headers={"Authorization": "Bearer valid_tok"},
            timeout=30,
            json={"uris": uris},
        )

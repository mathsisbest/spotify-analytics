from unittest.mock import Mock, patch

import pytest
import requests
from spotify_analytics.auth import (
    SpotifyAuthError,
    SpotifyTokenResponse,
    TokenStore,
    build_authorize_url,
)


@pytest.fixture
def store() -> TokenStore:
    return TokenStore(client_id="cid", client_secret="csec")


class TestTokenStoreInit:
    def test_no_tokens_initially(self, store: TokenStore) -> None:
        assert store.access_token is None
        assert store.get_refresh_token() is None
        assert store.is_expired() is True

    def test_clear_resets_state(self, store: TokenStore) -> None:
        store.set_tokens("tok", 3600, "rtok")
        store.clear()
        assert store.access_token is None
        assert store.get_refresh_token() is None


class TestTokenStoreSetAndGet:
    def test_set_tokens(self, store: TokenStore) -> None:
        store.set_tokens("access123", 3600, "refresh123")
        assert store.access_token == "access123"
        assert store.get_refresh_token() == "refresh123"
        assert store.is_expired() is False

    def test_access_token_near_expiry(self, store: TokenStore) -> None:
        store.set_tokens("access123", 30)  # 30 seconds from now
        assert store.access_token is None  # within 60s buffer so expired

    def test_set_refresh_token_only(self, store: TokenStore) -> None:
        store.set_refresh_token("rtok")
        assert store.get_refresh_token() == "rtok"
        assert store.access_token is None

    def test_negative_expires_in(self, store: TokenStore) -> None:
        store.set_tokens("tok", -1)
        assert store.access_token is None
        assert store.is_expired() is True


class TestTokenStoreEncodeCredentials:
    def test_encode_credentials(self, store: TokenStore) -> None:
        encoded = store._encode_credentials("cid", "csec")
        assert encoded == "Y2lkOmNzZWM="

    def test_encode_credentials_special_chars(self) -> None:
        store = TokenStore(client_id="a:b", client_secret="c/d")
        encoded = store._encode_credentials("a:b", "c/d")
        assert encoded == "YTpiOmMvZA=="


class TestTokenStoreExchangeCode:
    def test_successful_exchange(self, store: TokenStore) -> None:
        mock_resp = Mock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "access_token": "new_tok",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "new_rtok",
            "scope": "user-read-recently-played",
        }

        with patch("spotify_analytics.auth.requests.post", return_value=mock_resp):
            token = store.exchange_code("auth_code", "http://localhost/callback")

        assert isinstance(token, SpotifyTokenResponse)
        assert token.access_token == "new_tok"
        assert token.refresh_token == "new_rtok"
        assert store.access_token == "new_tok"
        assert store.get_refresh_token() == "new_rtok"

    def test_exchange_http_error(self, store: TokenStore) -> None:
        mock_resp = Mock(spec=requests.Response)
        mock_resp.status_code = 400
        mock_resp.text = "bad request"

        with (
            patch("spotify_analytics.auth.requests.post", return_value=mock_resp),
            pytest.raises(SpotifyAuthError, match="Token exchange failed"),
        ):
            store.exchange_code("code", "uri")

    def test_exchange_network_error(self, store: TokenStore) -> None:
        with (
            patch("spotify_analytics.auth.requests.post", side_effect=requests.ConnectionError),
            pytest.raises(requests.ConnectionError),
        ):
            store.exchange_code("code", "uri")


class TestTokenStoreRefresh:
    def test_refresh_no_token_raises(self, store: TokenStore) -> None:
        with pytest.raises(SpotifyAuthError, match="No refresh token"):
            store.refresh()

    def test_successful_refresh(self, store: TokenStore) -> None:
        store.set_refresh_token("old_rtok")
        mock_resp = Mock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "access_token": "refreshed_tok",
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": "user-read-recently-played",
        }

        with patch("spotify_analytics.auth.requests.post", return_value=mock_resp):
            token = store.refresh()

        assert token.access_token == "refreshed_tok"
        assert store.access_token == "refreshed_tok"
        assert store.get_refresh_token() == "old_rtok"

    def test_refresh_rotates_refresh_token(self, store: TokenStore) -> None:
        store.set_refresh_token("old_rtok")
        mock_resp = Mock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "access_token": "refreshed_tok",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "new_rtok",
        }

        with patch("spotify_analytics.auth.requests.post", return_value=mock_resp):
            store.refresh()

        assert store.get_refresh_token() == "new_rtok"

    def test_refresh_http_error(self, store: TokenStore) -> None:
        store.set_refresh_token("rtok")
        mock_resp = Mock(spec=requests.Response)
        mock_resp.status_code = 401
        mock_resp.text = "invalid refresh token"

        with (
            patch("spotify_analytics.auth.requests.post", return_value=mock_resp),
            pytest.raises(SpotifyAuthError, match="Token refresh failed"),
        ):
            store.refresh()


class TestTokenStoreGetValidToken:
    def test_returns_access_token_if_valid(self, store: TokenStore) -> None:
        store.set_tokens("valid_tok", 3600)
        token = store.get_valid_token()
        assert token == "valid_tok"

    def test_refreshes_if_expired(self, store: TokenStore) -> None:
        store.set_tokens("expired_tok", 0)
        store.set_refresh_token("rtok")

        mock_resp = Mock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "access_token": "new_tok",
            "expires_in": 3600,
        }

        with patch("spotify_analytics.auth.requests.post", return_value=mock_resp):
            token = store.get_valid_token()

        assert token == "new_tok"
        assert store.access_token == "new_tok"

    def test_no_tokens_raises(self, store: TokenStore) -> None:
        with pytest.raises(SpotifyAuthError, match="No access token and no refresh token"):
            store.get_valid_token()

    def test_expired_no_refresh_raises(self, store: TokenStore) -> None:
        store.set_tokens("tok", 0)
        with pytest.raises(SpotifyAuthError, match="No access token and no refresh token"):
            store.get_valid_token()


class TestBuildAuthorizeUrl:
    def test_basic_url(self) -> None:
        url = build_authorize_url("cid", "http://localhost/callback")
        assert "client_id=cid" in url
        assert "redirect_uri=http://localhost/callback" in url
        assert "response_type=code" in url
        assert "scope=user-read-recently-played" in url

    def test_custom_scope(self) -> None:
        url = build_authorize_url("cid", "http://localhost/callback", scope="user-top-read")
        assert "scope=user-top-read" in url

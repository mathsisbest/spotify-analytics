from __future__ import annotations

import base64
import time
from typing import Any

import requests

from spotify_analytics.models import SpotifyTokenResponse

TOKEN_URL = "https://accounts.spotify.com/api/token"
AUTH_URL = "https://accounts.spotify.com/authorize"


__all__ = [
    "SpotifyAuthError",
    "SpotifyTokenResponse",
    "TokenStore",
    "build_authorize_url",
]


class SpotifyAuthError(Exception):
    pass


class TokenStore:
    def __init__(self, client_id: str, client_secret: str) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._expires_at: float = 0.0

    @property
    def access_token(self) -> str | None:
        if self._access_token and time.time() < self._expires_at - 60:
            return self._access_token
        return None

    def set_tokens(
        self, access_token: str, expires_in: int, refresh_token: str | None = None
    ) -> None:
        self._access_token = access_token
        self._expires_at = time.time() + expires_in
        if refresh_token:
            self._refresh_token = refresh_token

    def set_refresh_token(self, refresh_token: str) -> None:
        self._refresh_token = refresh_token

    def get_refresh_token(self) -> str | None:
        return self._refresh_token

    def is_expired(self) -> bool:
        return time.time() >= self._expires_at - 60

    def clear(self) -> None:
        self._access_token = None
        self._refresh_token = None
        self._expires_at = 0.0

    @staticmethod
    def _encode_credentials(client_id: str, client_secret: str) -> str:
        raw = f"{client_id}:{client_secret}"
        return base64.b64encode(raw.encode()).decode()

    def exchange_code(self, code: str, redirect_uri: str) -> SpotifyTokenResponse:
        encoded = self._encode_credentials(self._client_id, self._client_secret)
        headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data: dict[str, str] = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        }
        resp = requests.post(TOKEN_URL, headers=headers, data=data, timeout=30)
        if resp.status_code != 200:
            raise SpotifyAuthError(f"Token exchange failed: {resp.status_code} {resp.text}")
        payload: dict[str, Any] = resp.json()
        token = SpotifyTokenResponse(**payload)
        self.set_tokens(token.access_token, token.expires_in, token.refresh_token)
        return token

    def refresh(self) -> SpotifyTokenResponse:
        if not self._refresh_token:
            raise SpotifyAuthError("No refresh token available")
        encoded = self._encode_credentials(self._client_id, self._client_secret)
        headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data: dict[str, str] = {
            "grant_type": "refresh_token",
            "refresh_token": self._refresh_token,
        }
        resp = requests.post(TOKEN_URL, headers=headers, data=data, timeout=30)
        if resp.status_code != 200:
            raise SpotifyAuthError(f"Token refresh failed: {resp.status_code} {resp.text}")
        payload = resp.json()
        token = SpotifyTokenResponse(**payload)
        new_refresh = token.refresh_token or self._refresh_token
        self.set_tokens(token.access_token, token.expires_in, new_refresh)
        if token.refresh_token:
            self._refresh_token = token.refresh_token
        return token

    def get_valid_token(self) -> str:
        cached = self.access_token
        if cached is not None:
            return cached
        if self._refresh_token:
            self.refresh()
            cached = self._access_token
            if cached is not None:
                return cached
        raise SpotifyAuthError("No access token and no refresh token")


def build_authorize_url(
    client_id: str, redirect_uri: str, scope: str = "user-read-recently-played"
) -> str:
    params = f"client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}"
    return f"{AUTH_URL}?{params}"

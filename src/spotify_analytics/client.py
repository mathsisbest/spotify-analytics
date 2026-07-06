from __future__ import annotations

from typing import Any

import requests

from spotify_analytics.auth import TokenStore
from spotify_analytics.models import (
    Artist,
    StreamingHistoryItem,
    Track,
    TrackFeatures,
)

BASE_URL = "https://api.spotify.com/v1"


class SpotifyClientError(Exception):
    pass


class RateLimitError(SpotifyClientError):
    def __init__(self, retry_after: int = 60) -> None:
        self.retry_after = retry_after
        super().__init__(f"Rate limited, retry after {retry_after}s")


class SpotifyClient:
    def __init__(self, token_store: TokenStore) -> None:
        self._token_store = token_store
        self._session = requests.Session()

    def _headers(self) -> dict[str, str]:
        token = self._token_store.get_valid_token()
        return {"Authorization": f"Bearer {token}"}

    def _request(self, method: str, url: str, **kwargs: Any) -> Any:
        resp = self._session.request(method, url, headers=self._headers(), timeout=30, **kwargs)
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", 60))
            raise RateLimitError(retry_after)
        if resp.status_code == 401:
            self._token_store.refresh()
            resp = self._session.request(method, url, headers=self._headers(), timeout=30, **kwargs)
        if resp.status_code != 200:
            raise SpotifyClientError(f"API error {resp.status_code}: {resp.text}")
        result: Any = resp.json()
        return result

    def get_recently_played(self, after: int | None = None) -> list[StreamingHistoryItem]:
        params: dict[str, str | int] = {"limit": 50}
        if after is not None:
            params["after"] = after

        data = self._request("GET", f"{BASE_URL}/me/player/recently-played", params=params)
        assert isinstance(data, dict)
        items: list[StreamingHistoryItem] = []
        for item in data.get("items", []):
            track_data = item.get("track", {})
            artists = track_data.get("artists", [])
            played_at = item.get("played_at", "")
            if not played_at:
                continue
            try:
                album_data = track_data.get("album", {})
                history_item = StreamingHistoryItem(
                    track_id=track_data.get("id", ""),
                    played_at=played_at,
                    track_name=track_data.get("name", ""),
                    artist_id=artists[0].get("id", "") if artists else "",
                    artist_name=artists[0].get("name", "") if artists else "",
                    artist_ids=[a.get("id", "") for a in artists],
                    artist_names=[a.get("name", "") for a in artists],
                    album_name=album_data.get("name", ""),
                    album_id=album_data.get("id", ""),
                    duration_ms=track_data.get("duration_ms", 0),
                    context=item.get("context", {}).get("uri") if item.get("context") else None,
                )
            except (ValueError, TypeError):
                continue
            items.append(history_item)
        return items

    def get_track(self, track_id: str) -> Track:
        data = self._request("GET", f"{BASE_URL}/tracks/{track_id}")
        assert isinstance(data, dict)
        artists = [
            Artist(
                id=a.get("id", ""),
                name=a.get("name", ""),
                href=a.get("href", ""),
            )
            for a in data.get("artists", [])
        ]
        return Track(
            id=data.get("id", ""),
            name=data.get("name", ""),
            artists=artists,
            duration_ms=data.get("duration_ms", 0),
            popularity=data.get("popularity", 0),
            album_name=data.get("album", {}).get("name", ""),
            album_release_date=data.get("album", {}).get("release_date", ""),
        )

    def get_artist(self, artist_id: str) -> Artist:
        data = self._request("GET", f"{BASE_URL}/artists/{artist_id}")
        assert isinstance(data, dict)
        return Artist(
            id=data.get("id", ""),
            name=data.get("name", ""),
            genres=data.get("genres", []),
            popularity=data.get("popularity", 0),
            followers_total=data.get("followers", {}).get("total", 0),
        )

    def get_audio_features(self, track_id: str) -> TrackFeatures | None:
        data = self._request("GET", f"{BASE_URL}/audio-features/{track_id}")
        if isinstance(data, dict) and data.get("error"):
            return None
        assert isinstance(data, dict)
        return TrackFeatures(
            track_id=data.get("id", track_id),
            danceability=data.get("danceability", 0.0),
            energy=data.get("energy", 0.0),
            key=data.get("key", -1),
            loudness=data.get("loudness", -60.0),
            mode=data.get("mode", 0),
            speechiness=data.get("speechiness", 0.0),
            acousticness=data.get("acousticness", 0.0),
            instrumentalness=data.get("instrumentalness", 0.0),
            liveness=data.get("liveness", 0.0),
            valence=data.get("valence", 0.0),
            tempo=data.get("tempo", 0.0),
            time_signature=data.get("time_signature", 4),
            duration_ms=data.get("duration_ms", 0),
        )

    def get_several_audio_features(self, track_ids: list[str]) -> list[TrackFeatures]:
        if not track_ids:
            return []
        ids = ",".join(track_ids)
        data = self._request("GET", f"{BASE_URL}/audio-features", params={"ids": ids})
        assert isinstance(data, dict)
        features_list = data.get("audio_features", [])
        result: list[TrackFeatures] = []
        for feat in features_list:
            if feat is None:
                continue
            result.append(
                TrackFeatures(
                    track_id=feat.get("id", ""),
                    danceability=feat.get("danceability", 0.0),
                    energy=feat.get("energy", 0.0),
                    key=feat.get("key", -1),
                    loudness=feat.get("loudness", -60.0),
                    mode=feat.get("mode", 0),
                    speechiness=feat.get("speechiness", 0.0),
                    acousticness=feat.get("acousticness", 0.0),
                    instrumentalness=feat.get("instrumentalness", 0.0),
                    liveness=feat.get("liveness", 0.0),
                    valence=feat.get("valence", 0.0),
                    tempo=feat.get("tempo", 0.0),
                    time_signature=feat.get("time_signature", 4),
                    duration_ms=feat.get("duration_ms", 0),
                )
            )
        return result

    def close(self) -> None:
        self._session.close()

from unittest.mock import patch

import pytest
from spotify_analytics.auth import TokenStore
from spotify_analytics.client import SpotifyClient
from spotify_analytics.enrich import (
    EnrichmentError,
    build_track_id_set,
    find_tracks_needing_features,
)
from spotify_analytics.models import StreamingHistoryItem, TrackFeatures


@pytest.fixture
def client() -> SpotifyClient:
    store = TokenStore(client_id="cid", client_secret="csec")
    store.set_tokens("tok", 3600)
    return SpotifyClient(store)


class TestBuildTrackIdSet:
    def test_extracts_ids(self) -> None:
        items = [
            StreamingHistoryItem(track_id="t1", played_at="2024-01-01T00:00:00Z"),
            StreamingHistoryItem(track_id="t2", played_at="2024-01-01T00:01:00Z"),
        ]
        ids = build_track_id_set(items)
        assert ids == {"t1", "t2"}

    def test_empty_ids(self) -> None:
        item = StreamingHistoryItem(track_id="", played_at="2024-01-01T00:00:00Z")
        ids = build_track_id_set([item])
        assert ids == set()

    def test_duplicates_deduplicated(self) -> None:
        items = [
            StreamingHistoryItem(track_id="t1", played_at="2024-01-01T00:00:00Z"),
            StreamingHistoryItem(track_id="t1", played_at="2024-01-01T00:01:00Z"),
        ]
        ids = build_track_id_set(items)
        assert ids == {"t1"}

    def test_empty_items(self) -> None:
        assert build_track_id_set([]) == set()


class TestFindTracksNeedingFeatures:
    def test_empty_items_returns_empty(self, client: SpotifyClient) -> None:
        result = find_tracks_needing_features([], client)
        assert result == []

    def test_all_tracks_have_existing_features(self, client: SpotifyClient) -> None:
        items = [
            StreamingHistoryItem(track_id="t1", played_at="2024-01-01T00:00:00Z"),
        ]
        result = find_tracks_needing_features(items, client, existing_feature_ids={"t1"})
        assert result == []

    def test_missing_features_fetched(self, client: SpotifyClient) -> None:
        items = [
            StreamingHistoryItem(track_id="t1", played_at="2024-01-01T00:00:00Z"),
        ]
        mock_features = [
            TrackFeatures(track_id="t1", danceability=0.5, energy=0.7),
        ]

        with patch.object(
            client, "get_several_audio_features", return_value=mock_features
        ) as mock_fetch:
            result = find_tracks_needing_features(items, client, existing_feature_ids=set())

        assert len(result) == 1
        assert result[0].track_id == "t1"
        assert result[0].danceability == 0.5
        mock_fetch.assert_called_once_with(["t1"])

    def test_skip_empty_track_ids(self, client: SpotifyClient) -> None:
        items = [
            StreamingHistoryItem(track_id="", played_at="2024-01-01T00:00:00Z"),
        ]
        valid_items = [i for i in items if i is not None and i.track_id]
        result = find_tracks_needing_features(valid_items, client)
        assert result == []

    def test_fetch_error_propagates(self, client: SpotifyClient) -> None:
        items = [
            StreamingHistoryItem(track_id="t1", played_at="2024-01-01T00:00:00Z"),
        ]

        with (
            patch.object(client, "get_several_audio_features", side_effect=Exception("API down")),
            pytest.raises(EnrichmentError, match="Failed to fetch audio features"),
        ):
            find_tracks_needing_features(items, client)

    def test_batch_size_respected(self, client: SpotifyClient) -> None:
        items = [
            StreamingHistoryItem(track_id=f"t{i}", played_at="2024-01-01T00:00:00Z")
            for i in range(150)
        ]

        batch1 = [TrackFeatures(track_id=f"t{i}") for i in range(100)]
        batch2 = [TrackFeatures(track_id=f"t{i}") for i in range(100, 150)]

        with patch.object(
            client, "get_several_audio_features", side_effect=[batch1, batch2]
        ) as mock_fetch:
            result = find_tracks_needing_features(items, client, existing_feature_ids=set())

        assert len(result) == 150
        assert mock_fetch.call_count == 2

    def test_partially_existing_features(self, client: SpotifyClient) -> None:
        items = [
            StreamingHistoryItem(track_id="t_exists", played_at="2024-01-01T00:00:00Z"),
            StreamingHistoryItem(track_id="t_new", played_at="2024-01-01T00:00:00Z"),
        ]
        mock_features = [
            TrackFeatures(track_id="t_new", danceability=0.3),
        ]

        with patch.object(
            client, "get_several_audio_features", return_value=mock_features
        ) as mock_fetch:
            result = find_tracks_needing_features(items, client, existing_feature_ids={"t_exists"})

        assert len(result) == 1
        assert result[0].track_id == "t_new"
        mock_fetch.assert_called_once_with(["t_new"])

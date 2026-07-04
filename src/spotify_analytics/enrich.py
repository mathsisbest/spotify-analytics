from __future__ import annotations

from spotify_analytics.client import SpotifyClient
from spotify_analytics.models import StreamingHistoryItem, TrackFeatures


class EnrichmentError(Exception):
    pass


def find_tracks_needing_features(
    items: list[StreamingHistoryItem],
    client: SpotifyClient,
    existing_feature_ids: set[str] | None = None,
) -> list[TrackFeatures]:
    if not items:
        return []

    track_ids: set[str] = set()
    for item in items:
        if item.track_id:
            track_ids.add(item.track_id)

    if existing_feature_ids:
        track_ids = track_ids - existing_feature_ids

    if not track_ids:
        return []

    features: list[TrackFeatures] = []
    track_ids_list = list(track_ids)
    batch_size = 100

    for i in range(0, len(track_ids_list), batch_size):
        batch = track_ids_list[i : i + batch_size]
        try:
            batch_features = client.get_several_audio_features(batch)
            features.extend(batch_features)
        except Exception as e:
            raise EnrichmentError(f"Failed to fetch audio features for batch: {e}") from e

    return features


def build_track_id_set(items: list[StreamingHistoryItem]) -> set[str]:
    return {item.track_id for item in items if item.track_id}

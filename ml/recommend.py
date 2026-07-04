"""
Next-track recommender.

Generates track recommendations based on:
  - Current listening context (recent tracks, time of day)
  - Audio-feature similarity (cluster membership)
  - Recency-weighted popularity
"""

from typing import Any


def recommend_for_user(
    recent_track_ids: list[str],
    n: int = 10,
) -> list[dict[str, Any]]:
    return []

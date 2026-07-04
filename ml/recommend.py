from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

_FEATURE_COLS = [
    "danceability",
    "energy",
    "valence",
    "tempo",
    "loudness",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "key",
    "mode",
]


def _generate_catalog(n_tracks: int = 500) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    return pd.DataFrame(
        {
            "track_id": [f"synth_track_{i:04d}" for i in range(n_tracks)],
            "danceability": rng.uniform(0.0, 1.0, n_tracks),
            "energy": rng.uniform(0.0, 1.0, n_tracks),
            "valence": rng.uniform(0.0, 1.0, n_tracks),
            "tempo": rng.uniform(60.0, 200.0, n_tracks),
            "loudness": rng.uniform(-60.0, 0.0, n_tracks),
            "speechiness": rng.uniform(0.0, 1.0, n_tracks),
            "acousticness": rng.uniform(0.0, 1.0, n_tracks),
            "instrumentalness": rng.uniform(0.0, 1.0, n_tracks),
            "liveness": rng.uniform(0.0, 1.0, n_tracks),
            "key": rng.integers(0, 12, n_tracks),
            "mode": rng.integers(0, 2, n_tracks),
        }
    )


def _fit_clusters(
    catalog: pd.DataFrame,
    n_clusters: int = 8,
) -> tuple[pd.DataFrame, KMeans, StandardScaler]:
    scaler = StandardScaler()
    scaled = scaler.fit_transform(catalog[_FEATURE_COLS])
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
    catalog = catalog.copy()
    catalog["cluster_id"] = km.fit_predict(scaled)
    return catalog, km, scaler


def _candidates_from_other_clusters(
    catalog: pd.DataFrame,
    n: int,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for cid in sorted(catalog["cluster_id"].unique()):
        cluster_tracks = catalog[catalog["cluster_id"] == cid]
        if not cluster_tracks.empty:
            results.append(
                {
                    "track_id": str(cluster_tracks.iloc[0]["track_id"]),
                    "score": round(1.0 - cid * 0.01, 4),
                    "cluster_id": int(cid),
                }
            )
    return results[:n] if n > 0 else []


def recommend_for_user(
    recent_track_ids: list[str],
    n: int = 10,
) -> list[dict[str, Any]]:
    if n <= 0:
        return []

    catalog = _generate_catalog()
    catalog, km, scaler = _fit_clusters(catalog)

    recent_in_catalog = catalog[catalog["track_id"].isin(recent_track_ids)]

    if recent_in_catalog.empty:
        return _candidates_from_other_clusters(catalog, n)

    target_cluster = int(recent_in_catalog["cluster_id"].mode().iloc[0])

    candidates = catalog[
        (catalog["cluster_id"] == target_cluster) & (~catalog["track_id"].isin(recent_track_ids))
    ].copy()

    if candidates.empty:
        return _candidates_from_other_clusters(catalog, n)

    recent_scaled = scaler.transform(recent_in_catalog[_FEATURE_COLS])
    centroid = recent_scaled.mean(axis=0)

    candidate_scaled = scaler.transform(candidates[_FEATURE_COLS])
    distances = np.linalg.norm(candidate_scaled - centroid, axis=1)
    max_dist = float(distances.max()) if distances.max() > 0 else 1.0
    scores = list(1.0 - (distances / max_dist) + 0.1)

    candidates = candidates.copy()
    candidates["_score"] = scores
    candidates = candidates.sort_values("_score", ascending=False)

    results: list[dict[str, Any]] = []
    for _, row in candidates.head(n).iterrows():
        results.append(
            {
                "track_id": str(row["track_id"]),
                "score": round(float(row["_score"]), 4),
                "cluster_id": int(row["cluster_id"]),
            }
        )

    return results

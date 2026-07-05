"""
Training pipeline for Spotify analytics ML models.

Usage:
    python -m ml.train --mode cluster
    python -m ml.train --mode predict
    python -m ml.train --mode forecast
"""

import argparse
from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, silhouette_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from ml.features import build_cluster_features, build_skip_prediction_features
from ml.forecast import forecast_listening_volume

CLUSTER_FEATURES = [
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

PREDICT_FEATURES = [
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
    "hour_of_day",
    "day_of_week",
    "is_weekend",
    "session_position",
    "artist_play_count_30d",
    "track_play_count_30d",
]


def train_cluster() -> dict[str, Any]:
    data = build_cluster_features()
    df = pd.DataFrame(data)
    x = df[CLUSTER_FEATURES].values

    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x)

    clustering = DBSCAN(eps=0.5, min_samples=3)
    labels = clustering.fit_predict(x_scaled)

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = int((labels == -1).sum())

    if n_clusters < 2 or n_noise == len(labels):
        sil_score = 0.0
    else:
        mask = labels != -1
        sil_score = float(silhouette_score(x_scaled[mask], labels[mask]))

    return {
        "n_clusters": n_clusters,
        "silhouette_score": round(sil_score, 4),
        "n_noise": n_noise,
        "n_samples": len(df),
    }


def train_predict() -> dict[str, Any]:
    data = build_skip_prediction_features("2024-01-01", "2024-12-31")
    df = pd.DataFrame(data)

    x = df[PREDICT_FEATURES].values
    y = df["target_replayed"].values

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(x_train, y_train)

    y_pred = clf.predict(x_test)

    acc = float(accuracy_score(y_test, y_pred))
    f1 = float(f1_score(y_test, y_pred))

    importances: list[dict[str, Any]] = [
        {"feature": name, "importance": round(float(imp), 4)}
        for name, imp in zip(PREDICT_FEATURES, clf.feature_importances_)
    ]
    importances.sort(key=lambda x: float(x["importance"]), reverse=True)

    return {
        "accuracy": round(acc, 4),
        "f1": round(f1, 4),
        "n_samples": len(df),
        "feature_importances": importances,
    }


def _generate_synthetic_history(days: int = 180) -> pd.Series:
    rng = np.random.default_rng(seed=42)
    dates = pd.date_range(end=pd.Timestamp.today(), periods=days, freq="D")
    t = np.arange(days)
    dow = dates.dayofweek
    weekly_pattern = np.array([1.0, 0.92, 0.92, 0.95, 1.0, 1.35, 1.20])
    noise = rng.normal(0, 40, days)
    values = 1000.0 + 0.5 * t + weekly_pattern[dow] * 250 + noise
    return pd.Series(values, index=dates, name="listening_volume")


def train_forecast() -> dict[str, Any]:
    days = 14
    history = _generate_synthetic_history()

    model = ExponentialSmoothing(
        history,
        trend="add",
        seasonal="add",
        seasonal_periods=7,
        initialization_method="estimated",
    )
    fitted = model.fit()

    residuals = (history - fitted.fittedvalues).dropna()

    mae = float(np.mean(np.abs(residuals)))
    rmse = float(np.sqrt(np.mean(residuals**2)))

    predictions = forecast_listening_volume(days=days)

    return {
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "n_days": days,
        "predictions": predictions,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=["cluster", "predict", "forecast"])
    args = parser.parse_args()

    if args.mode == "cluster":
        result = train_cluster()
    elif args.mode == "predict":
        result = train_predict()
    elif args.mode == "forecast":
        result = train_forecast()

    print(result)

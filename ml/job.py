from __future__ import annotations

import argparse
import uuid
from typing import Any

import pandas as pd
from google.cloud import bigquery
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

from ml.features import build_cluster_features
from ml.load import (
    CLUSTER_TABLE,
    FORECAST_TABLE,
    METRICS_TABLE,
    write_cluster_assignments,
    write_forecast,
    write_model_metrics,
)
from ml.train import CLUSTER_FEATURES, train_cluster, train_forecast, train_predict


def _compute_cluster_assignments() -> list[dict[str, Any]]:
    data = build_cluster_features()
    df = pd.DataFrame(data)
    x = df[CLUSTER_FEATURES].values
    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x)
    clustering = DBSCAN(eps=0.5, min_samples=3)
    labels = clustering.fit_predict(x_scaled)
    row: dict[str, Any]
    assignments: list[dict[str, Any]] = []
    for i, row in enumerate(data):
        r = dict(row)
        r["cluster_id"] = int(labels[i])
        assignments.append(r)
    return assignments


def run_training(
    client: bigquery.Client | None = None,
    project: str = "",
    dataset: str = "ml",
) -> dict[str, Any]:
    run_id = str(uuid.uuid4())
    summary: dict[str, Any] = {"run_id": run_id, "modes": {}}

    if client is None:
        print(f"[dry-run] Training run {run_id}")

        cluster_metrics = train_cluster()
        print(f"[dry-run] cluster metrics: {cluster_metrics}")
        summary["modes"]["cluster"] = cluster_metrics

        predict_metrics = train_predict()
        print(f"[dry-run] predict metrics: {predict_metrics}")
        summary["modes"]["predict"] = predict_metrics

        forecast_metrics = train_forecast()
        print(f"[dry-run] forecast metrics: {forecast_metrics}")
        summary["modes"]["forecast"] = forecast_metrics
    else:
        prefix = f"{project}.{dataset}." if project and dataset else ""

        cluster_metrics = train_cluster()
        write_model_metrics(client, f"{prefix}{METRICS_TABLE}", cluster_metrics, "cluster", run_id)
        summary["modes"]["cluster"] = cluster_metrics

        assignments = _compute_cluster_assignments()
        write_cluster_assignments(client, f"{prefix}{CLUSTER_TABLE}", assignments, run_id)
        summary["cluster_assignments"] = len(assignments)

        predict_metrics = train_predict()
        write_model_metrics(client, f"{prefix}{METRICS_TABLE}", predict_metrics, "predict", run_id)
        summary["modes"]["predict"] = predict_metrics

        forecast_metrics = train_forecast()
        write_model_metrics(
            client, f"{prefix}{METRICS_TABLE}", forecast_metrics, "forecast", run_id
        )
        write_forecast(
            client,
            f"{prefix}{FORECAST_TABLE}",
            forecast_metrics["predictions"],
            run_id,
        )
        summary["modes"]["forecast"] = forecast_metrics

    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="")
    parser.add_argument("--dataset", default="ml")
    args = parser.parse_args()

    if args.project and args.dataset:
        bq_client = bigquery.Client(project=args.project)
        result = run_training(client=bq_client, project=args.project, dataset=args.dataset)
    else:
        result = run_training()

    print(f"Run complete: run_id={result['run_id']}")


if __name__ == "__main__":
    main()

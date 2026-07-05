from __future__ import annotations

from datetime import datetime
from typing import Any

from google.cloud import bigquery

CLUSTER_TABLE = "ml_cluster_assignments"
METRICS_TABLE = "ml_model_metrics"
FORECAST_TABLE = "ml_forecast"


def write_cluster_assignments(
    client: bigquery.Client,
    table_id: str,
    assignments: list[dict[str, Any]],
    run_id: str,
) -> int:
    trained_at = datetime.utcnow().isoformat()
    rows: list[dict[str, Any]] = []
    for row in assignments:
        r = dict(row)
        r["run_id"] = run_id
        r["trained_at"] = trained_at
        rows.append(r)
    client.insert_rows_json(table_id, rows)
    return len(rows)


def write_model_metrics(
    client: bigquery.Client,
    table_id: str,
    metrics: dict[str, Any],
    model_type: str,
    run_id: str,
) -> int:
    trained_at = datetime.utcnow().isoformat()
    rows: list[dict[str, Any]] = []
    for key, value in metrics.items():
        if key == "feature_importances":
            for fi in value:
                rows.append(
                    {
                        "model_type": model_type,
                        "metric_name": f"feature_importance_{fi['feature']}",
                        "metric_value": float(fi["importance"]),
                        "run_id": run_id,
                        "trained_at": trained_at,
                    }
                )
        elif key == "predictions":
            continue
        else:
            rows.append(
                {
                    "model_type": model_type,
                    "metric_name": key,
                    "metric_value": float(value),
                    "run_id": run_id,
                    "trained_at": trained_at,
                }
            )
    client.insert_rows_json(table_id, rows)
    return len(rows)


def write_forecast(
    client: bigquery.Client,
    table_id: str,
    predictions: list[dict[str, Any]],
    run_id: str,
) -> int:
    trained_at = datetime.utcnow().isoformat()
    rows: list[dict[str, Any]] = []
    for pred in predictions:
        rows.append(
            {
                "forecast_date": pred["date"],
                "predicted_minutes": pred["yhat"],
                "lower_bound": pred["yhat_lower"],
                "upper_bound": pred["yhat_upper"],
                "run_id": run_id,
                "trained_at": trained_at,
            }
        )
    client.insert_rows_json(table_id, rows)
    return len(rows)

from __future__ import annotations

from unittest.mock import MagicMock, create_autospec, patch

import pytest
from google.cloud import bigquery

from ml.job import run_training
from ml.load import (
    CLUSTER_TABLE,
    FORECAST_TABLE,
    METRICS_TABLE,
    write_cluster_assignments,
    write_forecast,
    write_model_metrics,
)


@pytest.fixture
def mock_client() -> MagicMock:
    return create_autospec(bigquery.Client, instance=True)  # type: ignore[no-any-return]


class TestWriteClusterAssignments:
    def test_adds_run_id_and_trained_at(self, mock_client: MagicMock) -> None:
        assignments = [{"track_id": "t1", "cluster_id": 0}]
        write_cluster_assignments(mock_client, "tbl", assignments, "run-abc")
        rows = mock_client.insert_rows_json.call_args[0][1]
        assert rows[0]["run_id"] == "run-abc"
        assert "trained_at" in rows[0]

    def test_returns_row_count(self, mock_client: MagicMock) -> None:
        assignments = [
            {"track_id": "t1", "cluster_id": 0},
            {"track_id": "t2", "cluster_id": 1},
        ]
        result = write_cluster_assignments(mock_client, "tbl", assignments, "run-1")
        assert result == 2

    def test_calls_insert_rows_json(self, mock_client: MagicMock) -> None:
        assignments = [{"track_id": "t1", "cluster_id": 0}]
        write_cluster_assignments(mock_client, "tbl", assignments, "run-1")
        mock_client.insert_rows_json.assert_called_once()

    def test_does_not_mutate_input(self, mock_client: MagicMock) -> None:
        original = {"track_id": "t1", "cluster_id": 0}
        assignments = [original]
        write_cluster_assignments(mock_client, "tbl", assignments, "run-1")
        assert "run_id" not in original
        assert "trained_at" not in original

    def test_passes_correct_table_id(self, mock_client: MagicMock) -> None:
        assignments = [{"track_id": "t1", "cluster_id": 0}]
        write_cluster_assignments(
            mock_client, "proj.ds.ml_cluster_assignments", assignments, "run-1"
        )
        assert mock_client.insert_rows_json.call_args[0][0] == "proj.ds.ml_cluster_assignments"

    def test_empty_assignments_returns_zero(self, mock_client: MagicMock) -> None:
        result = write_cluster_assignments(mock_client, "tbl", [], "run-1")
        assert result == 0
        mock_client.insert_rows_json.assert_called_once_with("tbl", [])


class TestWriteModelMetrics:
    def test_writes_scalar_metrics_as_separate_rows(self, mock_client: MagicMock) -> None:
        metrics = {"n_clusters": 5, "silhouette_score": 0.42}
        write_model_metrics(mock_client, "tbl", metrics, "cluster", "run-1")
        rows = mock_client.insert_rows_json.call_args[0][1]
        assert len(rows) == 2
        names = {r["metric_name"] for r in rows}
        assert names == {"n_clusters", "silhouette_score"}

    def test_adds_model_type_and_run_id(self, mock_client: MagicMock) -> None:
        metrics = {"mae": 30.5}
        write_model_metrics(mock_client, "tbl", metrics, "forecast", "run-xyz")
        row = mock_client.insert_rows_json.call_args[0][1][0]
        assert row["model_type"] == "forecast"
        assert row["run_id"] == "run-xyz"

    def test_flattens_feature_importances(self, mock_client: MagicMock) -> None:
        metrics = {
            "accuracy": 0.85,
            "feature_importances": [
                {"feature": "danceability", "importance": 0.12},
                {"feature": "energy", "importance": 0.10},
            ],
        }
        write_model_metrics(mock_client, "tbl", metrics, "predict", "run-1")
        rows = mock_client.insert_rows_json.call_args[0][1]
        assert len(rows) == 3
        metric_names = {r["metric_name"] for r in rows}
        assert "feature_importance_danceability" in metric_names
        assert "feature_importance_energy" in metric_names
        fi_row = next(r for r in rows if "feature_importance" in r["metric_name"])
        assert fi_row["metric_value"] == 0.12

    def test_skips_predictions_key(self, mock_client: MagicMock) -> None:
        metrics = {
            "mae": 30.5,
            "predictions": [{"date": "2024-01-01", "yhat": 100.0}],
        }
        write_model_metrics(mock_client, "tbl", metrics, "forecast", "run-1")
        rows = mock_client.insert_rows_json.call_args[0][1]
        assert len(rows) == 1
        assert rows[0]["metric_name"] == "mae"

    def test_returns_row_count(self, mock_client: MagicMock) -> None:
        metrics = {"a": 1.0, "b": 2.0}
        result = write_model_metrics(mock_client, "tbl", metrics, "t", "run-1")
        assert result == 2

    def test_scalar_rows_have_no_extra_keys(self, mock_client: MagicMock) -> None:
        metrics = {"n_samples": 100}
        write_model_metrics(mock_client, "tbl", metrics, "cluster", "run-1")
        row = mock_client.insert_rows_json.call_args[0][1][0]
        expected = {"model_type", "metric_name", "metric_value", "run_id", "trained_at"}
        assert set(row.keys()) == expected

    def test_empty_metrics_returns_zero(self, mock_client: MagicMock) -> None:
        result = write_model_metrics(mock_client, "tbl", {}, "t", "run-1")
        assert result == 0


class TestWriteForecast:
    def test_renames_columns(self, mock_client: MagicMock) -> None:
        predictions = [
            {
                "date": "2024-01-01",
                "yhat": 100.0,
                "yhat_lower": 80.0,
                "yhat_upper": 120.0,
            }
        ]
        write_forecast(mock_client, "tbl", predictions, "run-1")
        row = mock_client.insert_rows_json.call_args[0][1][0]
        assert row["forecast_date"] == "2024-01-01"
        assert row["predicted_minutes"] == 100.0
        assert row["lower_bound"] == 80.0
        assert row["upper_bound"] == 120.0

    def test_adds_run_id_and_trained_at(self, mock_client: MagicMock) -> None:
        predictions = [
            {
                "date": "2024-01-01",
                "yhat": 100.0,
                "yhat_lower": 80.0,
                "yhat_upper": 120.0,
            }
        ]
        write_forecast(mock_client, "tbl", predictions, "run-abc")
        row = mock_client.insert_rows_json.call_args[0][1][0]
        assert row["run_id"] == "run-abc"
        assert "trained_at" in row

    def test_returns_row_count(self, mock_client: MagicMock) -> None:
        predictions = [
            {"date": "2024-01-01", "yhat": 100.0, "yhat_lower": 80.0, "yhat_upper": 120.0},
            {"date": "2024-01-02", "yhat": 110.0, "yhat_lower": 90.0, "yhat_upper": 130.0},
        ]
        result = write_forecast(mock_client, "tbl", predictions, "run-1")
        assert result == 2

    def test_calls_insert_rows_json_with_correct_table(self, mock_client: MagicMock) -> None:
        predictions = [
            {"date": "2024-01-01", "yhat": 100.0, "yhat_lower": 80.0, "yhat_upper": 120.0},
        ]
        write_forecast(mock_client, "proj.ds.ml_forecast", predictions, "run-1")
        assert mock_client.insert_rows_json.call_args[0][0] == "proj.ds.ml_forecast"

    def test_empty_predictions_returns_zero(self, mock_client: MagicMock) -> None:
        result = write_forecast(mock_client, "tbl", [], "run-1")
        assert result == 0


class TestRunTraining:
    def test_dry_run_returns_summary(self) -> None:
        result = run_training()
        assert "run_id" in result
        assert "modes" in result
        assert "cluster" in result["modes"]
        assert "predict" in result["modes"]
        assert "forecast" in result["modes"]

    def test_dry_run_summary_has_all_result_keys(self) -> None:
        result = run_training()
        for mode in ("cluster", "predict", "forecast"):
            assert isinstance(result["modes"][mode], dict)

    def test_dry_run_run_id_is_uuid_string(self) -> None:
        result = run_training()
        assert isinstance(result["run_id"], str)
        assert len(result["run_id"]) > 0

    def test_with_client_writes_outputs(self, mock_client: MagicMock) -> None:
        mock_client.insert_rows_json.return_value = []
        result = run_training(client=mock_client, project="proj", dataset="ds")
        assert mock_client.insert_rows_json.call_count >= 4
        assert "run_id" in result
        assert "cluster_assignments" in result
        assert result["cluster_assignments"] > 0

    def test_with_client_writes_to_correct_tables(self, mock_client: MagicMock) -> None:
        mock_client.insert_rows_json.return_value = []
        run_training(client=mock_client, project="proj", dataset="ds")
        calls = mock_client.insert_rows_json.call_args_list
        table_ids = [c[0][0] for c in calls]
        assert "proj.ds.ml_model_metrics" in table_ids
        assert "proj.ds.ml_cluster_assignments" in table_ids
        assert "proj.ds.ml_forecast" in table_ids

    def test_with_client_returns_summary(self, mock_client: MagicMock) -> None:
        mock_client.insert_rows_json.return_value = []
        result = run_training(client=mock_client, project="proj", dataset="ds")
        assert "modes" in result
        for mode in ("cluster", "predict", "forecast"):
            assert mode in result["modes"]
            assert isinstance(result["modes"][mode], dict)

    def test_without_project_dataset_prefixes_table_correctly(self, mock_client: MagicMock) -> None:
        mock_client.insert_rows_json.return_value = []
        run_training(client=mock_client, project="", dataset="")
        calls = mock_client.insert_rows_json.call_args_list
        table_ids = [c[0][0] for c in calls]
        assert METRICS_TABLE in table_ids
        assert CLUSTER_TABLE in table_ids
        assert FORECAST_TABLE in table_ids

    def test_dry_run_prints_output(self, capsys: pytest.CaptureFixture[str]) -> None:
        result = run_training()
        captured = capsys.readouterr()
        assert "dry-run" in captured.out
        assert result["run_id"] in captured.out


class TestCli:
    def test_main_calls_run_training_dry_run(self) -> None:
        test_args = ["ml.job"]
        with (
            patch("sys.argv", test_args),
            patch("ml.job.run_training") as mock_run,
        ):
            from ml.job import main

            main()
            mock_run.assert_called_once_with()

    def test_main_calls_run_training_with_client(self) -> None:
        test_args = ["ml.job", "--project", "proj", "--dataset", "ds"]
        with (
            patch("sys.argv", test_args),
            patch("ml.job.bigquery.Client") as mock_bq,
            patch("ml.job.run_training") as mock_run,
        ):
            from ml.job import main

            main()
            mock_run.assert_called_once_with(
                client=mock_bq.return_value,
                project="proj",
                dataset="ds",
            )

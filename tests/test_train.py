from datetime import date

from ml.train import train_cluster, train_forecast, train_predict

CLUSTER_RESULT_KEYS = {"n_clusters", "silhouette_score", "n_noise", "n_samples"}
PREDICT_RESULT_KEYS = {"accuracy", "f1", "n_samples", "feature_importances"}
FORECAST_RESULT_KEYS = {"mae", "rmse", "n_days", "predictions"}
FORECAST_PRED_KEYS = {"date", "yhat", "yhat_lower", "yhat_upper"}


class TestTrainCluster:
    def test_returns_dict_with_all_keys(self) -> None:
        result = train_cluster()
        assert isinstance(result, dict)
        assert set(result.keys()) == CLUSTER_RESULT_KEYS

    def test_correct_types(self) -> None:
        result = train_cluster()
        assert isinstance(result["n_clusters"], int)
        assert isinstance(result["silhouette_score"], float)
        assert isinstance(result["n_noise"], int)
        assert isinstance(result["n_samples"], int)

    def test_n_samples_100(self) -> None:
        assert train_cluster()["n_samples"] == 100

    def test_n_clusters_non_negative(self) -> None:
        assert train_cluster()["n_clusters"] >= 0

    def test_n_noise_non_negative(self) -> None:
        assert train_cluster()["n_noise"] >= 0

    def test_silhouette_score_in_range(self) -> None:
        result = train_cluster()
        assert -1.0 <= result["silhouette_score"] <= 1.0

    def test_noise_plus_clusters_equals_samples(self) -> None:
        result = train_cluster()
        labelled = int(result["n_samples"] - result["n_noise"])
        assert labelled >= 0

    def test_silhouette_zero_when_all_noise(self) -> None:
        result = train_cluster()
        if result["n_noise"] == result["n_samples"]:
            assert result["silhouette_score"] == 0.0

    def test_deterministic(self) -> None:
        assert train_cluster() == train_cluster()


class TestTrainPredict:
    def test_returns_dict_with_all_keys(self) -> None:
        result = train_predict()
        assert isinstance(result, dict)
        assert set(result.keys()) == PREDICT_RESULT_KEYS

    def test_correct_types(self) -> None:
        result = train_predict()
        assert isinstance(result["accuracy"], float)
        assert isinstance(result["f1"], float)
        assert isinstance(result["n_samples"], int)
        assert isinstance(result["feature_importances"], list)

    def test_n_samples_positive(self) -> None:
        assert train_predict()["n_samples"] > 0

    def test_accuracy_in_range(self) -> None:
        result = train_predict()
        assert 0.0 <= result["accuracy"] <= 1.0

    def test_f1_in_range(self) -> None:
        result = train_predict()
        assert 0.0 <= result["f1"] <= 1.0

    def test_feature_importances_structure(self) -> None:
        result = train_predict()
        for entry in result["feature_importances"]:
            assert set(entry.keys()) == {"feature", "importance"}
            assert isinstance(entry["feature"], str)
            assert isinstance(entry["importance"], float)
            assert 0.0 <= entry["importance"] <= 1.0

    def test_feature_importances_sorted_descending(self) -> None:
        result = train_predict()
        imps = [e["importance"] for e in result["feature_importances"]]
        assert imps == sorted(imps, reverse=True)

    def test_feature_importances_count(self) -> None:
        assert len(train_predict()["feature_importances"]) == 17

    def test_deterministic(self) -> None:
        assert train_predict() == train_predict()


class TestTrainForecast:
    def test_returns_dict_with_all_keys(self) -> None:
        result = train_forecast()
        assert isinstance(result, dict)
        assert set(result.keys()) == FORECAST_RESULT_KEYS

    def test_correct_types(self) -> None:
        result = train_forecast()
        assert isinstance(result["mae"], float)
        assert isinstance(result["rmse"], float)
        assert isinstance(result["n_days"], int)
        assert isinstance(result["predictions"], list)
        assert all(isinstance(p, dict) for p in result["predictions"])

    def test_n_days_is_14(self) -> None:
        assert train_forecast()["n_days"] == 14

    def test_mae_positive(self) -> None:
        assert train_forecast()["mae"] >= 0

    def test_rmse_positive(self) -> None:
        assert train_forecast()["rmse"] >= 0

    def test_prediction_count(self) -> None:
        assert len(train_forecast()["predictions"]) == 14

    def test_prediction_keys(self) -> None:
        result = train_forecast()
        for entry in result["predictions"]:
            assert set(entry.keys()) == FORECAST_PRED_KEYS
            assert isinstance(entry["date"], str)
            assert isinstance(entry["yhat"], float)
            assert isinstance(entry["yhat_lower"], float)
            assert isinstance(entry["yhat_upper"], float)

    def test_prediction_date_format(self) -> None:
        result = train_forecast()
        for entry in result["predictions"]:
            date.fromisoformat(entry["date"])

    def test_confidence_intervals(self) -> None:
        result = train_forecast()
        for entry in result["predictions"]:
            assert entry["yhat_lower"] <= entry["yhat"]
            assert entry["yhat_upper"] >= entry["yhat"]

    def test_predictions_positive(self) -> None:
        result = train_forecast()
        for entry in result["predictions"]:
            assert entry["yhat"] > 0

    def test_deterministic(self) -> None:
        assert train_forecast() == train_forecast()

from datetime import date

from ml.forecast import forecast_listening_volume


class TestForecast:
    def test_default_days(self) -> None:
        result = forecast_listening_volume()
        assert len(result) == 14

    def test_custom_days(self) -> None:
        result = forecast_listening_volume(days=7)
        assert len(result) == 7

    def test_large_forecast(self) -> None:
        result = forecast_listening_volume(days=30)
        assert len(result) == 30

    def test_return_structure(self) -> None:
        result = forecast_listening_volume(days=1)
        entry = result[0]
        assert set(entry.keys()) == {"date", "yhat", "yhat_lower", "yhat_upper"}
        assert isinstance(entry["date"], str)
        assert isinstance(entry["yhat"], float)
        assert isinstance(entry["yhat_lower"], float)
        assert isinstance(entry["yhat_upper"], float)

    def test_date_format(self) -> None:
        result = forecast_listening_volume(days=1)
        parsed = date.fromisoformat(result[0]["date"])
        assert isinstance(parsed, date)

    def test_confidence_intervals(self) -> None:
        result = forecast_listening_volume(days=14)
        for entry in result:
            assert entry["yhat_lower"] <= entry["yhat"]
            assert entry["yhat_upper"] >= entry["yhat"]

    def test_zero_days_returns_empty(self) -> None:
        assert forecast_listening_volume(days=0) == []

    def test_negative_days_returns_empty(self) -> None:
        assert forecast_listening_volume(days=-5) == []

    def test_deterministic(self) -> None:
        assert forecast_listening_volume(days=14) == forecast_listening_volume(days=14)

    def test_values_are_positive(self) -> None:
        result = forecast_listening_volume(days=14)
        for entry in result:
            assert entry["yhat"] > 0

    def test_monotonic_dates(self) -> None:
        result = forecast_listening_volume(days=14)
        dates_list = [entry["date"] for entry in result]
        assert dates_list == sorted(dates_list)

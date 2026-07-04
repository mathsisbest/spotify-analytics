from typing import Any

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing


def _generate_synthetic_history(days: int = 180) -> pd.Series:
    rng = np.random.default_rng(seed=42)
    dates = pd.date_range(end=pd.Timestamp.today(), periods=days, freq="D")
    t = np.arange(days)
    dow = dates.dayofweek
    weekly_pattern = np.array([1.0, 0.92, 0.92, 0.95, 1.0, 1.35, 1.20])
    noise = rng.normal(0, 40, days)
    values = 1000.0 + 0.5 * t + weekly_pattern[dow] * 250 + noise
    return pd.Series(values, index=dates, name="listening_volume")


def forecast_listening_volume(days: int = 14) -> list[dict[str, Any]]:
    if days <= 0:
        return []

    history = _generate_synthetic_history()

    model = ExponentialSmoothing(
        history,
        trend="add",
        seasonal="add",
        seasonal_periods=7,
        initialization_method="estimated",
    )
    fitted = model.fit()

    forecast = fitted.forecast(days)

    residuals = (history - fitted.fittedvalues).dropna()
    sigma = float(np.std(residuals, ddof=1))

    results: list[dict[str, Any]] = []
    for date, yhat in forecast.items():
        results.append(
            {
                "date": date.strftime("%Y-%m-%d"),
                "yhat": round(float(yhat), 2),
                "yhat_lower": round(float(yhat - 1.96 * sigma), 2),
                "yhat_upper": round(float(yhat + 1.96 * sigma), 2),
            }
        )

    return results

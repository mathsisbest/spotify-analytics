select
    forecast_date,
    predicted_minutes,
    lower_bound,
    upper_bound,
    run_id,
    trained_at
from {{ source('marts', 'ml_forecast') }}

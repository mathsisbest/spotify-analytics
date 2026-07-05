select
    model_type,
    metric_name,
    metric_value,
    run_id,
    trained_at
from {{ source('marts', 'ml_model_metrics') }}

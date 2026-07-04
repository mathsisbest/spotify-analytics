with listening as (
    select
        track_id,
        played_at
    from {{ ref('stg_streaming_history') }}
)

select
    track_id,
    played_at,
    extract(hour from played_at) as hour_of_day,
    extract(dayofweek from played_at) as day_of_week,
    extract(month from played_at) as month,
    extract(day from played_at) as day_of_month,
    extract(year from played_at) as year,
    case
        when extract(dayofweek from played_at) in (1, 7) then true
        else false
    end as is_weekend
from listening

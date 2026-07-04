-- Assert that minutes_listened is never negative.
select
    listening_date,
    minutes_listened
from {{ ref('fct_daily_summary') }}
where minutes_listened < 0

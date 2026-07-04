-- Assert that minutes_listened is within a reasonable range (0 to 24 hours per day).
-- 1440 minutes = 24 hours; 1440 * 24 = 34560 allows up to 24 concurrent days
-- which should never happen from a single-user poller.
select
    listening_date,
    minutes_listened
from {{ ref('fct_daily_summary') }}
where minutes_listened < 0
   or minutes_listened > 34560

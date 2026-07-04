-- Assert that played_at timestamps are never in the future.
select
    track_id,
    played_at
from {{ ref('fct_listening') }}
where played_at > current_timestamp()

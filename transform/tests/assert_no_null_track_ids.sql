-- Assert that fct_listening contains no null track_ids.
select
    track_id
from {{ ref('fct_listening') }}
where track_id is null

-- TODO (Phase 2): Sessionize listening history.
-- A new session starts when the gap between consecutive plays exceeds 30 minutes.
-- Output columns: session_id, session_start, session_end, track_count, ...
-- This is a shell to be fleshed out in Phase 2.

with listening as (
    select
        track_id,
        played_at
    from {{ ref('stg_streaming_history') }}
)

select
    track_id,
    played_at,
    timestamp_diff(
        played_at,
        lag(played_at) over (order by played_at),
        minute
    ) as gap_minutes
from listening

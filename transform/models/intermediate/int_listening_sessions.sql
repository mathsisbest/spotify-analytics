with listening as (
    select
        track_id,
        played_at
    from {{ ref('stg_streaming_history') }}
),

with_gaps as (
    select
        track_id,
        played_at,
        timestamp_diff(played_at, lag(played_at) over (order by played_at), minute) as gap_minutes
    from listening
),

session_groups as (
    select
        track_id,
        played_at,
        gap_minutes,
        sum(case when gap_minutes > 30 or gap_minutes is null then 1 else 0 end) over (
            order by played_at
            rows between unbounded preceding and current row
        ) as session_group
    from with_gaps
),

sessionized as (
    select
        session_group,
        track_id,
        played_at,
        min(played_at) over (partition by session_group) as session_start_ts,
        max(played_at) over (partition by session_group) as session_end_ts,
        row_number() over (partition by session_group order by played_at) as session_track_number,
        gap_minutes
    from session_groups
)

select
    to_hex(md5(concat(cast(session_group as string), cast(session_start_ts as string)))) as session_id,
    track_id,
    played_at,
    session_start_ts,
    session_end_ts,
    session_track_number,
    gap_minutes
from sessionized
order by played_at

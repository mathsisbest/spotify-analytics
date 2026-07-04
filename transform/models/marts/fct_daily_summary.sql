with listening as (
    select
        played_at,
        track_id,
        artist_id,
        duration_ms
    from {{ ref('fct_listening') }}
),

daily as (
    select
        date(played_at) as listening_date,
        count(distinct track_id) as track_count,
        count(distinct artist_id) as artist_count,
        sum(duration_ms) / 60000.0 as minutes_listened,
        count(*) as listen_count
    from listening
    group by listening_date
)

select
    listening_date,
    minutes_listened,
    track_count,
    artist_count,
    listen_count
from daily

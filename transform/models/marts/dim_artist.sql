with artist_listening as (
    select
        artist_id,
        any_value(artist_name) as artist_name,
        min(played_at) as first_listened,
        max(played_at) as last_listened,
        count(*) as listen_count
    from {{ ref('stg_streaming_history') }}
    group by artist_id
)

select
    al.artist_id,
    al.artist_name,
    cast(null as array<string>) as genres,
    cast(null as int64) as popularity,
    cast(null as int64) as follower_count,
    al.first_listened,
    al.last_listened,
    al.listen_count,
    current_timestamp() as last_updated
from artist_listening as al

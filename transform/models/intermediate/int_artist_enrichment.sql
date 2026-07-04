with artists as (
    select distinct
        artist_id,
        artist_name
    from {{ ref('stg_streaming_history') }}
)

select
    artist_id,
    artist_name,
    cast(null as array<string>) as genres,
    cast(null as int64) as popularity,
    cast(null as int64) as follower_count,
    cast(null as timestamp) as last_updated
from artists

with source as (
    select
        track_id,
        track_name,
        artist_name,
        artist_id,
        album_name,
        album_id,
        played_at,
        context,
        ingested_at
    from {{ source('raw', 'streaming_history') }}
),

deduplicated as (
    select
        *,
        row_number() over (
            partition by track_id, played_at
            order by ingested_at desc
        ) as rn
    from source
),

casted as (
    select
        track_id,
        track_name,
        artist_name,
        artist_id,
        album_name,
        album_id,
        cast(played_at as timestamp) as played_at,
        context,
        cast(ingested_at as timestamp) as ingested_at
    from deduplicated
    where rn = 1
)

select
    track_id,
    track_name,
    artist_name,
    artist_id,
    album_name,
    album_id,
    played_at,
    context,
    ingested_at
from casted

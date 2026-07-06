with source as (
    select
        track_id,
        track_name,
        artist_id,
        artist_name,
        artist_ids,
        artist_names,
        album_name,
        album_id,
        played_at,
        context,
        duration_ms,
        loaded_at
    from {{ source('raw', 'streaming_history') }}
),

deduplicated as (
    select
        *,
        row_number() over (
            partition by track_id, played_at
            order by loaded_at desc
        ) as rn
    from source
),

casted as (
    select
        track_id,
        track_name,
        artist_id,
        artist_name,
        artist_ids,
        artist_names,
        album_name,
        album_id,
        cast(played_at as timestamp) as played_at,
        context,
        duration_ms,
        cast(loaded_at as timestamp) as loaded_at
    from deduplicated
    where rn = 1
)

select
    track_id,
    track_name,
    artist_id,
    artist_name,
    artist_ids,
    artist_names,
    album_name,
    album_id,
    played_at,
    context,
    duration_ms,
    loaded_at
from casted

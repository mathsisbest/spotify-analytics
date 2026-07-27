with source as (
    select
        replace(spotify_track_uri, 'spotify:track:', '') as track_id,
        master_metadata_track_name as track_name,
        cast(null as string) as artist_id,
        master_metadata_album_artist_name as artist_name,
        cast(null as string) as artist_ids,
        master_metadata_album_artist_name as artist_names,
        master_metadata_album_album_name as album_name,
        cast(null as string) as album_id,
        cast(ts as timestamp) as played_at,
        reason_start as context,
        ms_played as duration_ms,
        current_timestamp() as loaded_at
    from {{ source('raw', 'streaming_history_extended') }}
    where master_metadata_track_name is not null
),

deduplicated as (
    select
        *,
        row_number() over (
            partition by track_id, played_at
            order by played_at desc
        ) as rn
    from source
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
from deduplicated
where rn = 1

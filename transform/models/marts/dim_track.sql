with track_info as (
    select
        track_id,
        any_value(track_name) as track_name,
        any_value(artist_name) as artist_name,
        any_value(artist_id) as artist_id,
        any_value(album_name) as album_name,
        any_value(album_id) as album_id,
        min(played_at) as scd_valid_from
    from {{ ref('stg_streaming_history') }}
    group by track_id
),

latest_features as (
    select
        *,
        row_number() over (
            partition by track_id
            order by fetched_at desc
        ) as rn
    from {{ ref('stg_track_features') }}
)

select
    ti.track_id,
    ti.track_name,
    ti.artist_name,
    ti.artist_id,
    ti.album_name,
    ti.album_id,
    ti.scd_valid_from,
    cast(null as timestamp) as scd_valid_to,
    true as is_current,
    lf.danceability,
    lf.energy,
    lf.key,
    lf.loudness,
    lf.mode,
    lf.speechiness,
    lf.acousticness,
    lf.instrumentalness,
    lf.liveness,
    lf.valence,
    lf.tempo,
    lf.time_signature,
    lf.duration_ms,
    lf.fetched_at
from track_info as ti
left join latest_features as lf
    on ti.track_id = lf.track_id and lf.rn = 1

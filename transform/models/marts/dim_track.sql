-- TODO (Phase 2): Track dimension with slowly-changing metadata + audio features.
-- One row per track_id, upserted as new data arrives.
-- This is a stub to be fleshed out in Phase 2.

with tracks as (
    select distinct
        sh.track_id,
        sh.track_name,
        sh.artist_name,
        sh.artist_id,
        sh.album_name,
        sh.album_id,
        tf.danceability,
        tf.energy,
        tf.key,
        tf.loudness,
        tf.mode,
        tf.speechiness,
        tf.acousticness,
        tf.instrumentalness,
        tf.liveness,
        tf.valence,
        tf.tempo,
        tf.time_signature,
        tf.duration_ms,
        tf.fetched_at,
        row_number() over (
            partition by sh.track_id
            order by tf.fetched_at desc
        ) as rn
    from {{ ref('stg_streaming_history') }} as sh
    left join {{ ref('stg_track_features') }} as tf
        on sh.track_id = tf.track_id
)

select
    track_id,
    track_name,
    artist_name,
    artist_id,
    album_name,
    album_id,
    danceability,
    energy,
    key,
    loudness,
    mode,
    speechiness,
    acousticness,
    instrumentalness,
    liveness,
    valence,
    tempo,
    time_signature,
    duration_ms,
    fetched_at
from tracks
where rn = 1

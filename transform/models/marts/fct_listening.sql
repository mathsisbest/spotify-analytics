-- TODO (Phase 2): Fact listening table with full enrichment.
-- One row per listen, joined with audio features, time features, and session context.
-- This is a stub to be fleshed out in Phase 2.

with listening as (
    select
        sh.track_id,
        sh.track_name,
        sh.artist_name,
        sh.artist_id,
        sh.album_name,
        sh.album_id,
        sh.played_at,
        sh.context,
        tf.danceability,
        tf.energy,
        tf.valence,
        tf.tempo,
        tf.duration_ms,
        tf.key,
        tf.loudness,
        tf.mode,
        tf.speechiness,
        tf.acousticness,
        tf.instrumentalness,
        tf.liveness,
        tf.time_signature,
        t.hour_of_day,
        t.day_of_week,
        t.month,
        t.is_weekend
    from {{ ref('stg_streaming_history') }} as sh
    left join {{ ref('stg_track_features') }} as tf
        on sh.track_id = tf.track_id
    left join {{ ref('int_time_features') }} as t
        on sh.track_id = t.track_id and sh.played_at = t.played_at
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
    danceability,
    energy,
    valence,
    tempo,
    duration_ms,
    key,
    loudness,
    mode,
    speechiness,
    acousticness,
    instrumentalness,
    liveness,
    time_signature,
    hour_of_day,
    day_of_week,
    month,
    is_weekend
from listening

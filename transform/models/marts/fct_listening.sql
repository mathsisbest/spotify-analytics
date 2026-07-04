with streaming_base as (
    select *
    from {{ ref('stg_streaming_history') }}
),

audio_features as (
    select
        track_id,
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
        duration_ms
    from {{ ref('stg_track_features') }}
),

time_features as (
    select
        track_id,
        played_at,
        hour_of_day,
        day_of_week,
        month,
        day_of_month,
        year,
        is_weekend
    from {{ ref('int_time_features') }}
),

joined as (
    select
        sb.*,
        af.danceability,
        af.energy,
        af.key,
        af.loudness,
        af.mode,
        af.speechiness,
        af.acousticness,
        af.instrumentalness,
        af.liveness,
        af.valence,
        af.tempo,
        af.time_signature,
        af.duration_ms,
        tf.hour_of_day,
        tf.day_of_week,
        tf.month,
        tf.day_of_month,
        tf.year,
        tf.is_weekend
    from streaming_base as sb
    left join audio_features as af
        on sb.track_id = af.track_id
    left join time_features as tf
        on sb.track_id = tf.track_id and sb.played_at = tf.played_at
)

select
    j.*,
    ils.* except (track_id, played_at)
from joined as j
left join {{ ref('int_listening_sessions') }} as ils
    on j.track_id = ils.track_id and j.played_at = ils.played_at

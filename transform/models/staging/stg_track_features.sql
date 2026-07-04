with source as (
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
        duration_ms,
        fetched_at
    from {{ source('raw', 'track_features') }}
),

casted as (
    select
        track_id,
        cast(danceability as float64) as danceability,
        cast(energy as float64) as energy,
        cast(key as int64) as key,
        cast(loudness as float64) as loudness,
        cast(mode as int64) as mode,
        cast(speechiness as float64) as speechiness,
        cast(acousticness as float64) as acousticness,
        cast(instrumentalness as float64) as instrumentalness,
        cast(liveness as float64) as liveness,
        cast(valence as float64) as valence,
        cast(tempo as float64) as tempo,
        cast(time_signature as int64) as time_signature,
        cast(duration_ms as int64) as duration_ms,
        cast(fetched_at as timestamp) as fetched_at
    from source
)

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
    duration_ms,
    fetched_at
from casted

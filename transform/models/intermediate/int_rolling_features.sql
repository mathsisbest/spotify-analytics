with daily_listening as (
    select
        artist_id,
        date(played_at) as listening_date,
        avg(danceability) as avg_danceability,
        avg(energy) as avg_energy,
        avg(valence) as avg_valence,
        avg(tempo) as avg_tempo,
        avg(loudness) as avg_loudness,
        avg(acousticness) as avg_acousticness,
        avg(instrumentalness) as avg_instrumentalness,
        avg(liveness) as avg_liveness,
        avg(speechiness) as avg_speechiness,
        count(*) as listen_count
    from {{ ref('fct_listening') }}
    group by artist_id, listening_date
)

select
    artist_id,
    listening_date,
    avg_danceability,
    avg_energy,
    avg_valence,
    avg_tempo,
    avg_loudness,
    avg_acousticness,
    avg_instrumentalness,
    avg_liveness,
    avg_speechiness,
    listen_count,
    avg(avg_danceability) over (
        partition by artist_id
        order by unix_date(listening_date)
        range between 6 preceding and current row
    ) as avg_danceability_7d,
    avg(avg_danceability) over (
        partition by artist_id
        order by unix_date(listening_date)
        range between 29 preceding and current row
    ) as avg_danceability_30d,
    avg(avg_energy) over (
        partition by artist_id
        order by unix_date(listening_date)
        range between 6 preceding and current row
    ) as avg_energy_7d,
    avg(avg_energy) over (
        partition by artist_id
        order by unix_date(listening_date)
        range between 29 preceding and current row
    ) as avg_energy_30d,
    avg(avg_valence) over (
        partition by artist_id
        order by unix_date(listening_date)
        range between 6 preceding and current row
    ) as avg_valence_7d,
    avg(avg_valence) over (
        partition by artist_id
        order by unix_date(listening_date)
        range between 29 preceding and current row
    ) as avg_valence_30d,
    avg(avg_tempo) over (
        partition by artist_id
        order by unix_date(listening_date)
        range between 6 preceding and current row
    ) as avg_tempo_7d,
    avg(avg_tempo) over (
        partition by artist_id
        order by unix_date(listening_date)
        range between 29 preceding and current row
    ) as avg_tempo_30d,
    avg(avg_loudness) over (
        partition by artist_id
        order by unix_date(listening_date)
        range between 6 preceding and current row
    ) as avg_loudness_7d,
    avg(avg_loudness) over (
        partition by artist_id
        order by unix_date(listening_date)
        range between 29 preceding and current row
    ) as avg_loudness_30d,
    avg(avg_acousticness) over (
        partition by artist_id
        order by unix_date(listening_date)
        range between 6 preceding and current row
    ) as avg_acousticness_7d,
    avg(avg_acousticness) over (
        partition by artist_id
        order by unix_date(listening_date)
        range between 29 preceding and current row
    ) as avg_acousticness_30d,
    avg(avg_instrumentalness) over (
        partition by artist_id
        order by unix_date(listening_date)
        range between 6 preceding and current row
    ) as avg_instrumentalness_7d,
    avg(avg_instrumentalness) over (
        partition by artist_id
        order by unix_date(listening_date)
        range between 29 preceding and current row
    ) as avg_instrumentalness_30d,
    avg(avg_liveness) over (
        partition by artist_id
        order by unix_date(listening_date)
        range between 6 preceding and current row
    ) as avg_liveness_7d,
    avg(avg_liveness) over (
        partition by artist_id
        order by unix_date(listening_date)
        range between 29 preceding and current row
    ) as avg_liveness_30d,
    avg(avg_speechiness) over (
        partition by artist_id
        order by unix_date(listening_date)
        range between 6 preceding and current row
    ) as avg_speechiness_7d,
    avg(avg_speechiness) over (
        partition by artist_id
        order by unix_date(listening_date)
        range between 29 preceding and current row
    ) as avg_speechiness_30d,
    sum(listen_count) over (
        partition by artist_id
        order by unix_date(listening_date)
        range between 6 preceding and current row
    ) as track_count_7d,
    sum(listen_count) over (
        partition by artist_id
        order by unix_date(listening_date)
        range between 29 preceding and current row
    ) as track_count_30d
from daily_listening
order by artist_id, listening_date

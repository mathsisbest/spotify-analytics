with cluster_data as (
    select
        track_id,
        cluster_id,
        danceability,
        energy,
        valence,
        tempo,
        loudness,
        speechiness,
        acousticness,
        instrumentalness,
        liveness,
        key,
        mode,
        time_signature,
        duration_ms,
        run_id,
        trained_at
    from {{ source('marts', 'ml_cluster_assignments') }}
)

select
    cd.track_id,
    dt.track_name,
    cd.cluster_id,
    cd.danceability,
    cd.energy,
    cd.valence,
    cd.tempo,
    cd.loudness,
    cd.speechiness,
    cd.acousticness,
    cd.instrumentalness,
    cd.liveness,
    cd.key,
    cd.mode,
    cd.time_signature,
    cd.duration_ms,
    cd.run_id,
    cd.trained_at
from cluster_data as cd
left join {{ ref('dim_track') }} as dt
    on cd.track_id = dt.track_id

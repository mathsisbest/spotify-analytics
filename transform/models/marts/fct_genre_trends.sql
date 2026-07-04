with daily_listens as (
    select
        date(played_at) as listening_date,
        artist_name,
        artist_id
    from {{ ref('fct_listening') }}
),

artist_genres as (
    select
        artist_id,
        case
            when genres is not null and array_length(genres) > 0 then genres
            else [coalesce(artist_name, 'Unknown')]
        end as genre_array
    from {{ ref('dim_artist') }}
),

daily_genre_counts as (
    select
        dl.listening_date,
        g.genre
    from daily_listens as dl
    inner join artist_genres as ag
        on dl.artist_id = ag.artist_id
    cross join unnest(ag.genre_array) as g
),

aggregated as (
    select
        listening_date,
        genre,
        count(*) as listen_count
    from daily_genre_counts
    group by listening_date, genre
),

daily_totals as (
    select
        listening_date,
        sum(listen_count) as total_listens
    from aggregated
    group by listening_date
)

select
    a.listening_date,
    a.genre,
    a.listen_count,
    round(a.listen_count / nullif(dt.total_listens, 0), 6) as share_of_day
from aggregated as a
inner join daily_totals as dt
    on a.listening_date = dt.listening_date
order by a.listening_date desc, share_of_day desc

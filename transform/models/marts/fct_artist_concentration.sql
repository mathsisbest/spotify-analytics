with daily_artist_listens as (
    select
        date(played_at) as listening_date,
        artist_name,
        count(*) as listen_count
    from {{ ref('fct_listening') }}
    group by listening_date, artist_name
),

daily_totals as (
    select
        listening_date,
        sum(listen_count) as total_listens
    from daily_artist_listens
    group by listening_date
),

artist_shares as (
    select
        dal.listening_date,
        dal.artist_name,
        dal.listen_count,
        dt.total_listens,
        dal.listen_count / nullif(dt.total_listens, 0) as share_of_day,
        row_number() over (
            partition by dal.listening_date
            order by dal.listen_count desc
        ) as artist_rank
    from daily_artist_listens as dal
    inner join daily_totals as dt
        on dal.listening_date = dt.listening_date
)

select
    listening_date,
    total_listens,
    max(if(artist_rank = 1, artist_name, null)) as top_artist_name,
    coalesce(max(if(artist_rank = 1, share_of_day, null)), 0) as top_artist_share,
    coalesce(sum(if(artist_rank <= 5, share_of_day, 0)), 0) as top5_artist_concentration,
    round(coalesce(sum(share_of_day * share_of_day) * 10000, 0), 2) as hhi
from artist_shares
group by listening_date, total_listens
order by listening_date desc

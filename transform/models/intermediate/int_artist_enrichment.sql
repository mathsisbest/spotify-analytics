-- TODO (Phase 2): Enrich artists with genres, popularity, follower counts.
-- Source: raw.artist_data or Spotify Artist API data loaded into raw.
-- This is a shell to be fleshed out in Phase 2.

with artists as (
    select distinct
        artist_id,
        artist_name
    from {{ ref('stg_streaming_history') }}
)

select
    artist_id,
    artist_name
from artists

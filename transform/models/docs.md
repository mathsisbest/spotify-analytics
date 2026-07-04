{% docs doc__played_at %}
ISO-8601 timestamp indicating when the track playback ended, as reported by the
Spotify Web API. Used as the primary event timestamp for all time-based analysis.
{% enddocs %}

{% docs doc__track_id %}
Spotify track identifier — a unique base-62 string assigned by Spotify to every
track in their catalogue. Used as the primary key for joining listening events
with audio features and track metadata.
{% enddocs %}

{% docs doc__artist_id %}
Spotify artist identifier — a unique base-62 string assigned by Spotify to every
artist in their catalogue. Used as the primary key for artist-level aggregations
and enrichment.
{% enddocs %}

{% docs doc__duration_ms %}
Track duration in milliseconds as reported by the Spotify Audio Features API.
Convert to minutes by dividing by 60000.0 for human-readable listening totals.
{% enddocs %}

{% docs doc__audio_features %}
Audio features are perceptual and acoustic metrics computed by Spotify for each
track. They include danceability, energy, valence, tempo, loudness, and others —
each scored between 0.0 and 1.0 unless noted otherwise. These features enable
mood-based, genre-agnostic analysis of listening patterns.
{% enddocs %}

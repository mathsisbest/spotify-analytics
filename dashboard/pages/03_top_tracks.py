import pandas as pd
import streamlit as st

from dashboard.components import bar_chart, kpi_card
from dashboard.data import get_top_tracks

st.title("🎵 Top Track Analytics")
st.caption("Shylla's most played songs & streaming frequency")

limit = st.slider("Select Top N Tracks", min_value=5, max_value=30, value=10)

tracks = get_top_tracks(limit=limit)
if tracks:
    top_track = tracks[0]
    total_plays = sum(t["listen_count"] for t in tracks)

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_card("#1 Track", top_track["track_name"], help_text="Most played song")
    with col2:
        kpi_card("#1 Artist", top_track["artist_name"], help_text="Artist of top song")
    with col3:
        kpi_card("#1 Play Count", f"{top_track['listen_count']:,}", help_text="Times played")

    bar_chart(
        tracks,
        x="track_name",
        y="listen_count",
        title="Top Songs by Stream Count",
        height=400,
    )

    st.subheader("📋 Track Leaderboard")
    df = pd.DataFrame(tracks)
    if "minutes_listened" in df.columns:
        df["minutes_listened"] = df["minutes_listened"].round(1)
    display = df.rename(
        columns={
            "track_name": "Song Title",
            "artist_name": "Artist",
            "listen_count": "Streams",
            "minutes_listened": "Minutes Streamed",
        }
    )
    st.dataframe(display, hide_index=True, use_container_width=True)
else:
    st.info("No track data available.")

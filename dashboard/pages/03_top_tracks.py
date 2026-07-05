import pandas as pd
import streamlit as st

from dashboard.components import bar_chart
from dashboard.data import get_top_tracks

st.header("Top Tracks")

limit = st.slider("Number of tracks", min_value=5, max_value=25, value=10)

tracks = get_top_tracks(limit=limit)
if tracks:
    bar_chart(tracks, x="track_name", y="listen_count", title="Top Tracks by Listen Count")

    df = pd.DataFrame(tracks)
    display = df.rename(
        columns={
            "track_name": "Track",
            "artist_name": "Artist",
            "listen_count": "Listens",
        }
    )
    st.dataframe(display, hide_index=True)
else:
    st.info("No track data available.")

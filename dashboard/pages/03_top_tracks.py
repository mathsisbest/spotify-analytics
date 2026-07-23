import pandas as pd
import streamlit as st

from dashboard.components import bar_chart, grouped_bar_chart
from dashboard.data import get_dual_top_tracks, get_top_tracks

st.header("Top Tracks")

user_profile = st.session_state.get("user_profile", "Shylla (Personal) 🎵")
st.caption(f"Top track breakdown for **{user_profile}**")

limit = st.slider("Number of tracks", min_value=5, max_value=25, value=10)

if "Both" in user_profile:
    dual_tracks = get_dual_top_tracks(limit=limit)
    if dual_tracks:
        grouped_bar_chart(
            dual_tracks,
            x="track_name",
            y="listen_count",
            color="user",
            title="Top Tracks Comparison (Shylla Personal vs. Work)",
        )

        df = pd.DataFrame(dual_tracks)
        display = df.rename(
            columns={
                "track_name": "Track",
                "artist_name": "Artist",
                "listen_count": "Listens",
                "user": "Profile",
            }
        )
        st.dataframe(display, hide_index=True)
    else:
        st.info("No comparative track data available.")
else:
    tracks = get_top_tracks(limit=limit, user_profile=user_profile)
    if tracks:
        bar_chart(
            tracks,
            x="track_name",
            y="listen_count",
            title=f"Top Tracks by Listen Count ({user_profile})",
        )

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

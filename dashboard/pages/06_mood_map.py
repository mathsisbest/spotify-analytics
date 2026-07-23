import pandas as pd
import streamlit as st

from dashboard.components import radar_chart, scatter_chart
from dashboard.data import get_mood_map, get_user_audio_profiles

st.header("Audio Feature & Mood Analytics")
st.caption("Showing mood clusters & feature profile for **Shylla**")

categories, profiles = get_user_audio_profiles()
radar_chart(categories, profiles, title="🎧 Shylla's Audio Feature Fingerprint")

st.divider()
st.subheader("Interactive Mood Space (Energy × Danceability)")

mood = get_mood_map()

if mood:
    df = pd.DataFrame(mood)
    df["cluster"] = df["cluster_id"].astype(str)

    scatter_chart(
        df.to_dict(orient="records"),
        x="energy",
        y="danceability",
        color="cluster",
        title="Track Clustering by Energy & Danceability",
        hover_data=["track_name", "artist_name", "valence"],
    )

    st.subheader("Audio Feature Averages by Cluster")
    avg = df.groupby("cluster_id")[["danceability", "energy", "valence", "tempo"]].mean()
    avg.index = avg.index.map(int)
    st.dataframe(
        avg.round(3).rename_axis("Cluster"),
        use_container_width=True,
    )
else:
    st.info("No mood data available.")

import pandas as pd
import streamlit as st

from dashboard.components import radar_chart, scatter_chart
from dashboard.data import get_mood_map, get_user_audio_profiles

st.header("Audio Feature & Mood Analytics")
st.caption("Showing mood clusters & feature profile for **Shylla**")

raw_profiles = get_user_audio_profiles()
categories = ["valence", "energy", "danceability", "acousticness", "liveness"]
profiles = {name: [p[c] for c in categories] for name, p in raw_profiles.items()}
radar_chart(categories, profiles, title="🎧 Shylla's Audio Feature Fingerprint")

st.divider()
st.subheader("Interactive Mood Space (Energy × Danceability)")

mood = get_mood_map()

if mood:
    df = pd.DataFrame(mood)
    if "cluster_id" in df.columns:
        df["cluster"] = df["cluster_id"].astype(str)
    else:
        df["cluster"] = "0"
    scatter_chart(
        df=df.to_dict(orient="records"),
        x="valence",
        y="energy",
        color="cluster",
        title="Track Distribution in Mood Space",
        hover_data=["track_name", "artist_name"],
    )
else:
    st.info("No mood data available.")

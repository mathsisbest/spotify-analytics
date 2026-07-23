import pandas as pd
import streamlit as st

from dashboard.components import gauge_chart, radar_chart, scatter_chart
from dashboard.data import get_mood_map, get_taste_compatibility, get_user_audio_profiles

st.header("Audio Feature & Mood Analytics")

user_profile = st.session_state.get("user_profile", "Daniel 🎧")
st.caption(f"Showing mood clusters & feature profiles for **{user_profile}**")

col_radar, col_gauge = st.columns([1.6, 1])

with col_radar:
    categories, profiles = get_user_audio_profiles()
    radar_chart(categories, profiles, title="🎧 Listener Audio Feature Fingerprint")

with col_gauge:
    compat = get_taste_compatibility()
    gauge_chart(compat["compatibility_score"], title="Dual Taste Compatibility Match")
    st.markdown(f"**Shared Top Artists:** {', '.join(compat['shared_top_artists'])}")
    st.markdown(f"**Genre Overlap:** {', '.join(compat['genre_overlap'])}")

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

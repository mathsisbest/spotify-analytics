import pandas as pd
import streamlit as st

from dashboard.components import radar_chart, scatter_chart
from dashboard.data import get_mood_map, get_user_audio_profiles

st.title("🎨 Mood Space & Audio Fingerprint")
st.caption("Acoustic feature analysis & mood clustering for **Shylla**")

raw_profiles = get_user_audio_profiles()
categories = ["valence", "energy", "danceability", "acousticness", "liveness"]
profiles = {name: [p[c] for c in categories] for name, p in raw_profiles.items()}

col_radar, col_info = st.columns([1.6, 1])

with col_radar:
    radar_chart(categories, profiles, title="🎧 Audio Feature Radar Fingerprint", height=420)

with col_info:
    st.markdown("### Audio Profile Highlights")
    shylla_p = raw_profiles.get("Shylla", {})
    st.progress(
        float(shylla_p.get("energy", 0.7)),
        text=f"Energy ({shylla_p.get('energy', 0.7) * 100:.0f}%)",
    )
    st.progress(
        float(shylla_p.get("danceability", 0.65)),
        text=f"Danceability ({shylla_p.get('danceability', 0.65) * 100:.0f}%)",
    )
    st.progress(
        float(shylla_p.get("valence", 0.6)),
        text=f"Valence / Positivity ({shylla_p.get('valence', 0.6) * 100:.0f}%)",
    )
    st.progress(
        float(shylla_p.get("acousticness", 0.3)),
        text=f"Acousticness ({shylla_p.get('acousticness', 0.3) * 100:.0f}%)",
    )

st.divider()
st.subheader("🌌 Interactive Mood Space (Energy × Valence)")
st.caption("Valence (sad vs happy) vs. Energy (calm vs intense)")

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
        height=450,
        hover_data=["track_name", "artist_name"],
    )
else:
    st.info("No mood data available.")

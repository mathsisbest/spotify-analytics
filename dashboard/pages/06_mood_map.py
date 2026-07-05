import pandas as pd
import streamlit as st

from dashboard.components import scatter_chart
from dashboard.data import get_mood_map

st.header("Mood Map")

mood = get_mood_map()

if mood:
    df = pd.DataFrame(mood)
    df["cluster"] = df["cluster_id"].astype(str)

    scatter_chart(
        df.to_dict(orient="records"),
        x="energy",
        y="danceability",
        color="cluster",
        title="Energy × Danceability by Cluster",
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

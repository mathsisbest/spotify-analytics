import pandas as pd
import streamlit as st

from dashboard.components import bar_chart
from dashboard.data import get_top_artists

st.header("Top Artists")

limit = st.slider("Number of artists", min_value=5, max_value=25, value=10)

artists = get_top_artists(limit=limit)
if artists:
    bar_chart(artists, x="artist_name", y="listen_count", title="Top Artists by Listen Count")

    df = pd.DataFrame(artists)
    df["minutes_listened"] = df["minutes_listened"].round(1)
    display = df.rename(
        columns={
            "artist_name": "Artist",
            "listen_count": "Listens",
            "minutes_listened": "Minutes",
        }
    )
    st.dataframe(display, hide_index=True)
else:
    st.info("No artist data available.")

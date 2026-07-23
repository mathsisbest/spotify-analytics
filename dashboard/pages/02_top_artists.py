import pandas as pd
import streamlit as st

from dashboard.components import bar_chart, donut_chart
from dashboard.data import get_top_artists

st.header("Top Artists Analytics")
st.caption("Top artist listening breakdown for **Shylla**")

limit = st.slider("Number of artists", min_value=5, max_value=25, value=10)

artists = get_top_artists(limit=limit)
if artists:
    col_bar, col_donut = st.columns([1.5, 1])

    with col_bar:
        bar_chart(
            artists,
            x="artist_name",
            y="listen_count",
            title="Top Artists by Listen Count",
        )

    with col_donut:
        labels = [a["artist_name"] for a in artists[:6]]
        values = [a["listen_count"] for a in artists[:6]]
        donut_chart(labels, values, title="Artist Share (Top 6)")

    st.subheader("Detailed Listening Statistics")
    df = pd.DataFrame(artists)
    df["minutes_listened"] = df["minutes_listened"].round(1)
    display = df.rename(
        columns={
            "artist_name": "Artist",
            "listen_count": "Listens",
            "minutes_listened": "Minutes Listened",
        }
    )
    st.dataframe(display, hide_index=True, use_container_width=True)
else:
    st.info("No artist data available.")

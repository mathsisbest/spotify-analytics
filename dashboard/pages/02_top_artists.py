import pandas as pd
import streamlit as st

from dashboard.components import bar_chart, donut_chart, kpi_card
from dashboard.data import get_top_artists

st.title("🎤 Top Artists Intelligence")
st.caption("Artist listening concentration & distribution")

limit = st.slider("Select Top N Artists", min_value=5, max_value=30, value=10)

artists = get_top_artists(limit=limit)
if artists:
    top_artist = artists[0]
    total_listens = sum(a["listen_count"] for a in artists)
    top_share = (top_artist["listen_count"] / max(total_listens, 1)) * 100

    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    with col_kpi1:
        kpi_card("#1 Top Artist", top_artist["artist_name"], help_text="Most listened artist")
    with col_kpi2:
        kpi_card(
            "#1 Artist Streams",
            f"{top_artist['listen_count']:,}",
            help_text="Total plays for top artist",
        )
    with col_kpi3:
        kpi_card(
            "Top Artist Concentration",
            f"{top_share:.1f}%",
            help_text="Share of total top artist plays",
        )

    col_bar, col_donut = st.columns([1.6, 1])

    with col_bar:
        bar_chart(
            artists,
            x="artist_name",
            y="listen_count",
            title="Top Artists by Stream Count",
            height=420,
        )

    with col_donut:
        labels = [a["artist_name"] for a in artists[:6]]
        values = [float(a["listen_count"]) for a in artists[:6]]
        donut_chart(labels, values, title="Stream Share (Top 6 Artists)", height=420)

    st.subheader("📊 Detailed Artist Breakdown")
    df = pd.DataFrame(artists)
    df["minutes_listened"] = df["minutes_listened"].round(1)
    display = df.rename(
        columns={
            "artist_name": "Artist Name",
            "listen_count": "Total Plays",
            "minutes_listened": "Minutes Streamed",
        }
    )
    st.dataframe(display, hide_index=True, use_container_width=True)
else:
    st.info("No artist data available.")

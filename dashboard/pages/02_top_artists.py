import pandas as pd
import streamlit as st

from components import bar_chart, donut_chart, kpi_card
from data import get_top_artists

st.title("🎤 Top Artists Intelligence")
st.markdown("##### *Artist Affinity, Market Share & Listening Concentration*")
st.caption("Detailed breakdown of your most streamed artists and audience attention distribution.")

limit = st.slider("Select Top N Artists", min_value=5, max_value=30, value=10)

artists = get_top_artists(limit=limit)
if artists:
    top_artist = artists[0]
    total_listens = sum(a["listen_count"] for a in artists)
    top_share = (top_artist["listen_count"] / max(total_listens, 1)) * 100

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_card("#1 Top Artist", top_artist["artist_name"], help_text="Most listened artist")
    with col2:
        kpi_card(
            "#1 Artist Streams",
            f"{top_artist['listen_count']:,}",
            help_text="Total play count for #1 artist",
        )
    with col3:
        kpi_card(
            "Share Concentration",
            f"{top_share:.1f}%",
            help_text="Top artist share of total streams",
        )

    st.markdown("<br>", unsafe_allow_html=True)
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
        donut_chart(labels, values, title="Share Distribution (Top 6)", height=420)

    st.subheader("📋 Artist Ranking Leaderboard")
    df = pd.DataFrame(artists)
    df["minutes_listened"] = df["minutes_listened"].round(1)
    display = df.rename(
        columns={
            "artist_name": "Artist Name",
            "listen_count": "Total Streams",
            "minutes_listened": "Minutes Streamed",
        }
    )
    st.dataframe(display, hide_index=True, use_container_width=True)
    st.download_button(
        label="📥 Export Top Artists CSV",
        data=display.to_csv(index=False),
        file_name="top_artists.csv",
        mime="text/csv",
    )
else:
    st.info("No artist data available.")

from datetime import date, timedelta

import pandas as pd
import streamlit as st

from dashboard.components import area_chart, kpi_card
from dashboard.data import get_genre_trends

st.title("🎸 Genre & Artist Evolution")
st.caption("Tracking how Shylla's music preferences evolve over time")

today = date.today()
default_start = today - timedelta(days=90)

col_d1, col_d2 = st.columns(2)
with col_d1:
    start_date = st.date_input("Start date", value=default_start, key="genre_start")
with col_d2:
    end_date = st.date_input("End date", value=today, key="genre_end")

trends = get_genre_trends(start_date.isoformat(), end_date.isoformat())
if trends:
    df = pd.DataFrame(trends)
    unique_genres = df["genre"].nunique()
    top_genre_row = (
        df.groupby("genre")["listen_count"]
        .sum()
        .reset_index()
        .sort_values("listen_count", ascending=False)
        .iloc[0]
    )

    k1, k2 = st.columns(2)
    with k1:
        kpi_card(
            "#1 Top Genre / Artist",
            top_genre_row["genre"],
            help_text="Most listened genre category",
        )
    with k2:
        kpi_card(
            "Active Categories",
            str(unique_genres),
            help_text="Distinct genre categories in time range",
        )

    area_chart(
        trends,
        x="listening_date" if "listening_date" in trends[0] else "date",
        y="share" if "share" in trends[0] else "listen_count",
        color="genre",
        title="Genre Share Distribution Over Time",
        height=450,
    )
else:
    st.info("No genre trend data for the selected date range.")

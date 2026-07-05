from datetime import date, timedelta

import streamlit as st

from dashboard.components import area_chart
from dashboard.data import get_genre_trends

st.header("Genre Trends")

today = date.today()
default_start = today - timedelta(days=90)
start_date = st.date_input("Start date", value=default_start, key="genre_start")
end_date = st.date_input("End date", value=today, key="genre_end")

trends = get_genre_trends(start_date.isoformat(), end_date.isoformat())

if trends:
    area_chart(
        trends,
        x="listening_date",
        y="share",
        color="genre",
        title="Genre Share Over Time",
    )
else:
    st.info("No genre data for the selected date range.")

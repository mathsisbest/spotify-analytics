from datetime import date, timedelta

import streamlit as st

from dashboard.components import area_chart
from dashboard.data import get_genre_trends

st.header("Genre Trends")

user_profile = st.session_state.get("user_profile", "Daniel 🎧")
st.caption(f"Genre breakdown for **{user_profile}**")

today = date.today()
default_start = today - timedelta(days=90)
start_date = st.date_input("Start date", value=default_start, key="genre_start")
end_date = st.date_input("End date", value=today, key="genre_end")

if "Both" in user_profile:
    st.subheader("Daniel's Genre Share Over Time")
    d_trends = get_genre_trends(
        start_date.isoformat(), end_date.isoformat(), user_profile="Daniel 🎧"
    )
    if d_trends:
        area_chart(
            d_trends,
            x="listening_date",
            y="share",
            color="genre",
            title="Daniel's Genre Share Over Time",
        )

    st.subheader("Wife's Genre Share Over Time")
    w_trends = get_genre_trends(
        start_date.isoformat(), end_date.isoformat(), user_profile="Wife 🎵"
    )
    if w_trends:
        area_chart(
            w_trends,
            x="listening_date",
            y="share",
            color="genre",
            title="Wife's Genre Share Over Time",
        )
else:
    trends = get_genre_trends(
        start_date.isoformat(), end_date.isoformat(), user_profile=user_profile
    )
    if trends:
        area_chart(
            trends,
            x="listening_date",
            y="share",
            color="genre",
            title=f"Genre Share Over Time ({user_profile})",
        )
    else:
        st.info("No genre data for the selected date range.")

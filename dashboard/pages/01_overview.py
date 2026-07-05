from datetime import date, timedelta

import pandas as pd
import streamlit as st

from dashboard.components import kpi_card, time_series_chart
from dashboard.data import get_daily_summary, get_recent_tracks

st.header("Overview")

today = date.today()
default_start = today - timedelta(days=30)
start_date = st.date_input("Start date", value=default_start, key="overview_start")
end_date = st.date_input("End date", value=today, key="overview_end")

summary = get_daily_summary(start_date.isoformat(), end_date.isoformat())

if summary:
    total_minutes = sum(r["minutes_listened"] for r in summary)
    total_tracks = sum(r["track_count"] for r in summary)
    total_artists = sum(r["artist_count"] for r in summary)

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_card("Minutes Listened", f"{total_minutes:.0f}")
    with col2:
        kpi_card("Tracks Played", str(total_tracks))
    with col3:
        kpi_card("Unique Artists", str(total_artists))

    time_series_chart(
        summary,
        x="listening_date",
        y="minutes_listened",
        title="Daily Listening Minutes",
    )
else:
    st.info("No data for the selected date range.")

st.subheader("Recent Tracks")
recent = get_recent_tracks(limit=20)
if recent:
    df = pd.DataFrame(recent)
    df["played_at_display"] = pd.to_datetime(df["played_at"]).dt.strftime("%Y-%m-%d %H:%M")
    df["duration_s"] = (df["duration_ms"] / 1000).astype(int)
    display = df.rename(
        columns={
            "track_name": "Track",
            "artist_name": "Artist",
            "album_name": "Album",
            "played_at_display": "Played At",
            "duration_s": "Duration (s)",
        }
    )
    cols = ["Track", "Artist", "Album", "Played At", "Duration (s)"]
    st.dataframe(display[cols], hide_index=True)

from datetime import date, timedelta

import pandas as pd
import streamlit as st

from dashboard.components import kpi_card, time_series_chart
from dashboard.data import get_daily_summary, get_recent_tracks

st.title("🎧 Executive Overview")
st.caption("Real-time listening activity & streaming metrics")

today = date.today()
default_start = today - timedelta(days=30)

col_date1, col_date2 = st.columns(2)
with col_date1:
    start_date = st.date_input("Start date", value=default_start, key="overview_start")
with col_date2:
    end_date = st.date_input("End date", value=today, key="overview_end")

summary = get_daily_summary(start_date.isoformat(), end_date.isoformat())

if summary:
    total_minutes = sum(r["minutes_listened"] for r in summary)
    total_tracks = sum(r["track_count"] for r in summary)
    total_artists = sum(r.get("artist_count", r.get("unique_artists", 0)) for r in summary)
    avg_daily = total_minutes / max(len(summary), 1)

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        kpi_card(
            "Total Minutes", f"{total_minutes:,.0f}", help_text="Total listening time in minutes"
        )
    with kpi2:
        kpi_card("Tracks Streamed", f"{total_tracks:,}", help_text="Total song play count")
    with kpi3:
        kpi_card("Unique Artists", f"{total_artists:,}", help_text="Distinct musical artists")
    with kpi4:
        kpi_card("Daily Avg (Min)", f"{avg_daily:.1f}", help_text="Average daily listening volume")

    st.subheader("📈 Streaming Volume Trend")
    time_series_chart(
        summary,
        x="listening_date",
        y="minutes_listened",
        title="Daily Listening Volume (Minutes)",
        height=380,
    )
else:
    st.info("No listening data available for the selected date range.")

st.divider()
st.subheader("⚡ Live Stream Activity Feed")
st.caption("Latest songs ingested in real-time from Spotify API")

recent = get_recent_tracks(limit=15)
if recent:
    df = pd.DataFrame(recent)
    df["played_at_display"] = pd.to_datetime(df["played_at"]).dt.strftime("%Y-%m-%d %H:%M")
    df["duration_min"] = (df["duration_ms"] / 60000.0).round(1)
    display = df.rename(
        columns={
            "track_name": "Track Title",
            "artist_name": "Artist",
            "album_name": "Album",
            "played_at_display": "Timestamp",
            "duration_min": "Duration (min)",
        }
    )
    cols = ["Track Title", "Artist", "Album", "Timestamp", "Duration (min)"]
    st.dataframe(display[cols], hide_index=True, use_container_width=True)
else:
    st.info("No recent streams found.")

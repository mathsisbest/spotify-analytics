from datetime import date, timedelta

import pandas as pd
import streamlit as st

from components import kpi_card, time_series_chart
from data import get_daily_summary, get_recent_tracks

st.title("⚡ Executive Summary & Live Feed")
st.markdown("##### *Macro Streaming Trends & Ingestion Pipeline Feed*")
st.caption(
    "High-level overview of listening volume trends, stream counts, and real-time ingestion status."
)

today = date.today()
default_start = today - timedelta(days=30)

col_d1, col_d2 = st.columns(2)
with col_d1:
    start_date = st.date_input("Start date", value=default_start, key="exec_start")
with col_d2:
    end_date = st.date_input("End date", value=today, key="exec_end")

summary = get_daily_summary(start_date.isoformat(), end_date.isoformat())

if summary:
    total_minutes = sum(r["minutes_listened"] for r in summary)
    total_tracks = sum(r["track_count"] for r in summary)
    total_artists = sum(r.get("artist_count", r.get("unique_artists", 0)) for r in summary)
    avg_daily = total_minutes / max(len(summary), 1)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        kpi_card(
            "Total Minutes Streamed",
            f"{total_minutes:,.0f}",
            help_text="Total accumulated listening time",
        )
    with k2:
        kpi_card("Tracks Streamed", f"{total_tracks:,}", help_text="Total song playback events")
    with k3:
        kpi_card(
            "Distinct Artists", f"{total_artists:,}", help_text="Unique musical artists played"
        )
    with k4:
        kpi_card(
            "Daily Average Volume",
            f"{avg_daily:.1f} min",
            help_text="Average listening volume per day",
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📈 Listening Volume Trend")
    st.caption("Daily accumulated listening duration across the selected window.")
    time_series_chart(
        summary,
        x="listening_date",
        y="minutes_listened",
        title="Daily Listening Duration (Minutes)",
        height=380,
    )
else:
    st.info("No summary metrics available for the selected date range.")

st.divider()
st.subheader("⚡ Live Stream Activity Feed")
st.caption("Latest song plays ingested into BigQuery raw storage via Spotify Web API.")

recent = get_recent_tracks(limit=15)
if recent:
    df = pd.DataFrame(recent)
    df["played_at_display"] = pd.to_datetime(df["played_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    df["duration_min"] = (df["duration_ms"] / 60000.0).round(2)
    display = df.rename(
        columns={
            "track_name": "Track Title",
            "artist_name": "Artist",
            "album_name": "Album",
            "played_at_display": "Played At (UTC)",
            "duration_min": "Duration (min)",
        }
    )
    cols = ["Track Title", "Artist", "Album", "Played At (UTC)", "Duration (min)"]
    st.dataframe(display[cols], hide_index=True, use_container_width=True)
else:
    st.info("No recent streams found.")

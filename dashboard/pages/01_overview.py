from datetime import date, timedelta

import pandas as pd
import streamlit as st

from dashboard.components import gauge_chart, kpi_card, time_series_chart
from dashboard.data import (
    get_daily_summary,
    get_recent_tracks,
    get_taste_compatibility,
)

st.header("Overview")

user_profile = st.session_state.get("user_profile", "Shylla (Personal) 🎵")
st.caption(f"Active Listener Profile: **{user_profile}**")

today = date.today()
default_start = today - timedelta(days=30)
start_date = st.date_input("Start date", value=default_start, key="overview_start")
end_date = st.date_input("End date", value=today, key="overview_end")

if "Both" in user_profile:
    st.subheader("Shylla's Dual Listening Taste Profile")
    compat = get_taste_compatibility()
    gauge_col, info_col = st.columns([1, 1])
    with gauge_col:
        gauge_chart(
            value=compat["compatibility_score"],
            title="Profile Alignment Score",
        )
    with info_col:
        st.markdown("### Top Shared Favorites Across Profiles")
        st.markdown("**Shared Top Artists:** " + ", ".join(compat["shared_top_artists"]))
        st.markdown("**Overlapping Genres:** " + ", ".join(compat["genre_overlap"]))
        st.info(
            "High alignment on Indie Pop and Synthwave between "
            "Personal and Work listening sessions."
        )

    st.subheader("Comparative Listening Volume")
    p_summary = get_daily_summary(
        start_date.isoformat(),
        end_date.isoformat(),
        user_profile="Shylla (Personal) 🎵",
    )
    w_summary = get_daily_summary(
        start_date.isoformat(),
        end_date.isoformat(),
        user_profile="Shylla (Work) 🎧",
    )

    p_min = sum(r["minutes_listened"] for r in p_summary) if p_summary else 0
    w_min = sum(r["minutes_listened"] for r in w_summary) if w_summary else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_card("Personal Listening Min", f"{p_min:.0f}")
    with col2:
        kpi_card("Work Listening Min", f"{w_min:.0f}")
    with col3:
        kpi_card(
            "Total Combined Min",
            f"{(p_min + w_min):.0f}",
        )
    with col4:
        kpi_card(
            "Primary Listening Focus",
            "Personal (+12%)" if p_min >= w_min else "Work (+12%)",
        )

    time_series_chart(
        p_summary,
        x="listening_date",
        y="minutes_listened",
        title="Shylla (Personal) Daily Listening Minutes",
    )
else:
    summary = get_daily_summary(
        start_date.isoformat(), end_date.isoformat(), user_profile=user_profile
    )

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
            kpi_card("Artist Appearances", str(total_artists))

        time_series_chart(
            summary,
            x="listening_date",
            y="minutes_listened",
            title=f"Daily Listening Minutes ({user_profile})",
        )
    else:
        st.info("No data for the selected date range.")

st.subheader(f"Recent Tracks ({user_profile})")
recent = get_recent_tracks(limit=20, user_profile=user_profile)
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

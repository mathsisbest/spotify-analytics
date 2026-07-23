import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

import dashboard.theme  # noqa: F401
from dashboard.components import radar_chart
from dashboard.data import (
    get_forecast,
    get_recommendations,
    get_user_audio_profiles,
)

st.header("ML Insights")

user_profile = st.session_state.get("user_profile", "Shylla (Personal) 🎵")
st.caption(f"Machine learning predictions & recommendations for **{user_profile}**")

st.subheader("Audio Feature Radar Comparison")
categories, profiles = get_user_audio_profiles()

if "Both" in user_profile:
    radar_chart(
        categories=categories,
        profiles=profiles,
        title="Dual Audio Feature Profile Comparison (Shylla Personal vs Work)",
    )
else:
    active_profile_key = (
        "Shylla (Personal) 🎵" if "Personal" in user_profile else "Shylla (Work) 🎧"
    )
    single_profile = {
        active_profile_key: profiles.get(active_profile_key, profiles["Shylla (Personal) 🎵"])
    }
    radar_chart(
        categories=categories,
        profiles=single_profile,
        title=f"Audio Feature Profile ({user_profile})",
    )

st.subheader("Listening Forecast (14 days)")

forecast = get_forecast(user_profile=user_profile)
if forecast:
    dates = [r["forecast_date"] for r in forecast]
    predicted = [r["predicted_minutes"] for r in forecast]
    lower = [r["lower_bound"] for r in forecast]
    upper = [r["upper_bound"] for r in forecast]

    template_name = "spotify" if "spotify" in pio.templates else "plotly_dark"

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=upper,
            mode="lines",
            line=dict(width=0),
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=lower,
            mode="lines",
            line=dict(width=0),
            fillcolor="rgba(29,185,84,0.2)",
            fill="tonexty",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=predicted,
            mode="lines+markers",
            line=dict(color="#1DB954", width=2),
            name="Predicted Minutes",
        )
    )
    fig.update_layout(
        title=f"Daily Listening Minutes (14-Day Forecast - {user_profile})",
        template=template_name,
        height=500,
        yaxis_title="Minutes",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No forecast data available.")

st.subheader("Recommended Tracks")
recs = get_recommendations(user_profile=user_profile)
if recs:
    rows = [
        {
            "Track": r["track_name"],
            "Artist": r["artist_name"],
            "Score": f"{r['score']:.2f}",
            "Why": r["reason"],
        }
        for r in recs
    ]
    st.dataframe(rows, hide_index=True)
else:
    st.info("No recommendations available.")

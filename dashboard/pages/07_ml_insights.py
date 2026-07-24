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
st.caption("Machine learning predictions & recommendations for **Shylla**")

st.subheader("Audio Feature Profile")
raw_profiles = get_user_audio_profiles()
categories = ["valence", "energy", "danceability", "acousticness", "liveness"]
profiles = {name: [p[c] for c in categories] for name, p in raw_profiles.items()}
radar_chart(
    categories=categories,
    profiles=profiles,
    title="Shylla's Audio Feature Profile",
)

st.subheader("Listening Forecast (14 days)")

forecast = get_forecast()

if forecast:
    dates = [f["date"] for f in forecast]
    yhat = [f["predicted_minutes"] for f in forecast]
    lower = [f["lower_bound"] for f in forecast]
    upper = [f["upper_bound"] for f in forecast]

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
            fill="tonexty",
            fillcolor="rgba(29, 185, 84, 0.15)",
            name="Confidence Interval",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=yhat,
            mode="lines+markers",
            line=dict(color="#1DB954", width=3),
            name="Forecasted Minutes",
        )
    )
    template = "spotify" if "spotify" in pio.templates else "plotly_dark"
    fig.update_layout(
        title="Predicted Listening Minutes (Next 14 Days)",
        xaxis_title="Date",
        yaxis_title="Minutes",
        template=template,
        height=450,
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No forecast data available.")

st.divider()
st.subheader("Recommended Tracks")

recs = get_recommendations()

if recs:
    for rec in recs:
        st.markdown(
            f"🎵 **{rec['track_name']}** by *{rec['artist_name']}*\n"
            f"   - {rec['reason']} (Score: {rec['score']:.2f})"
        )
else:
    st.info("No recommendations available.")

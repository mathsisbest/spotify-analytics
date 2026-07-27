from datetime import datetime

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

import dashboard.theme  # noqa: F401
from dashboard.components import kpi_card
from dashboard.data import export_playlist, get_forecast, get_recommendations

st.title("🤖 Predictive AI & Smart Recommendations")
st.markdown("##### *Time-Series Volume Forecasting & Cosine Vector Playlist Generation*")
st.caption(
    "Scikit-Learn ML models forecasting daily streaming volume and generating vector-matched playlist recommendations."
)

forecast = get_forecast()

if forecast:
    dates = [f["date"] for f in forecast]
    yhat = [f["predicted_minutes"] for f in forecast]
    lower = [f["lower_bound"] for f in forecast]
    upper = [f["upper_bound"] for f in forecast]

    total_pred = sum(yhat)
    avg_pred = total_pred / max(len(yhat), 1)

    k1, k2 = st.columns(2)
    with k1:
        kpi_card(
            "14-Day Predicted Total Volume",
            f"{total_pred:,.0f} min",
            help_text="Total predicted listening minutes over next 14 days",
        )
    with k2:
        kpi_card(
            "Predicted Daily Average",
            f"{avg_pred:.1f} min/day",
            help_text="Expected daily average listening volume",
        )

    st.markdown("<br>", unsafe_allow_html=True)
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
            name="95% Confidence Interval",
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
        title="Predicted Daily Listening Volume (Next 14 Days)",
        xaxis_title="Date",
        yaxis_title="Minutes",
        template=template,
        height=420,
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No forecast model available.")

st.divider()
st.subheader("💡 Algorithmic Playlist Recommendations (Cosine Similarity)")
st.caption(
    "Personalized song recommendations generated via 12-dimensional acoustic feature vector matching."
)

recs = get_recommendations()

if recs:
    for rec in recs:
        with st.container():
            col_rec, col_score = st.columns([4, 1])
            with col_rec:
                st.markdown(f"🎵 **{rec['track_name']}** by *{rec['artist_name']}*")
                st.caption(rec["reason"])
            with col_score:
                st.caption(f"Vector Similarity: **{rec.get('score', 0.95):.2f}**")

    st.markdown("<br>", unsafe_allow_html=True)

    track_ids = [
        r.get("track_id", f"track_{i}")
        for i, r in enumerate(recs)
        if r.get("track_id") or r.get("track_name")
    ]
    playlist_name = f"Resonance Mix — {datetime.now().strftime('%Y-%m-%d')}"

    if st.button("🎧 Export Recommendations as Spotify Playlist", type="primary"):
        url = export_playlist(track_ids, playlist_name)
        if url:
            st.success(
                f"🎉 Playlist successfully created on your Spotify account! [Open Playlist in Spotify]({url})"
            )
        else:
            st.error("Failed to create playlist. Ensure Spotify credentials are valid.")
else:
    st.info("No recommendations available.")

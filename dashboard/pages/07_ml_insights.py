import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

import dashboard.theme  # noqa: F401
from dashboard.components import kpi_card
from dashboard.data import get_forecast, get_recommendations

st.title("🤖 Predictive AI & Smart Insights")
st.caption("Time-series volume forecasting & algorithmic track recommendations")

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
st.subheader("💡 Algorithmic Recommendations")
st.caption("Personalized song recommendations based on acoustic feature similarity")

recs = get_recommendations()

if recs:
    for rec in recs:
        with st.container():
            col_rec, col_score = st.columns([4, 1])
            with col_rec:
                st.markdown(f"🎵 **{rec['track_name']}** by *{rec['artist_name']}*")
                st.caption(rec["reason"])
            with col_score:
                st.metric("Match Score", f"{rec['score'] * 100:.0f}%")
else:
    st.info("No recommendations available.")

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from dashboard.data import get_recent_tracks
from ml.mood_transitions import build_mood_transition_matrix

st.title("🔄 Mood Transitions")
st.caption("Markov Chain Analysis of Listening Mood Shifts")

tracks = get_recent_tracks(limit=100)
if not tracks:
    st.info("No listening history available to calculate mood transitions.")
else:
    transitions = build_mood_transition_matrix(tracks)
    states = transitions["states"]
    matrix = transitions["transition_matrix"]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Transition Matrix Heatmap")
        df_mat = pd.DataFrame(matrix, index=states, columns=states)
        fig = go.Figure(
            data=go.Heatmap(
                z=df_mat.values,
                x=states,
                y=states,
                colorscale="Viridis",
                text=df_mat.values.round(2),
                texttemplate="%{text}",
            )
        )
        fig.update_layout(
            xaxis_title="Next Mood",
            yaxis_title="Current Mood",
            paper_bgcolor="#191414",
            plot_bgcolor="#191414",
            font=dict(color="#FFFFFF"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🌊 Mood Flow (Sankey Diagram)")
        sources = []
        targets = []
        values = []
        for i in range(4):
            for j in range(4):
                if matrix[i][j] > 0:
                    sources.append(i)
                    targets.append(j + 4)
                    values.append(matrix[i][j])

        labels = [f"From: {s}" for s in states] + [f"To: {s}" for s in states]

        fig_sankey = go.Figure(
            data=go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=labels,
                    color="#1DB954",
                ),
                link=dict(
                    source=sources,
                    target=targets,
                    value=values,
                    color="rgba(29, 185, 84, 0.4)",
                ),
            )
        )
        fig_sankey.update_layout(
            paper_bgcolor="#191414",
            plot_bgcolor="#191414",
            font=dict(color="#FFFFFF"),
        )
        st.plotly_chart(fig_sankey, use_container_width=True)

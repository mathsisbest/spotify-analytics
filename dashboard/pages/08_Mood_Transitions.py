import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data import get_recent_tracks
from ml.mood_transitions import build_mood_transition_matrix

st.title("🔄 Mood Transitions & Markov Chain Flow")
st.markdown("##### *Stochastic Modeling of Audio Mood Trajectories*")
st.caption(
    "Analyzing state-transition probabilities across Euphoric, Chill, Intense, and Melancholic mood states."
)

tracks = get_recent_tracks(limit=100)
if not tracks:
    st.info("No listening history available to calculate mood transition probabilities.")
else:
    transitions = build_mood_transition_matrix(tracks)
    states = transitions["states"]
    matrix = transitions["transition_matrix"]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Transition Probability Matrix")
        st.caption("Likelihood of transitioning from state A to state B.")
        df_mat = pd.DataFrame(matrix, index=states, columns=states)
        fig = go.Figure(
            data=go.Heatmap(
                z=df_mat.values,
                x=states,
                y=states,
                colorscale="Greens",
                text=df_mat.values.round(2),
                texttemplate="%{text}",
            )
        )
        fig.update_layout(
            xaxis_title="Next Mood State",
            yaxis_title="Current Mood State",
            paper_bgcolor="#181818",
            plot_bgcolor="#181818",
            font=dict(color="#FFFFFF"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🌊 Mood Flow (Sankey Diagram)")
        st.caption("Directional flow of listening sessions between mood quadrants.")
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
                    line=dict(color="#282828", width=0.5),
                    label=labels,
                    color="#1DB954",
                ),
                link=dict(
                    source=sources,
                    target=targets,
                    value=values,
                    color="rgba(29, 185, 84, 0.3)",
                ),
            )
        )
        fig_sankey.update_layout(
            paper_bgcolor="#181818",
            plot_bgcolor="#181818",
            font=dict(color="#FFFFFF"),
        )
        st.plotly_chart(fig_sankey, use_container_width=True)

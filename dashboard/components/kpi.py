import streamlit as st

SPOTIFY_GREEN = "#1DB954"


def kpi_card(
    label: str,
    value: str,
    delta: str | None = None,
    help_text: str | None = None,
) -> None:
    st.metric(label=label, value=value, delta=delta, delta_color="normal", help=help_text)

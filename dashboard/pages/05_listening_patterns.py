from typing import Any

import streamlit as st

from dashboard.components import heatmap_chart
from dashboard.data import get_listening_heatmap

st.header("Listening Patterns")

user_profile = st.session_state.get("user_profile", "Shylla (Personal) 🎵")
st.caption(f"Listening activity breakdown for **{user_profile}**")

days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
hours = [f"{h:02d}:00" for h in range(24)]


def _render_single_heatmap(data: list[dict[str, Any]], title: str) -> None:
    z: list[list[float]] = [[0.0] * 24 for _ in range(7)]
    for row in data:
        z[row["day_of_week"]][row["hour_of_day"]] = row["minutes"]

    heatmap_chart(z, x=hours, y=days, title=title)

    by_hour: dict[int, list[float]] = {}
    for row in data:
        by_hour.setdefault(row["hour_of_day"], []).append(row["minutes"])
    peak_hour = max(by_hour, key=lambda h: sum(by_hour[h]) / len(by_hour[h]))
    quiet_hour = min(by_hour, key=lambda h: sum(by_hour[h]) / len(by_hour[h]))

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Peak Listening Hour", f"{peak_hour:02d}:00")
    with col2:
        st.metric("Quietest Hour", f"{quiet_hour:02d}:00")


if "Both" in user_profile:
    st.subheader("Shylla (Personal) Activity Heatmap")
    p_data = get_listening_heatmap(user_profile="Shylla (Personal) 🎵")
    if p_data:
        _render_single_heatmap(p_data, title="Shylla (Personal) Listening Activity (Day × Hour)")

    st.subheader("Shylla (Work) Activity Heatmap")
    w_data = get_listening_heatmap(user_profile="Shylla (Work) 🎧")
    if w_data:
        _render_single_heatmap(w_data, title="Shylla (Work) Listening Activity (Day × Hour)")
else:
    data = get_listening_heatmap(user_profile=user_profile)
    if data:
        _render_single_heatmap(data, title=f"Listening Activity ({user_profile}) (Day × Hour)")
    else:
        st.info("No listening pattern data available.")

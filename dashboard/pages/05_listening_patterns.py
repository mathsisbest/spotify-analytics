import streamlit as st

from dashboard.components import heatmap_chart
from dashboard.data import get_listening_heatmap

st.header("Listening Patterns")

data = get_listening_heatmap()

if data:
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    hours = [f"{h:02d}:00" for h in range(24)]
    z: list[list[float]] = [[0.0] * 24 for _ in range(7)]
    for row in data:
        z[row["day_of_week"]][row["hour_of_day"]] = row["minutes"]

    heatmap_chart(z, x=hours, y=days, title="Listening Activity (Day × Hour)")

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
else:
    st.info("No listening pattern data available.")

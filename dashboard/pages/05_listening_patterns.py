import streamlit as st

from dashboard.components import heatmap_chart, kpi_card
from dashboard.data import get_listening_heatmap

st.title("🕒 Listening Rhythms & Heatmaps")
st.caption("Day × Hour activity patterns identifying peak listening windows")

data = get_listening_heatmap()

if data:
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    hours = [f"{h:02d}:00" for h in range(24)]
    z: list[list[float]] = [[0.0] * 24 for _ in range(7)]

    for row in data:
        dow = int(row.get("day_of_week", 0))
        hod = int(row.get("hour_of_day", row.get("hour", 0)))
        val = float(row.get("minutes", row.get("listen_count", 0)))
        if 0 <= dow < 7 and 0 <= hod < 24:
            z[dow][hod] += val

    heatmap_chart(
        z, x=hours, y=days, title="Weekly Listening Activity Heatmap (Day × Hour)", height=450
    )

    by_hour: dict[int, float] = {}
    for row in data:
        hod = int(row.get("hour_of_day", row.get("hour", 0)))
        val = float(row.get("minutes", row.get("listen_count", 0)))
        by_hour[hod] = by_hour.get(hod, 0.0) + val

    if by_hour:
        peak_h = max(by_hour, key=lambda h: by_hour[h])
        quiet_h = min(by_hour, key=lambda h: by_hour[h])

        col1, col2 = st.columns(2)
        with col1:
            kpi_card(
                "Peak Listening Window",
                f"{peak_h:02d}:00 - {peak_h + 1:02d}:00",
                help_text="Hour with highest streaming volume",
            )
        with col2:
            kpi_card(
                "Quietest Listening Window",
                f"{quiet_h:02d}:00 - {quiet_h + 1:02d}:00",
                help_text="Hour with lowest streaming volume",
            )
else:
    st.info("No listening pattern data available.")

import pandas as pd
import streamlit as st

from dashboard.components import bar_chart, kpi_card
from dashboard.data import get_top_tracks

st.title("🎵 Top Tracks Intelligence")
st.markdown("##### *Most Streamed Songs & Playback Frequencies*")
st.caption("Deep dive into your most played individual tracks across your streaming history.")

limit = st.slider("Select Top N Tracks", min_value=5, max_value=30, value=10)

tracks = get_top_tracks(limit=limit)
if tracks:
    top_track = tracks[0]
    total_plays = sum(t["listen_count"] for t in tracks)

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_card("#1 Track Title", top_track["track_name"], help_text="Most streamed track overall")
    with col2:
        kpi_card(
            "#1 Track Artist", top_track["artist_name"], help_text="Artist performing top track"
        )
    with col3:
        kpi_card(
            "#1 Play Count",
            f"{top_track['listen_count']:,}",
            help_text="Total play count for top track",
        )

    st.markdown("<br>", unsafe_allow_html=True)
    bar_chart(
        tracks,
        x="track_name",
        y="listen_count",
        title="Top Songs by Stream Count",
        height=400,
    )

    st.subheader("📋 Track Performance Leaderboard")
    df = pd.DataFrame(tracks)
    if "minutes_listened" in df.columns:
        df["minutes_listened"] = df["minutes_listened"].round(1)
    display = df.rename(
        columns={
            "track_name": "Song Title",
            "artist_name": "Artist",
            "listen_count": "Streams",
            "minutes_listened": "Minutes Streamed",
        }
    )
    st.dataframe(display, hide_index=True, use_container_width=True)
    st.download_button(
        label="📥 Export Top Tracks CSV",
        data=display.to_csv(index=False),
        file_name="top_tracks.csv",
        mime="text/csv",
    )
else:
    st.info("No track performance data available.")

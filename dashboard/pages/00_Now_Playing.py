import time

import streamlit as st

from dashboard.data import get_now_playing

st.title("🎵 Currently Playing")
st.markdown("##### *Live Real-Time Playback & Session Telemetry*")
st.caption("Direct telemetry feed from your active Spotify session via Spotify Web API.")

placeholder = st.empty()
now = get_now_playing()

if now and now.get("is_playing"):
    with placeholder.container():
        st.markdown(
            """
            <div style="background-color: #181818; border: 1px solid #1DB954; border-radius: 12px; padding: 24px; margin-bottom: 20px;">
            """,
            unsafe_allow_html=True,
        )
        col_art, col_info = st.columns([1, 2.2])
        with col_art:
            if now.get("album_art_url"):
                st.image(now["album_art_url"], use_container_width=True)
        with col_info:
            st.markdown(f"# {now['track_name']}")
            st.markdown(f"### **{now['artist_name']}**")
            st.markdown(f"##### *Album: {now['album_name']}*")

            st.markdown("<br>", unsafe_allow_html=True)
            progress = now["progress_ms"] / max(now["duration_ms"], 1)
            st.progress(progress)

            elapsed = now["progress_ms"] // 1000
            total = now["duration_ms"] // 1000
            st.markdown(
                f"<div style='display: flex; justify-content: space-between; color: #B3B3B3; font-weight: 700; font-size: 0.9rem;'>"
                f"<span>⏱️ {elapsed // 60}:{elapsed % 60:02d}</span>"
                f"<span>Track ID: <code>{now['track_id']}</code></span>"
                f"<span>⏳ {total // 60}:{total % 60:02d}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)
    time.sleep(5)
    st.rerun()
else:
    st.info(
        "🎧 No active Spotify playback detected. Start playing a song on Spotify to see live telemetry here!"
    )

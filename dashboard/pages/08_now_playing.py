import time

import streamlit as st

from dashboard.data import get_now_playing

st.title("🎵 Now Playing")
st.caption("Live from your Spotify session")

placeholder = st.empty()

now = get_now_playing()

if now and now.get("is_playing"):
    with placeholder.container():
        col_art, col_info = st.columns([1, 2])
        with col_art:
            if now.get("album_art_url"):
                st.image(now["album_art_url"], width=250)
        with col_info:
            st.markdown(f"### {now['track_name']}")
            st.markdown(f"**{now['artist_name']}** — *{now['album_name']}*")
            progress = now["progress_ms"] / max(now["duration_ms"], 1)
            st.progress(progress)
            elapsed = now["progress_ms"] // 1000
            total = now["duration_ms"] // 1000
            st.caption(f"{elapsed // 60}:{elapsed % 60:02d} / {total // 60}:{total % 60:02d}")
    time.sleep(5)
    st.rerun()
else:
    st.info("No active Spotify playback detected.")

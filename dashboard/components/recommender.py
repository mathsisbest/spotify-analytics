from typing import Any

import streamlit as st


def show_recommendations(tracks: list[dict[str, Any]] | None = None) -> None:
    if not tracks:
        st.info("No recommendations yet. Train the model to see suggestions.")
        return

    for t in tracks:
        st.markdown(f"**{t['track_name']}** — {t['artist_name']}")
        if "preview_url" in t and t["preview_url"]:
            st.audio(t["preview_url"])

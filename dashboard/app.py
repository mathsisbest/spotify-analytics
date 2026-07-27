import sys
from pathlib import Path

import streamlit as st

_repo_root = str(Path(__file__).resolve().parent.parent)
_src = str(Path(__file__).resolve().parent.parent / "src")
for p in [_repo_root, _src]:
    if p not in sys.path:
        sys.path.insert(0, p)

st.set_page_config(
    page_title="Resonance — Spotify Music Intelligence Studio",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded",
)

spotify_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Circular+Std:wght@400;500;700;900&family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Spotify Dark Theme Palette */
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid #282828;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
    }

    /* Card Panels */
    .spotify-card {
        background-color: #181818;
        border: 1px solid #282828;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 16px;
        transition: background-color 0.2s ease, border-color 0.2s ease;
    }

    .spotify-card:hover {
        background-color: #282828;
        border-color: #1DB954;
    }

    /* Metric Cards Glassmorphism & Spotify Green accent */
    div[data-testid="stMetric"] {
        background-color: #181818;
        border: 1px solid #282828;
        border-radius: 8px;
        padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        transition: transform 0.2s ease, border-color 0.2s ease, background-color 0.2s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        background-color: #282828;
        border-color: #1DB954;
    }

    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 900 !important;
        color: #1DB954 !important;
        letter-spacing: -0.5px;
    }

    div[data-testid="stMetricLabel"] {
        color: #B3B3B3 !important;
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Spotify Green Primary Pill Buttons */
    .stButton>button {
        background-color: #1DB954 !important;
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 0.9rem !important;
        border-radius: 50px !important;
        border: none !important;
        padding: 12px 28px !important;
        letter-spacing: 0.2px;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 4px 14px rgba(29, 185, 84, 0.3);
    }

    .stButton>button:hover {
        background-color: #1ed760 !important;
        color: #000000 !important;
        transform: scale(1.04);
        box-shadow: 0 6px 20px rgba(30, 215, 96, 0.5);
    }

    /* Streamlit Dataframe Headers & Table */
    div[data-testid="stDataFrame"] {
        background-color: #181818;
        border: 1px solid #282828;
        border-radius: 8px;
    }

    /* Headings Accent */
    h1, h2, h3 {
        color: #FFFFFF;
        font-weight: 800;
        letter-spacing: -0.5px;
    }

    /* Tabs Styling */
    button[data-baseweb="tab"] {
        font-weight: 700 !important;
        color: #B3B3B3 !important;
    }

    button[aria-selected="true"] {
        color: #1DB954 !important;
        border-bottom-color: #1DB954 !important;
    }
    </style>
"""
st.markdown(spotify_css, unsafe_allow_html=True)

# Sidebar Branding
st.sidebar.markdown(
    """
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
        <div style="background-color: #1DB954; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: 900; color: #000000;">
            ⚡
        </div>
        <div>
            <h2 style="color: #FFFFFF; font-size: 1.3rem; font-weight: 900; margin: 0;">Resonance</h2>
            <p style="color: #1DB954; font-size: 0.75rem; font-weight: 700; margin: 0; text-transform: uppercase; letter-spacing: 0.8px;">
                Spotify Intelligence Studio
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.divider()

st.sidebar.markdown(
    """
    <div style="background: #181818;
                border-left: 4px solid #1DB954;
                padding: 12px;
                border-radius: 6px;
                margin-bottom: 20px;">
        <span style="font-size: 0.75rem; color: #1ED760; font-weight: 800; text-transform: uppercase;">
            🟢 LIVE GCP DATA PIPELINE
        </span><br>
        <span style="font-size: 0.75rem; color: #B3B3B3;">
            BigQuery · dbt Medallion · Scikit-Learn ML
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)

from dashboard.data import get_last_ingestion_run  # noqa: E402

last_run = get_last_ingestion_run()
if last_run:
    status_icon = "🟢" if last_run["status"] == "success" else "🔴"
    time_str = last_run["started_at"][:19] if last_run["started_at"] else "Unknown"
    st.sidebar.markdown(
        f"""
        <div style="font-size: 0.75rem; color: #B3B3B3;
                    border-top: 1px solid #282828;
                    padding-top: 12px; margin-top: 12px;">
            <span style="color: #FFFFFF; font-weight: 700;">{status_icon} Pipeline Status: {last_run["status"].upper()}</span><br/>
            <span>Last Ingestion: {time_str}</span><br/>
            <span>Ingested Rows: {last_run["tracks_ingested"]}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.sidebar.caption("Powered by Spotify Web API & Google Cloud")

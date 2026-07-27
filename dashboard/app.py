import streamlit as st

st.set_page_config(
    page_title="Resonance — Spotify Analytics & BI Studio",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .stApp {
        background: linear-gradient(180deg, #121212 0%, #080808 100%);
        color: #FFFFFF;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #181818 !important;
        border-right: 1px solid #282828;
    }

    /* Metric Cards Glassmorphism */
    div[data-testid="stMetric"] {
        background: rgba(40, 40, 40, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: rgba(29, 185, 84, 0.5);
    }

    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #1DB954 !important;
        letter-spacing: -0.5px;
    }

    div[data-testid="stMetricLabel"] {
        color: #B3B3B3 !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Buttons & Inputs */
    .stButton>button {
        background-color: #1DB954 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 50px !important;
        border: none !important;
        padding: 10px 24px !important;
        transition: all 0.2s ease !important;
    }

    .stButton>button:hover {
        background-color: #1ed760 !important;
        transform: scale(1.03);
    }

    /* Responsive Mobile Tweaks */
    @media (max-width: 768px) {
        div[data-testid="stMetricValue"] {
            font-size: 1.6rem !important;
        }
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

st.sidebar.markdown(
    """
    <div style="text-align: center; padding: 10px 0;">
        <h2 style="color: #1DB954; font-weight: 800; margin: 0;">🎵 Resonance</h2>
        <p style="color: #B3B3B3; font-size: 0.85rem; margin-top: 4px;">
            Cloud-Native Music Intelligence
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.divider()
st.sidebar.markdown(
    """
    <div style="background: rgba(29,185,84,0.1);
                border-left: 4px solid #1DB954;
                padding: 12px;
                border-radius: 6px;
                margin-bottom: 20px;">
        <span style="font-size: 0.8rem; color: #1ED760; font-weight: 700;">
            LIVE GCP PIPELINE
        </span><br>
        <span style="font-size: 0.75rem; color: #CCCCCC;">
            BigQuery · dbt · Cloud Functions
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.caption("Powered by Spotify Web API & GCP BigQuery")

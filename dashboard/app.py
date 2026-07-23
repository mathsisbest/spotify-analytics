import streamlit as st

st.set_page_config(
    page_title="Shylla's Spotify Analytics",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

custom_css = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp {
        background-color: #121212;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: #1DB954 !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #B3B3B3 !important;
        font-weight: 500 !important;
    }
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

st.sidebar.title("🎵 Shylla's Spotify Analytics")
st.sidebar.markdown("Cloud-Native Listening Insights for Shylla 🎵")
st.sidebar.divider()
st.sidebar.caption("Built with Streamlit · Powered by BigQuery & dbt")

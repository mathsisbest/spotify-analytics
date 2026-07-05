import streamlit as st

st.set_page_config(
    page_title="Spotify Analytics",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.sidebar.title("Spotify Analytics")
st.sidebar.markdown("Your personal listening dashboard")
st.sidebar.divider()

st.sidebar.markdown("---")
st.sidebar.caption("Built with Streamlit · Powered by BigQuery")

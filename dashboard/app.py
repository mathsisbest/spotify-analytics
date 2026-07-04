import streamlit as st

st.set_page_config(page_title="Spotify Analytics", layout="wide")

PAGES = [
    "Now Playing",
    "Year in Review",
    "Genre Explorer",
    "Mood Map",
    "Forecast",
    "Recommendations",
]

st.sidebar.title("Spotify Analytics")
selection = st.sidebar.radio("Navigate", PAGES)


def stub_page(title: str) -> None:
    st.header(title)
    st.info(f"🚧 {title} — coming soon.")


if selection == "Now Playing":
    stub_page("Now Playing")
elif selection == "Year in Review":
    stub_page("Year in Review")
elif selection == "Genre Explorer":
    stub_page("Genre Explorer")
elif selection == "Mood Map":
    stub_page("Mood Map")
elif selection == "Forecast":
    stub_page("Forecast")
elif selection == "Recommendations":
    stub_page("Recommendations")

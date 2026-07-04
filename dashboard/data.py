from __future__ import annotations

from datetime import date
from typing import Any

import streamlit as st
from google.cloud.bigquery import Row


@st.cache_data(ttl=120)
def get_recent_tracks(limit: int = 20) -> list[Row]:
    conn = st.connection("bigquery", type="bigquery")
    query = """
        SELECT *
        FROM marts.fct_listening
        ORDER BY played_at DESC
        LIMIT @limit
    """
    rows: list[Row] = conn.query(query, params={"limit": limit}).to_dicts()
    return rows


@st.cache_data(ttl=600)
def get_daily_summary(start_date: date, end_date: date) -> list[dict[str, Any]]:
    conn = st.connection("bigquery", type="bigquery")
    query = """
        SELECT *
        FROM marts.fct_daily_summary
        WHERE date BETWEEN @start AND @end
        ORDER BY date
    """
    result: list[dict[str, Any]] = conn.query(
        query, params={"start": start_date.isoformat(), "end": end_date.isoformat()}
    ).to_dicts()
    return result


@st.cache_data(ttl=600)
def get_genre_trends(start_date: date, end_date: date) -> list[dict[str, Any]]:
    conn = st.connection("bigquery", type="bigquery")
    query = """
        SELECT *
        FROM marts.fct_genre_trends
        WHERE date BETWEEN @start AND @end
        ORDER BY date, share DESC
    """
    result: list[dict[str, Any]] = conn.query(
        query, params={"start": start_date.isoformat(), "end": end_date.isoformat()}
    ).to_dicts()
    return result


@st.cache_data(ttl=3600)
def get_track_clusters() -> list[dict[str, Any]]:
    conn = st.connection("bigquery", type="bigquery")
    query = "SELECT * FROM marts.track_clusters"
    result: list[dict[str, Any]] = conn.query(query).to_dicts()
    return result

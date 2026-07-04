from typing import Any

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def time_series_chart(
    df: list[dict[str, Any]],
    x: str,
    y: str,
    title: str = "",
) -> None:
    fig = px.line(df, x=x, y=y, title=title)
    st.plotly_chart(fig, use_container_width=True)


def scatter_chart(
    df: list[dict[str, Any]],
    x: str,
    y: str,
    color: str | None = None,
    title: str = "",
) -> None:
    fig = px.scatter(df, x=x, y=y, color=color, title=title)
    st.plotly_chart(fig, use_container_width=True)


def bar_chart(
    df: list[dict[str, Any]],
    x: str,
    y: str,
    title: str = "",
) -> None:
    fig = px.bar(df, x=x, y=y, title=title)
    st.plotly_chart(fig, use_container_width=True)


def heatmap_chart(
    z: list[list[float]],
    x: list[str],
    y: list[str],
    title: str = "",
) -> None:
    fig = go.Figure(go.Heatmap(z=z, x=x, y=y))
    fig.update_layout(title=title)
    st.plotly_chart(fig, use_container_width=True)


def sankey_chart(
    labels: list[str],
    source: list[int],
    target: list[int],
    value: list[float],
    title: str = "",
) -> None:
    fig = go.Figure(
        go.Sankey(node=dict(label=labels), link=dict(source=source, target=target, value=value))
    )
    fig.update_layout(title=title)
    st.plotly_chart(fig, use_container_width=True)

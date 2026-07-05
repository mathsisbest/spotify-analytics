from typing import Any

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

pio.templates.default = "spotify"


def time_series_chart(
    df: list[dict[str, Any]],
    x: str,
    y: str,
    title: str = "",
    height: int = 500,
) -> None:
    fig = px.line(df, x=x, y=y, title=title, template="spotify", height=height)
    fig.update_traces(hovertemplate=f"{x}: %{{x}}<br>{y}: %{{y}}<extra></extra>")
    st.plotly_chart(fig, use_container_width=True)


def scatter_chart(
    df: list[dict[str, Any]],
    x: str,
    y: str,
    color: str | None = None,
    title: str = "",
    height: int = 500,
    hover_data: list[str] | None = None,
) -> None:
    fig = px.scatter(
        df,
        x=x,
        y=y,
        color=color,
        title=title,
        template="spotify",
        height=height,
        hover_data=hover_data,
    )
    fig.update_traces(
        marker=dict(opacity=0.7),
        hovertemplate=f"{x}: %{{x}}<br>{y}: %{{y}}<extra></extra>",
    )
    st.plotly_chart(fig, use_container_width=True)


def bar_chart(
    df: list[dict[str, Any]],
    x: str,
    y: str,
    title: str = "",
    height: int = 500,
) -> None:
    fig = px.bar(df, x=x, y=y, title=title, template="spotify", height=height)
    fig.update_traces(hovertemplate=f"{x}: %{{x}}<br>{y}: %{{y}}<extra></extra>")
    st.plotly_chart(fig, use_container_width=True)


def heatmap_chart(
    z: list[list[float]],
    x: list[str],
    y: list[str],
    title: str = "",
    height: int = 500,
) -> None:
    fig = go.Figure(go.Heatmap(z=z, x=x, y=y))
    fig.update_layout(title=title, template="spotify", height=height)
    fig.update_traces(hovertemplate="x: %{x}<br>y: %{y}<br>value: %{z}<extra></extra>")
    st.plotly_chart(fig, use_container_width=True)


def sankey_chart(
    labels: list[str],
    source: list[int],
    target: list[int],
    value: list[float],
    title: str = "",
    height: int = 500,
) -> None:
    fig = go.Figure(
        go.Sankey(node=dict(label=labels), link=dict(source=source, target=target, value=value))
    )
    fig.update_layout(title=title, template="spotify", height=height)
    fig.update_traces(
        hovertemplate="%{value} from %{source.label} to %{target.label}<extra></extra>"
    )
    st.plotly_chart(fig, use_container_width=True)


def area_chart(
    df: list[dict[str, Any]],
    x: str,
    y: str,
    color: str,
    title: str = "",
    height: int = 500,
) -> None:
    fig = px.area(df, x=x, y=y, color=color, title=title, template="spotify", height=height)
    fig.update_traces(hovertemplate=f"{x}: %{{x}}<br>{y}: %{{y}}<extra></extra>")
    st.plotly_chart(fig, use_container_width=True)

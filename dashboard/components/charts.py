from typing import Any

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

import dashboard.theme  # noqa: F401


def _template() -> str | go.layout.Template:
    if "spotify" in pio.templates:
        return "spotify"
    return "plotly_dark"


def time_series_chart(
    df: list[dict[str, Any]],
    x: str,
    y: str,
    title: str = "",
    height: int = 500,
) -> None:
    fig = px.line(df, x=x, y=y, title=title, template=_template(), height=height)
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
        template=_template(),
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
    fig = px.bar(df, x=x, y=y, title=title, template=_template(), height=height)
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
    fig.update_layout(title=title, template=_template(), height=height)
    fig.update_traces(hovertemplate="x: %{x}<br>y: %{y}<br>value: %{z}<extra></extra>")
    st.plotly_chart(fig, use_container_width=True)


def area_chart(
    df: list[dict[str, Any]],
    x: str,
    y: str,
    color: str,
    title: str = "",
    height: int = 500,
) -> None:
    fig = px.area(df, x=x, y=y, color=color, title=title, template=_template(), height=height)
    fig.update_traces(hovertemplate=f"{x}: %{{x}}<br>{y}: %{{y}}<extra></extra>")
    st.plotly_chart(fig, use_container_width=True)


def radar_chart(
    categories: list[str],
    profiles: dict[str, list[float]],
    title: str = "Audio Feature Profile Comparison",
    height: int = 500,
) -> None:
    fig = go.Figure()
    colors = ["#1DB954", "#1570EF", "#F04438", "#F79009"]
    for i, (name, values) in enumerate(profiles.items()):
        color = colors[i % len(colors)]
        fig.add_trace(
            go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill="toself",
                name=name,
                line_color=color,
                opacity=0.65,
            )
        )
    fig.update_layout(
        title=title,
        template=_template(),
        height=height,
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1.0], gridcolor="#333333"),
            angularaxis=dict(gridcolor="#333333"),
            bgcolor="#191414",
        ),
        showlegend=True,
    )
    st.plotly_chart(fig, use_container_width=True)


def donut_chart(
    labels: list[str],
    values: list[float],
    title: str = "",
    height: int = 450,
) -> None:
    pie_colors = ["#1DB954", "#1ED760", "#169C46", "#0D5C2B", "#38EF7D", "#11998E"]
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.45,
                marker=dict(colors=pie_colors),
                textinfo="percent+label",
            )
        ]
    )
    fig.update_layout(title=title, template=_template(), height=height, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)


def gauge_chart(
    value: float,
    title: str = "Taste Compatibility",
    max_value: float = 100.0,
    height: int = 350,
) -> None:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": title, "font": {"size": 20, "color": "#FFFFFF"}},
            number={"suffix": "%", "font": {"color": "#1DB954", "size": 36}},
            gauge={
                "axis": {"range": [None, max_value], "tickwidth": 1, "tickcolor": "#FFFFFF"},
                "bar": {"color": "#1DB954"},
                "bgcolor": "#282828",
                "borderwidth": 2,
                "bordercolor": "#333333",
                "steps": [
                    {"range": [0, 50], "color": "#191414"},
                    {"range": [50, 80], "color": "#222222"},
                    {"range": [80, 100], "color": "#282828"},
                ],
            },
        )
    )
    fig.update_layout(template=_template(), height=height, margin=dict(t=50, b=20, l=30, r=30))
    st.plotly_chart(fig, use_container_width=True)


def grouped_bar_chart(
    df: list[dict[str, Any]],
    x: str,
    y: str,
    color: str,
    title: str = "",
    height: int = 500,
) -> None:
    fig = px.bar(
        df,
        x=x,
        y=y,
        color=color,
        barmode="group",
        title=title,
        height=height,
        color_discrete_sequence=["#1DB954", "#1570EF", "#F04438"],
        template=_template(),
    )
    st.plotly_chart(fig, use_container_width=True)

import plotly.graph_objects as go
import plotly.io as pio

SPOTIFY_GREEN = "#1DB954"
DARK_BG = "#191414"
CARD_BG = "#282828"
TEXT_COLOR = "#FFFFFF"

DARK_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor=DARK_BG,
        plot_bgcolor=DARK_BG,
        font=dict(color=TEXT_COLOR, family="Inter, sans-serif"),
        xaxis=dict(gridcolor="#333333", zerolinecolor="#444444"),
        yaxis=dict(gridcolor="#333333", zerolinecolor="#444444"),
        colorway=[SPOTIFY_GREEN, "#1ED760", "#169C46", "#E13300", "#FFB4A2"],
        hovermode="x unified",
        hoverlabel=dict(bgcolor=CARD_BG, font_color=TEXT_COLOR),
        margin=dict(l=40, r=40, t=40, b=40),
    )
)

pio.templates["spotify"] = DARK_TEMPLATE
pio.templates.default = "spotify"

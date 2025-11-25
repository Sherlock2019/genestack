import streamlit as st
import plotly.graph_objects as go
from repo_health_metrics import load_repo_health

try:
    from theme_manager import get_theme
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False


def bmw_gauge(title, percent, theme):
    """Create a BMW-style gauge using the theme system"""
    color_good = theme["good"]
    color_warn = theme["warn"]
    color_bad = theme["bad"]
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=percent,
        title={"text": title, "font": {"size": 22, "color": theme["text"]}},
        number={"suffix": "%", "font": {"color": theme["text"], "size": 46}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": theme["text"]},
            "bgcolor": theme["bg"],
            "bar": {"color": theme["accent"]},
            "steps": [
                {"range": [0, 40], "color": color_bad},
                {"range": [40, 70], "color": color_warn},
                {"range": [70, 100], "color": color_good},
            ],
            "threshold": {
                "line": {"color": theme["accent_glow"], "width": 6},
                "thickness": 0.8,
                "value": percent
            }
        }
    ))

    fig.update_layout(
        paper_bgcolor=theme["chart_bg"],
        plot_bgcolor=theme["chart_bg"],
        margin=dict(l=5, r=5, t=40, b=5),
        font=dict(color=theme["text"]),
        xaxis_gridcolor=theme["chart_grid"],
        yaxis_gridcolor=theme["chart_grid"]
    )
    return fig


def render_repo_health_gauges(theme=None):
    """Render repo health gauges using the theme system"""
    st.subheader("🏎 BMW Repo Health Dashboard")

    # Get theme from theme manager if not provided
    if theme is None:
        if THEME_AVAILABLE:
            theme = get_theme()
        else:
            # Fallback theme
            theme = {
                "bg": "#000000",
                "card": "rgba(15, 15, 15, 0.85)",
                "text": "#EAF6FF",
                "accent": "#00A8FF",
                "accent_glow": "rgba(0, 168, 255, 0.65)",
                "good": "#00FFCC",
                "warn": "#FFB300",
                "bad": "#FF4D4D",
                "chart_bg": "#000000",
                "chart_grid": "#333333",
            }

    data = load_repo_health()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.plotly_chart(
            bmw_gauge("Commit Frequency", data["Commit Frequency"]["pct"], theme),
            use_container_width=True
        )

    with col2:
        st.plotly_chart(
            bmw_gauge("Review Velocity", data["Review Velocity"]["pct"], theme),
            use_container_width=True
        )

    with col3:
        st.plotly_chart(
            bmw_gauge("Code Churn Stability", data["Code Churn Stability"]["pct"], theme),
            use_container_width=True
        )

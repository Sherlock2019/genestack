import streamlit as st

# ----------------------------------------
# LIGHT THEME (Bright, colorful, high-contrast)
# ----------------------------------------
LIGHT_THEME = {
    "bg": "#FFFFFF",
    "card": "#F7F9FC",
    "text": "#1A1A1A",
    "accent": "#007BFF",
    "accent_glow": "rgba(0, 123, 255, 0.35)",
    "good": "#28A745",
    "warn": "#FFC107",
    "bad": "#DC3545",
    "chart_bg": "#FFFFFF",
    "chart_grid": "#DDDDDD",
}

# ----------------------------------------
# DARK THEME (BMW glow — neon, cinematic, readable)
# ----------------------------------------
DARK_THEME = {
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

# ----------------------------------------
# Theme Resolver
# ----------------------------------------
def get_theme():
    dark = st.session_state.get("dark_mode", False)  # Default to light mode
    return DARK_THEME if dark else LIGHT_THEME

# ----------------------------------------
# Theme Toggle Component
# ----------------------------------------
def theme_switcher():
    if "dark_mode" not in st.session_state:
        st.session_state["dark_mode"] = False  # Default to light mode

    st.toggle("🌗 Dark Mode", key="dark_mode")

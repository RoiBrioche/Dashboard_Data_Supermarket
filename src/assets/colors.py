"""
Charte Graphique E.Leclerc - Couleurs principales
"""

# Couleurs E.Leclerc officielles
LECLERC_ORANGE = "#ee8c11"
LECLERC_BLUE = "#0471b6"
LECLERC_WHITE = "#ffffff"

# Couleurs secondaires
LECLERC_LIGHT_GRAY = "#f5f5f5"
LECLERC_MEDIUM_GRAY = "#e0e0e0"
LECLERC_DARK_GRAY = "#333333"

# Palettes de couleurs pour les graphiques
COLOR_PATTERNS = {
    "primary": [LECLERC_BLUE, LECLERC_ORANGE],
    "sequential": ["#023e8a", "#0077b6", "#0096c7", "#00b4d8", "#48cae4"],
    "diverging": ["#0471b6", "#48cae4", "#ffffff", "#ffb700", "#ee8c11"],
    "categorical": [
        LECLERC_BLUE, LECLERC_ORANGE, "#48cae4", "#ffb700",
        "#90e0ef", "#ffd60a", "#00b4d8", "#ffaa00"
    ]
}

# Configuration Plotly
PLOTLY_LAYOUT_CONFIG = {
    "font": {"family": "Arial, sans-serif"},
    "title_font": {"size": 20, "color": LECLERC_DARK_GRAY},
    "showlegend": True,
    "legend": {
        "bgcolor": "rgba(255,255,255,0.8)",
        "bordercolor": LECLERC_MEDIUM_GRAY,
        "borderwidth": 1
    }
}

# Thème Streamlit
STREAMLIT_THEME = {
    "primaryColor": LECLERC_ORANGE,
    "backgroundColor": LECLERC_WHITE,
    "secondaryBackgroundColor": LECLERC_LIGHT_GRAY,
    "textColor": LECLERC_DARK_GRAY,
    "font": "sans-serif"
}

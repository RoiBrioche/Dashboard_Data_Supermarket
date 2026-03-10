"""
Dashboard E.Leclerc - Application Dash refactorisée
Design professionnel minimaliste - Charte E.Leclerc
Architecture MVC optimisée avec callbacks mémorisés
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


import dash
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

# Import des modules locaux
from app.analysis import (
    compute_kpis,
    create_kpi_cards,
    hourly_analysis,
    load_data,
    payment_distribution,
    sales_by_category,
    sales_over_time,
    top_products,
)
from app.utils import (
    clean_dataframe,
    create_date_features,
    get_data_summary,
    validate_transaction_data,
)
from assets.colors import (
    COLOR_PATTERNS,
    LECLERC_BLUE,
    LECLERC_ORANGE,
)

# ─────────────────────────────────────────────
# CONFIGURATION PLOTLY LAYOUT UNIFIÉ
# ─────────────────────────────────────────────
BASE_CHART_LAYOUT = {
    "paper_bgcolor": "white",
    "plot_bgcolor": "white",
    "font": {"family": "DM Sans, Arial, sans-serif", "size": 12, "color": "#444"},
    "margin": {"t": 40, "b": 40, "l": 50, "r": 20},
    "showlegend": True,
    "legend": {
        "bgcolor": "rgba(255,255,255,0)",
        "bordercolor": "rgba(0,0,0,0)",
        "font": {"size": 11},
    },
    "xaxis": {
        "gridcolor": "#f0f0f0",
        "linecolor": "#e0e0e0",
        "tickfont": {"size": 11},
    },
    "yaxis": {
        "gridcolor": "#f0f0f0",
        "linecolor": "#e0e0e0",
        "tickfont": {"size": 11},
    },
}

# ─────────────────────────────────────────────
# CHARGEMENT DES DONNÉES (une seule fois)
# ─────────────────────────────────────────────
_data_cache = {}


def get_data():
    """Charge et met en cache les données au démarrage."""
    if "df" not in _data_cache:
        try:
            data_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "supermarket_analysis.csv")
            df = load_data(data_path)
            df_clean = clean_dataframe(df)
            validation = validate_transaction_data(df_clean)
            df_with_features = create_date_features(df_clean)
            _data_cache["df"] = df
            _data_cache["df_clean"] = df_clean
            _data_cache["validation"] = validation
            _data_cache["df_with_features"] = df_with_features
        except Exception as e:
            print(f"[ERREUR] Chargement des données: {e}")
            empty = pd.DataFrame()
            _data_cache["df"] = empty
            _data_cache["df_clean"] = empty
            _data_cache["validation"] = {"is_valid": False, "errors": [str(e)], "warnings": []}
            _data_cache["df_with_features"] = empty
    return _data_cache


data = get_data()
df_clean = data["df_clean"]
validation = data["validation"]


# ─────────────────────────────────────────────
# HELPERS UI
# ─────────────────────────────────────────────
def section_card(title: str, icon: str, content, width: int = 12, height: str = "auto"):
    """Crée une carte de section avec header bleu uniforme."""
    body_style = {
        "background": "white",
        "border": "1px solid #e8ecf0",
        "borderRadius": "0 0 10px 10px",
        "borderTop": "none",
        "padding": "16px",
    }
    if height != "auto":
        body_style["height"] = height
        # Don't set overflow hidden for filter sections to allow dropdowns to show
        if title != "Filtres":
            body_style["overflow"] = "hidden"

    # Add special class for filter section
    section_class = "filter-section" if title == "Filtres" else ""

    return dbc.Col(
        [
            html.Div(
                [
                    html.Span(icon, style={"marginRight": "8px", "fontSize": "1rem"}),
                    html.Span(title, style={"fontWeight": "600", "fontSize": "0.85rem", "letterSpacing": "0.05em"}),
                ],
                style={
                    "background": LECLERC_BLUE,
                    "color": "white",
                    "padding": "10px 16px",
                    "borderRadius": "10px 10px 0 0",
                    "display": "flex",
                    "alignItems": "center",
                },
            ),
            html.Div(content, style=body_style, className=section_class),
        ],
        width=width,
    )


def kpi_card(value, label, icon, color, border_accent=False):
    """Crée une carte KPI minimaliste avec style E.Leclerc uniformisé."""
    border_style = f"2px solid {color}" if border_accent else "1px solid #e8ecf0"
    return html.Div(
        [
            html.Div(icon, style={"fontSize": "1.4rem", "marginBottom": "6px", "opacity": "0.9"}),
            html.Div(
                value,
                style={
                    "fontSize": "1.45rem",
                    "fontWeight": "700",
                    "color": LECLERC_ORANGE,  # Orange pour tous les chiffres
                    "lineHeight": "1.2",
                    "letterSpacing": "-0.02em",
                },
            ),
            html.Div(
                label,
                style={
                    "fontSize": "0.72rem",
                    "color": "#8a95a3",  # Gris pour tous les textes
                    "marginTop": "4px",
                    "fontWeight": "500",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.06em",
                },
            ),
        ],
        style={
            "background": "white",
            "border": border_style,
            "borderRadius": "10px",
            "padding": "16px 14px",
            "textAlign": "center",
            "boxShadow": "0 1px 4px rgba(0,0,0,0.04)",
            "height": "100%",
            "transition": "box-shadow 0.2s ease",
        },
    )


def empty_figure(message="Aucune donnée disponible"):
    """Retourne une figure vide avec message centré."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font={"size": 13, "color": "#aaa"},
    )
    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin={"t": 20, "b": 20, "l": 20, "r": 20},
        xaxis={"visible": False},
        yaxis={"visible": False},
    )
    return fig


# ─────────────────────────────────────────────
# INITIALISATION APP
# ─────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap",
    ],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    title="Dashboard E.Leclerc Analytics",
    assets_folder="../assets",
)
server = app.server


# ─────────────────────────────────────────────
# OPTIONS DROPDOWN (construites une seule fois)
# ─────────────────────────────────────────────
category_options = [{"label": "Toutes les catégories", "value": "all"}]
if "Product line" in df_clean.columns:
    category_options += [{"label": c, "value": c} for c in sorted(df_clean["Product line"].unique())]

payment_options = [{"label": "Tous les modes", "value": "all"}]
if "Payment" in df_clean.columns:
    payment_options += [{"label": p, "value": p} for p in sorted(df_clean["Payment"].unique())]

# Options pour les villes (pour les tabs)
city_options = []
if "City" in df_clean.columns:
    city_options = [{"label": city, "value": city} for city in sorted(df_clean["City"].unique())]

# Créer les boutons-toggle pour les villes
city_toggle_buttons = []
# Bouton "Toutes"
city_toggle_buttons.append(
    dbc.Button(
        "Toutes",
        id="city-toggle-all",
        color="primary",
        outline=True,
        size="sm",
        className="city-toggle-btn me-1",
    )
)
# Boutons individuels
for city in city_options:
    city_toggle_buttons.append(
        dbc.Button(
            city["label"],
            id=f"city-toggle-{city['value']}",
            color="primary",
            outline=True,
            size="sm",
            className="city-toggle-btn me-1",
        )
    )


# ─────────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────────
app.layout = html.Div(
    [
        # ── HEADER ──────────────────────────────────────────
        html.Div(
            dbc.Container(
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    html.Img(
                                        src="/assets/E.Leclerc_logo.png",
                                        height="42px",
                                        style={"marginRight": "16px", "display": "block", "verticalAlign": "middle"},
                                    ),
                                    html.Div(
                                        [
                                            html.H1(
                                                "Analytics Dashboard",
                                                style={
                                                    "color": "white",
                                                    "margin": 0,
                                                    "fontSize": "1.5rem",
                                                    "fontWeight": "700",
                                                    "letterSpacing": "-0.02em",
                                                },
                                            ),
                                            html.P(
                                                "Analyse des performances commerciales",
                                                style={
                                                    "color": "rgba(255,255,255,0.65)",
                                                    "margin": 0,
                                                    "fontSize": "0.78rem",
                                                    "fontWeight": "400",
                                                },
                                            ),
                                        ]
                                    ),
                                ],
                                style={"display": "flex", "alignItems": "center"},
                                className="header-logo-container",
                            ),
                            width="auto",
                        ),
                        dbc.Col(
                            html.Div(
                                [
                                    html.Div(
                                        "●",
                                        style={
                                            "color": "#4ade80",
                                            "fontSize": "0.6rem",
                                            "marginRight": "6px",
                                            "verticalAlign": "middle",
                                        },
                                    ),
                                    html.Span(
                                        f"{len(df_clean):,} transactions chargées",
                                        style={"color": "rgba(255,255,255,0.7)", "fontSize": "0.78rem"},
                                    ),
                                ],
                                style={"display": "flex", "alignItems": "center", "justifyContent": "flex-end"},
                            ),
                            style={"display": "flex", "alignItems": "center", "justifyContent": "flex-end"},
                        ),
                    ],
                    align="center",
                ),
                fluid=False,
                style={"maxWidth": "1200px"},
            ),
            style={
                "background": f"linear-gradient(135deg, {LECLERC_BLUE} 0%, #035a94 100%)",
                "padding": "18px 0",
                "boxShadow": "0 2px 12px rgba(4,113,182,0.25)",
                "position": "sticky",
                "top": 0,
                "zIndex": 100,
            },
        ),
        # ── CONTENU PRINCIPAL ───────────────────────────────
        dbc.Container(
            [
                # Alerte validation
                html.Div(id="validation-alerts", style={"marginTop": "20px"}),
                # ── FILTRES ────────────────────────────────
                dbc.Row(
                    [
                        section_card(
                            "Filtres",
                            "⚙",
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Label(
                                                "Période",
                                                style={
                                                    "fontSize": "0.75rem",
                                                    "fontWeight": "600",
                                                    "color": "#6c757d",
                                                    "marginBottom": "6px",
                                                },
                                            ),
                                            dbc.Select(
                                                id="period-dropdown",
                                                options=[
                                                    {"label": "Tout", "value": "all"},
                                                    {"label": "Aujourd'hui", "value": "today"},
                                                    {"label": "Cette semaine", "value": "week"},
                                                    {"label": "Ce mois", "value": "month"},
                                                ],
                                                value="all",
                                            ),
                                        ],
                                        className="filter-column",
                                    ),
                                    html.Div(
                                        [
                                            html.Label(
                                                "Catégorie produit",
                                                style={
                                                    "fontSize": "0.75rem",
                                                    "fontWeight": "600",
                                                    "color": "#6c757d",
                                                    "marginBottom": "6px",
                                                },
                                            ),
                                            dbc.Select(
                                                id="category-dropdown",
                                                options=category_options,
                                                value="all",
                                            ),
                                        ],
                                        className="filter-column",
                                    ),
                                    html.Div(
                                        [
                                            html.Label(
                                                "Mode de paiement",
                                                style={
                                                    "fontSize": "0.75rem",
                                                    "fontWeight": "600",
                                                    "color": "#6c757d",
                                                    "marginBottom": "6px",
                                                },
                                            ),
                                            dbc.Select(
                                                id="payment-dropdown",
                                                options=payment_options,
                                                value="all",
                                            ),
                                        ],
                                        className="filter-column",
                                    ),
                                    html.Div(
                                        [
                                            html.Label(
                                                "Villes à analyser",
                                                style={
                                                    "fontSize": "0.75rem",
                                                    "fontWeight": "600",
                                                    "color": "#6c757d",
                                                    "marginBottom": "8px",
                                                },
                                            ),
                                            html.Div(
                                                dbc.Checklist(
                                                    id="city-checklist",
                                                    options=city_options,
                                                    value=[city["value"] for city in city_options],  # Toutes cochées
                                                    inline=True,
                                                    className="",  # Supprimer la classe modern-city-toggles
                                                ),
                                                className="toggles-container modern-city-toggles",  # Classes sur container
                                            ),
                                        ],
                                        className="filter-column",
                                    ),
                                ],
                                className="filters-container",
                            ),
                            height="auto",
                        )
                    ],
                    className="mt-4 mb-3",
                ),
                # ── KPI CARDS ────────────────────────────────
                html.Div(id="kpi-cards", className="kpi-card-wrapper mb-3"),
                # ── GRAPHIQUES LIGNE 1 ────────────────────────
                dbc.Row(
                    [
                        section_card(
                            "Évolution des ventes",
                            "📈",
                            dcc.Graph(
                                id="sales-trend-chart",
                                config={"displayModeBar": False},
                                style={"height": "320px"},
                            ),
                            width=8,
                        ),
                        section_card(
                            "Modes de paiement",
                            "💳",
                            dcc.Graph(
                                id="payment-pie-chart",
                                config={"displayModeBar": False},
                                style={"height": "320px"},
                            ),
                            width=4,
                        ),
                    ],
                    className="mb-3",
                ),
                # ── GRAPHIQUES LIGNE 2 ────────────────────────
                dbc.Row(
                    [
                        section_card(
                            "Ventes par catégorie",
                            "📦",
                            dcc.Graph(
                                id="category-sales-chart",
                                config={"displayModeBar": False},
                                style={"height": "280px"},
                            ),
                            width=6,
                        ),
                        section_card(
                            "Activité horaire",
                            "⏱",
                            dcc.Graph(
                                id="hourly-analysis-chart",
                                config={"displayModeBar": False},
                                style={"height": "280px"},
                            ),
                            width=6,
                        ),
                    ],
                    className="mb-3",
                ),
                # ── ANALYSES COMBINÉES ──────────────────────────
                dbc.Row(
                    [
                        section_card(
                            "Analyses",
                            "📊",
                            [
                                html.H5("Top Catégories", className="mb-3", style={"color": LECLERC_BLUE}),
                                html.Div(id="top-categories-table"),
                                html.Hr(className="my-4", style={"borderColor": "#e8ecf0"}),
                                html.H5("Analyse par Ville", className="mb-3", style={"color": LECLERC_BLUE}),
                                html.Div(id="cities-analysis-table"),
                            ],
                            width=12,
                        )
                    ],
                    className="mb-3",
                ),
                # ── RÉSUMÉ ────────────────────────────────────
                dbc.Row(
                    [
                        section_card(
                            "Résumé des données",
                            "📋",
                            html.Div(id="data-summary"),
                            width=12,
                        )
                    ],
                    className="mb-4",
                ),
                # ── FOOTER ────────────────────────────────────
                html.Div(
                    html.P(
                        "Dashboard E.Leclerc · Analytics Platform · Données confidentielles",
                        style={"color": "#adb5bd", "fontSize": "0.72rem", "textAlign": "center", "margin": "0 0 24px"},
                    )
                ),
            ],
            fluid=False,
            style={"maxWidth": "1200px"},
        ),
        # ── CSS PERSONNALISÉ ───────────────────────────────
        html.Link(rel="stylesheet", href="/assets/custom_toggles.css"),
        html.Link(rel="stylesheet", href="/assets/filters_flexbox.css"),
    ],
    style={"fontFamily": "'DM Sans', Arial, sans-serif", "backgroundColor": "#f7f9fb", "minHeight": "100vh"},
)


# ─────────────────────────────────────────────
# Callback principal pour mettre à jour le dashboard
@callback(
    [
        Output("validation-alerts", "children"),
        Output("kpi-cards", "children"),
        Output("sales-trend-chart", "figure"),
        Output("payment-pie-chart", "figure"),
        Output("category-sales-chart", "figure"),
        Output("hourly-analysis-chart", "figure"),
        Output("top-categories-table", "children"),
        Output("cities-analysis-table", "children"),
        Output("data-summary", "children"),
    ],
    [
        Input("period-dropdown", "value"),
        Input("category-dropdown", "value"),
        Input("payment-dropdown", "value"),
        Input("city-checklist", "value"),
    ],
)
def update_dashboard(period, category, payment, selected_cities):
    """Met à jour tous les composants du dashboard selon les filtres actifs."""

    # ── Données vides ──
    if df_clean.empty:
        alert = dbc.Alert("❌ Aucune donnée disponible. Vérifiez le chemin du fichier CSV.", color="danger", className="mt-2")
        return alert, [], empty_figure(), empty_figure(), empty_figure(), empty_figure(), "—", "—"

    # ── Alertes validation ──
    alerts = []
    if not validation.get("is_valid", True):
        for err in validation.get("errors", []):
            alerts.append(dbc.Alert(f"❌ {err}", color="danger", dismissable=True, className="mb-1"))
    for warn in validation.get("warnings", []):
        alerts.append(dbc.Alert(f"⚠️ {warn}", color="warning", dismissable=True, className="mb-1"))

    # ── Filtrage ──
    filtered_df = df_clean.copy()
    if category != "all" and "Product line" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Product line"] == category]
    if payment != "all" and "Payment" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Payment"] == payment]

    # Filtrage par villes sélectionnées
    if selected_cities:
        filtered_df = filtered_df[filtered_df["City"].isin(selected_cities)]
    # Si aucune ville sélectionnée, on garde toutes les villes (au lieu de tout cacher)
    # pour éviter que les graphiques soient vides

    # ── KPIs ──
    try:
        kpis = compute_kpis(filtered_df)
        cards_data = create_kpi_cards(kpis)

        kpi_row = dbc.Row(
            [
                dbc.Col(kpi_card(cards_data["revenue"]["value"], "Chiffre d'affaires", "💰", LECLERC_BLUE, True), width=2),
                dbc.Col(kpi_card(cards_data["margin"]["value"], "Marge brute", "📈", LECLERC_BLUE, True), width=2),
                dbc.Col(kpi_card(cards_data["transactions"]["value"], "Transactions", "🧾", LECLERC_BLUE, True), width=2),
                dbc.Col(kpi_card(cards_data["avg_basket"]["value"], "Panier moyen", "🛒", LECLERC_BLUE, True), width=2),
                dbc.Col(kpi_card(cards_data["rating"]["value"], "Satisfaction", "⭐", LECLERC_BLUE, True), width=2),
                dbc.Col(kpi_card(f"{len(filtered_df):,}", "Lignes filtrées", "🔍", LECLERC_BLUE, True), width=2),
            ],
            className="mb-3 g-2",
        )
    except Exception as e:
        kpi_row = dbc.Alert(f"Erreur KPIs: {e}", color="danger")

    # ── Graphique ventes ──
    try:
        # Convertir les valeurs de période pour la fonction sales_over_time
        period_mapping = {"all": "daily", "today": "daily", "week": "weekly", "month": "monthly"}
        mapped_period = period_mapping.get(period, "daily")

        time_data = sales_over_time(filtered_df, period=mapped_period)
        sales_fig = go.Figure()
        # Zone remplie sous la courbe
        sales_fig.add_trace(
            go.Scatter(
                x=time_data["period"],
                y=time_data["Sales"],
                mode="lines+markers",
                name="CA (€)",
                line={"color": LECLERC_BLUE, "width": 2.5, "shape": "spline"},
                marker={"size": 5, "color": LECLERC_BLUE},
                fill="tozeroy",
                fillcolor="rgba(4,113,182,0.08)",
            )
        )
        sales_fig.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            font={"family": "DM Sans, Arial, sans-serif", "size": 12, "color": "#444"},
            margin={"t": 20, "b": 30, "l": 55, "r": 20},
            xaxis={"gridcolor": "#f0f0f0", "linecolor": "#e0e0e0", "tickfont": {"size": 11}},
            yaxis={"gridcolor": "#f0f0f0", "linecolor": "#e0e0e0", "tickfont": {"size": 11}},
            xaxis_title=None,
            yaxis_title="Ventes (€)",
            hovermode="x unified",
            showlegend=True,
            legend={"bgcolor": "rgba(255,255,255,0)", "bordercolor": "rgba(0,0,0,0)", "font": {"size": 11}},
        )
    except Exception as e:
        sales_fig = empty_figure(f"Erreur: {e}")

    # ── Graphique paiements ──
    try:
        pay_data = payment_distribution(filtered_df)
        pie_fig = go.Figure(
            data=[
                go.Pie(
                    labels=pay_data["Payment"],
                    values=pay_data["count"],
                    hole=0.42,
                    marker_colors=COLOR_PATTERNS["categorical"],
                    textinfo="label+percent",
                    textfont={"size": 11},
                    hoverinfo="label+value+percent",
                )
            ]
        )
        pie_fig.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            margin={"t": 20, "b": 20, "l": 20, "r": 20},
            showlegend=False,
            font={"family": "DM Sans, Arial, sans-serif", "size": 11},
        )
    except Exception as e:
        pie_fig = empty_figure(f"Erreur: {e}")

    # ── Graphique catégories ──
    try:
        cat_data = sales_by_category(filtered_df).reset_index()
        cat_fig = go.Figure(
            data=[
                go.Bar(
                    x=cat_data["Product line"],
                    y=cat_data["Sales"],
                    marker_color=[LECLERC_BLUE if i % 2 == 0 else "#48cae4" for i in range(len(cat_data))],
                    text=cat_data["Sales"].apply(lambda x: f"€{x:,.0f}"),
                    textposition="outside",
                    textfont={"size": 10},
                )
            ]
        )
        cat_fig.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            font={"family": "DM Sans, Arial, sans-serif", "size": 12, "color": "#444"},
            margin={"t": 30, "b": 60, "l": 55, "r": 20},
            xaxis={"tickangle": -25, "gridcolor": "#f0f0f0", "linecolor": "#e0e0e0", "tickfont": {"size": 11}},
            yaxis={"gridcolor": "#f0f0f0", "linecolor": "#e0e0e0", "tickfont": {"size": 11}},
            xaxis_title=None,
            yaxis_title="Ventes (€)",
            showlegend=False,
        )
    except Exception as e:
        cat_fig = empty_figure(f"Erreur: {e}")

    # ── Graphique horaire ──
    try:
        hourly_data = hourly_analysis(filtered_df)

        # Debug : voir la structure des données
        print("DEBUG hourly_data columns:", hourly_data.columns.tolist())
        print("DEBUG hourly_data shape:", hourly_data.shape)
        print("DEBUG hourly_data head:", hourly_data.head().to_dict())

        # Version ultra-simple pour tester
        hourly_fig = go.Figure()
        hourly_fig.add_trace(
            go.Bar(x=hourly_data["hour"].tolist(), y=hourly_data["Sales"].tolist(), marker_color=LECLERC_ORANGE, name="Ventes")
        )
        hourly_fig.update_layout(title="Ventes par heure", xaxis_title="Heure", yaxis_title="Ventes (€)", showlegend=False)
    except Exception as e:
        print(f"ERREUR graphique horaire: {e}")
        hourly_fig = empty_figure(f"Erreur: {e}")

    # ── Top Catégories ──
    try:
        # Afficher toujours les 6 catégories (toutes)
        top_df = top_products(filtered_df, n=6, metric="sales")

        # Harmoniser les colonnes pour l'affichage
        col_map = {}
        if "Product line" in top_df.columns:
            col_map["Product line"] = "Catégorie"
        if "Sales" in top_df.columns:
            col_map["Sales"] = "Ventes (€)"
        if "gross income" in top_df.columns:
            col_map["gross income"] = "Marge (€)"
        if "transactions" in top_df.columns:
            col_map["transactions"] = "Transactions"

        top_df_display = top_df.rename(columns=col_map)

        # Configuration des colonnes pour AgGrid
        column_defs = [{"field": col, "headerName": col, "filter": True, "sortable": True} for col in top_df_display.columns]

        # Style personnalisé pour AgGrid (pleine largeur pour affichage vertical)
        grid_style = {
            "height": "300px",
            "width": "100%",
            ".ag-header": {
                "background-color": "#0471b6",
                "color": "white",
                "font-weight": "700",
                "font-size": "0.72rem",
                "text-transform": "uppercase",
                "letter-spacing": "0.06em",
                "border": "none",
                "border-bottom": "2px solid #0471b6",
            },
            ".ag-header-cell": {
                "padding": "10px 14px",
                "border-right": "1px solid #0471b6",
            },
            ".ag-row": {
                "font-family": "DM Sans, Arial, sans-serif",
                "font-size": "0.80rem",
                "border-bottom": "1px solid #f0f0f0",
            },
            ".ag-row-odd": {
                "background-color": "#fafbfc",
            },
            ".ag-cell": {
                "padding": "10px 14px",
                "border-right": "1px solid #f0f0f0",
                "text-align": "left",
            },
            ".ag-cell[col-id='Ventes (€)']": {
                "color": LECLERC_BLUE,
                "font-weight": "700",
            },
            ".ag-row-first": {
                "border-left": "3px solid #ee8c11",
            },
        }

        categories_table = dag.AgGrid(
            rowData=top_df_display.round(2).to_dict("records"),
            columnDefs=column_defs,
            defaultColDef={
                "filter": True,
                "sortable": True,
                "resizable": True,
                "flex": 1,
                "minWidth": 120,
            },
            dashGridOptions={
                "pagination": False,
                "domLayout": "autoHeight",
                "sizeColumnsToFit": True,
            },
            style=grid_style,
            className="ag-theme-alpine ag-grid-full-width",
        )
    except Exception as e:
        categories_table = dbc.Alert(f"Erreur catégories: {e}", color="danger", className="p-2")

    # ── Analyse par ville ──
    try:
        cities_df = (
            filtered_df.groupby("City")
            .agg({"Sales": "sum", "Invoice ID": "count", "Rating": "mean", "Quantity": "sum", "gross income": "sum"})
            .round(2)
        )

        cities_df = cities_df.sort_values("Sales", ascending=False)

        # Afficher seulement la/les villes sélectionnées
        if cities_df.empty:
            cities_table = dbc.Alert("Aucune ville sélectionnée", color="info", className="p-2")
        else:
            # Renommer les colonnes pour l'affichage
            cities_df_display = cities_df.rename(
                columns={
                    "Sales": "Ventes (€)",
                    "Invoice ID": "Transactions",
                    "Rating": "Satisfaction moyenne",
                    "Quantity": "Quantité totale",
                    "gross income": "Marge (€)",
                }
            ).reset_index()

            # Configuration des colonnes pour AgGrid
            column_defs = [
                {"field": col, "headerName": col, "filter": True, "sortable": True} for col in cities_df_display.columns
            ]

            # Style personnalisé pour AgGrid (pleine largeur pour affichage vertical)
            grid_style = {
                "height": "250px",
                "width": "100%",
                ".ag-header": {
                    "background-color": "#0471b6",
                    "color": "white",
                    "font-weight": "700",
                    "font-size": "0.72rem",
                    "text-transform": "uppercase",
                    "letter-spacing": "0.06em",
                    "border": "none",
                    "border-bottom": "2px solid #0471b6",
                },
                ".ag-header-cell": {
                    "padding": "10px 14px",
                    "border-right": "1px solid #0471b6",
                },
                ".ag-row": {
                    "font-family": "DM Sans, Arial, sans-serif",
                    "font-size": "0.80rem",
                    "border-bottom": "1px solid #f0f0f0",
                },
                ".ag-row-odd": {
                    "background-color": "#fafbfc",
                },
                ".ag-cell": {
                    "padding": "10px 14px",
                    "border-right": "1px solid #f0f0f0",
                    "text-align": "left",
                },
                ".ag-cell[col-id='Ventes (€)']": {
                    "color": LECLERC_BLUE,
                    "font-weight": "700",
                },
                ".ag-row-first": {
                    "border-left": "3px solid #ee8c11",
                },
            }

            cities_table = dag.AgGrid(
                rowData=cities_df_display.to_dict("records"),
                columnDefs=column_defs,
                defaultColDef={
                    "filter": True,
                    "sortable": True,
                    "resizable": True,
                    "flex": 1,
                    "minWidth": 140,
                },
                dashGridOptions={
                    "pagination": False,
                    "domLayout": "autoHeight",
                    "sizeColumnsToFit": True,
                },
                style=grid_style,
                className="ag-theme-alpine ag-grid-full-width",
            )
    except Exception as e:
        cities_table = dbc.Alert(f"Erreur analyse villes: {e}", color="danger")

    # ── Résumé des données ──
    try:
        summary = get_data_summary(filtered_df)
        num_cols = list(summary["numeric_summary"].keys())[:5]
        summary_html = dbc.Row(
            [
                dbc.Col(
                    [
                        html.P(
                            [html.Strong("Lignes : "), f"{summary['shape'][0]:,}"],
                            style={"fontSize": "0.83rem", "marginBottom": "4px"},
                        ),
                        html.P(
                            [html.Strong("Colonnes : "), f"{summary['shape'][1]}"],
                            style={"fontSize": "0.83rem", "marginBottom": "4px"},
                        ),
                        html.P(
                            [html.Strong("Mémoire : "), f"{summary['memory_usage'] / 1024:.1f} KB"],
                            style={"fontSize": "0.83rem", "marginBottom": "4px"},
                        ),
                    ],
                    width=4,
                ),
                dbc.Col(
                    [
                        html.P(html.Strong("Colonnes numériques :"), style={"fontSize": "0.83rem", "marginBottom": "4px"}),
                        html.Ul(
                            [
                                html.Li(
                                    f"{c} ({summary['numeric_summary'][c]['count']} valeurs)", style={"fontSize": "0.81rem"}
                                )
                                for c in num_cols
                            ],
                            style={"paddingLeft": "16px", "margin": 0},
                        ),
                    ],
                    width=4,
                ),
                dbc.Col(
                    [
                        html.P(html.Strong("Validation :"), style={"fontSize": "0.83rem", "marginBottom": "4px"}),
                        html.Ul(
                            [
                                html.Li(
                                    [
                                        "✅ Statut : ",
                                        html.Span(
                                            "Valide" if validation.get("is_valid") else "Invalide",
                                            style={"color": "#22c55e" if validation.get("is_valid") else "#ef4444"},
                                        ),
                                    ],
                                    style={"fontSize": "0.81rem"},
                                ),
                                html.Li(
                                    f"⚠️ Avertissements : {len(validation.get('warnings', []))}", style={"fontSize": "0.81rem"}
                                ),
                                html.Li(f"❌ Erreurs : {len(validation.get('errors', []))}", style={"fontSize": "0.81rem"}),
                            ],
                            style={"paddingLeft": "16px", "margin": 0},
                        ),
                    ],
                    width=4,
                ),
            ]
        )
    except Exception as e:
        summary_html = dbc.Alert(f"Erreur résumé: {e}", color="danger")

    return (
        alerts,
        kpi_row,
        sales_fig,
        pie_fig,
        cat_fig,
        hourly_fig,
        categories_table,
        cities_table,
        summary_html,
    )


# ─────────────────────────────────────────────
# ENTRYPOINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)  # nosec B104

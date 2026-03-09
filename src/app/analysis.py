"""
Module d'analyse des données pour le dashboard E.Leclerc
Fonctions de calcul des KPI et analyses business
"""

from typing import Any

import pandas as pd
import plotly.graph_objects as go

# Import des couleurs E.Leclerc
from assets.colors import (
    COLOR_PATTERNS,
    LECLERC_BLUE,
    LECLERC_ORANGE,
    PLOTLY_LAYOUT_CONFIG,
)


def load_data(file_path: str) -> pd.DataFrame:
    """
    Charge les données depuis le fichier CSV

    Args:
        file_path: Chemin vers le fichier CSV

    Returns:
        DataFrame pandas avec les données nettoyées
    """
    try:
        df = pd.read_csv(file_path)

        # Conversion des types
        df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y")
        df["Time"] = pd.to_datetime(df["Time"], format="%I:%M:%S %p").dt.time

        # Nettoyage des colonnes numériques
        numeric_columns = ["Unit price", "Quantity", "Tax 5%", "Sales", "cogs", "gross income", "Rating"]
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Création de colonnes dérivées
        df["Year"] = df["Date"].dt.year
        df["Month"] = df["Date"].dt.month
        df["Day"] = df["Date"].dt.day
        df["DayOfWeek"] = df["Date"].dt.day_name()

        return df

    except Exception as e:
        raise ValueError(f"Erreur lors du chargement des données: {e}") from e


def compute_kpis(df: pd.DataFrame) -> dict[str, Any]:
    """
    Calcule les KPIs principaux du dashboard

    Args:
        df: DataFrame des transactions

    Returns:
        Dictionnaire avec tous les KPIs calculés
    """
    if df.empty:
        return {
            "total_revenue": 0,
            "total_margin": 0,
            "total_transactions": 0,
            "avg_basket": 0,
            "avg_rating": 0,
            "total_customers": 0,
            "member_customers": 0,
            "normal_customers": 0,
        }

    # KPIs principaux
    total_revenue = df["Sales"].sum()
    total_margin = df["gross income"].sum()
    total_transactions = len(df)
    avg_basket = total_revenue / total_transactions if total_transactions > 0 else 0
    avg_rating = df["Rating"].mean()

    # KPIs clients
    total_customers = df["Customer type"].value_counts().sum()
    member_customers = df[df["Customer type"] == "Member"]["Customer type"].count()
    normal_customers = df[df["Customer type"] == "Normal"]["Customer type"].count()

    return {
        "total_revenue": round(total_revenue, 2),
        "total_margin": round(total_margin, 2),
        "total_transactions": int(total_transactions),
        "avg_basket": round(avg_basket, 2),
        "avg_rating": round(avg_rating, 2),
        "total_customers": int(total_customers),
        "member_customers": int(member_customers),
        "normal_customers": int(normal_customers),
    }


def sales_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les ventes par catégorie de produits

    Args:
        df: DataFrame des transactions

    Returns:
        DataFrame avec ventes par catégorie
    """
    category_sales = (
        df.groupby("Product line")
        .agg({"Sales": "sum", "gross income": "sum", "Quantity": "sum", "Invoice ID": "count"})
        .rename(columns={"Invoice ID": "transactions", "gross income": "margin"})
        .round(2)
    )

    category_sales = category_sales.sort_values("Sales", ascending=False)
    return category_sales


def sales_over_time(df: pd.DataFrame, period: str = "daily") -> pd.DataFrame:
    """
    Calcule l'évolution des ventes dans le temps

    Args:
        df: DataFrame des transactions
        period: 'daily', 'weekly', 'monthly'

    Returns:
        DataFrame avec ventes par période
    """
    df_copy = df.copy()

    # Convertir en datetime pour éviter les problèmes d'accès .dt
    df_copy["Date"] = pd.to_datetime(df_copy["Date"])

    if period == "daily":
        df_copy["period"] = df_copy["Date"].dt.date
    elif period == "weekly":
        df_copy["period"] = df_copy["Date"].dt.to_period("W").dt.start_time
    elif period == "monthly":
        df_copy["period"] = df_copy["Date"].dt.to_period("M").dt.start_time
    else:
        raise ValueError("Period must be 'daily', 'weekly', or 'monthly'")

    time_sales = (
        df_copy.groupby("period")
        .agg({"Sales": "sum", "gross income": "sum", "Invoice ID": "count"})
        .rename(columns={"Invoice ID": "transactions", "gross income": "margin"})
        .round(2)
    )

    return time_sales.reset_index()


def profit_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule la marge par catégorie

    Args:
        df: DataFrame des transactions

    Returns:
        DataFrame avec marges par catégorie
    """
    category_profit = df.groupby("Product line").agg({"gross income": "sum", "Sales": "sum", "cogs": "sum"}).round(2)

    category_profit["margin_percentage"] = round((category_profit["gross income"] / category_profit["Sales"] * 100), 2)

    category_profit = category_profit.sort_values("gross income", ascending=False)
    return category_profit.reset_index()


def payment_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule la répartition des modes de paiement

    Args:
        df: DataFrame des transactions

    Returns:
        DataFrame avec distribution des paiements
    """
    payment_dist = df["Payment"].value_counts().to_frame("count")
    payment_dist["percentage"] = (payment_dist["count"] / len(df) * 100).round(2)

    return payment_dist.reset_index().rename(columns={"index": "payment_method"})


def top_products(df: pd.DataFrame, n: int = 10, metric: str = "sales") -> pd.DataFrame:
    """
    Identifie les top produits par métrique

    Args:
        df: DataFrame des transactions
        n: Nombre de produits à retourner
        metric: 'sales', 'margin', 'quantity'

    Returns:
        DataFrame avec top produits
    """
    if metric not in ["sales", "margin", "quantity"]:
        raise ValueError("Metric must be 'sales', 'margin', or 'quantity'")

    metric_col = {"sales": "Sales", "margin": "gross income", "quantity": "Quantity"}[metric]

    top_products = (
        df.groupby("Product line")
        .agg({metric_col: "sum", "Invoice ID": "count"})
        .rename(columns={"Invoice ID": "transactions"})
        .round(2)
    )

    top_products = top_products.sort_values(metric_col, ascending=False).head(n)
    return top_products.reset_index()


def customer_analysis(df: pd.DataFrame) -> dict[str, Any]:
    """
    Analyse détaillée des clients

    Args:
        df: DataFrame des transactions

    Returns:
        Dictionnaire avec analyses clients
    """
    # Répartition par type
    customer_type_dist = df["Customer type"].value_counts().to_dict()

    # Panier moyen par type
    avg_basket_by_type = df.groupby("Customer type")["Sales"].mean().round(2).to_dict()

    # Satisfaction par type
    rating_by_type = df.groupby("Customer type")["Rating"].mean().round(2).to_dict()

    # Analyse par genre
    gender_dist = df["Gender"].value_counts().to_dict()
    sales_by_gender = df.groupby("Gender")["Sales"].sum().round(2).to_dict()

    return {
        "customer_type_distribution": customer_type_dist,
        "avg_basket_by_type": avg_basket_by_type,
        "rating_by_type": rating_by_type,
        "gender_distribution": gender_dist,
        "sales_by_gender": sales_by_gender,
    }


def geographic_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyse des ventes par localisation géographique

    Args:
        df: DataFrame des transactions

    Returns:
        DataFrame avec analyses géographiques
    """
    geo_analysis = (
        df.groupby(["City", "Branch"])
        .agg({"Sales": "sum", "gross income": "sum", "Invoice ID": "count", "Rating": "mean"})
        .rename(columns={"Invoice ID": "transactions", "gross income": "margin"})
        .round(2)
    )

    geo_analysis["margin_percentage"] = (geo_analysis["margin"] / geo_analysis["Sales"] * 100).round(2)

    return geo_analysis.reset_index().sort_values("Sales", ascending=False)


def hourly_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyse des ventes par heure de la journée

    Args:
        df: DataFrame des transactions

    Returns:
        DataFrame avec ventes par heure
    """
    # Extraire l'heure du timestamp
    df_copy = df.copy()
    df_copy["hour"] = pd.to_datetime(df_copy["Time"], format="%I:%M:%S %p").dt.hour

    hourly_sales = (
        df_copy.groupby("hour")
        .agg({"Sales": "sum", "Invoice ID": "count", "Rating": "mean"})
        .rename(columns={"Invoice ID": "transactions"})
        .round(2)
    )

    return hourly_sales.reset_index()


def rating_analysis(df: pd.DataFrame) -> dict[str, Any]:
    """
    Analyse détaillée des ratings de satisfaction

    Args:
        df: DataFrame des transactions

    Returns:
        Dictionnaire avec analyses de rating
    """
    rating_stats = {
        "mean_rating": round(df["Rating"].mean(), 2),
        "median_rating": round(df["Rating"].median(), 2),
        "std_rating": round(df["Rating"].std(), 2),
        "min_rating": float(df["Rating"].min()),
        "max_rating": float(df["Rating"].max()),
    }

    # Distribution des ratings
    rating_dist = df["Rating"].value_counts().sort_index().to_dict()

    # Rating par catégorie
    rating_by_category = df.groupby("Product line")["Rating"].mean().round(2).to_dict()

    return {"statistics": rating_stats, "distribution": rating_dist, "by_category": rating_by_category}


# Fonctions de visualisation


def create_sales_trend_chart(df: pd.DataFrame, period: str = "daily") -> go.Figure:
    """
    Crée le graphique d'évolution des ventes

    Args:
        df: DataFrame des transactions
        period: 'daily', 'weekly', 'monthly'

    Returns:
        Figure Plotly
    """
    time_data = sales_over_time(df, period)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=time_data["period"],
            y=time_data["Sales"],
            mode="lines+markers",
            name="Chiffre d'affaires",
            line={"color": LECLERC_BLUE, "width": 3},
            marker={"size": 6},
        )
    )

    fig.update_layout(
        title=f"Évolution des ventes ({period})",
        xaxis_title="Période",
        yaxis_title="Chiffre d'affaires (€)",
        template="plotly_white",
        **PLOTLY_LAYOUT_CONFIG,
    )

    return fig


def create_category_sales_chart(df: pd.DataFrame) -> go.Figure:
    """
    Crée le graphique des ventes par catégorie

    Args:
        df: DataFrame des transactions

    Returns:
        Figure Plotly
    """
    category_data = sales_by_category(df)

    fig = go.Figure(
        data=[
            go.Bar(
                x=category_data.index,
                y=category_data["Sales"],
                marker={"color": COLOR_PATTERNS["primary"] * (len(category_data) // 2 + 1)},
                text=category_data["Sales"].round(2),
                textposition="auto",
            )
        ]
    )

    fig.update_layout(
        title="Ventes par catégorie",
        xaxis_title="Catégorie",
        yaxis_title="Chiffre d'affaires (€)",
        template="plotly_white",
        **PLOTLY_LAYOUT_CONFIG,
    )

    return fig


def create_payment_pie_chart(df: pd.DataFrame) -> go.Figure:
    """
    Crée le graphique camembert des modes de paiement

    Args:
        df: DataFrame des transactions

    Returns:
        Figure Plotly
    """
    payment_data = payment_distribution(df)

    fig = go.Figure(
        data=[
            go.Pie(
                labels=payment_data["Payment"],
                values=payment_data["count"],
                hole=0.3,
                marker_colors=COLOR_PATTERNS["categorical"],
            )
        ]
    )

    fig.update_layout(title="Répartition des modes de paiement", template="plotly_white", **PLOTLY_LAYOUT_CONFIG)

    return fig


def create_kpi_cards(kpis: dict[str, Any]) -> dict[str, dict]:
    """
    Crée les données pour les cartes KPI

    Args:
        kpis: Dictionnaire des KPIs

    Returns:
        Dictionnaire formaté pour l'affichage
    """
    return {
        "revenue": {
            "title": "Chiffre d'affaires",
            "value": f"€{kpis['total_revenue']:,.2f}",
            "delta": None,
            "color": LECLERC_BLUE,
        },
        "margin": {"title": "Marge totale", "value": f"€{kpis['total_margin']:,.2f}", "delta": None, "color": LECLERC_ORANGE},
        "transactions": {
            "title": "Transactions",
            "value": f"{kpis['total_transactions']:,}",
            "delta": None,
            "color": LECLERC_BLUE,
        },
        "avg_basket": {
            "title": "Panier moyen",
            "value": f"€{kpis['avg_basket']:,.2f}",
            "delta": None,
            "color": LECLERC_ORANGE,
        },
        "rating": {"title": "Satisfaction moyenne", "value": f"{kpis['avg_rating']}/10", "delta": None, "color": LECLERC_BLUE},
    }

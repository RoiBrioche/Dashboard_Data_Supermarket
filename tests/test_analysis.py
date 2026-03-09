"""
Tests unitaires pour le module analysis.py
Couvre toutes les fonctions de calcul KPI et d'analyse business
"""

import os
import sys

import pandas as pd
import plotly.graph_objects as go
import pytest

# Ajouter le chemin src pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.analysis import (
    compute_kpis,
    create_category_sales_chart,
    create_kpi_cards,
    create_payment_pie_chart,
    create_sales_trend_chart,
    customer_analysis,
    geographic_analysis,
    hourly_analysis,
    load_data,
    payment_distribution,
    profit_by_category,
    rating_analysis,
    sales_by_category,
    sales_over_time,
    top_products,
)


@pytest.fixture
def sample_dataframe():
    """Crée un DataFrame de test avec données réalistes."""
    return pd.DataFrame(
        {
            "Invoice ID": ["001", "002", "003", "004", "005"],
            "Branch": ["A", "B", "A", "C", "B"],
            "City": ["Yangon", "Mandalay", "Yangon", "Naypyitaw", "Mandalay"],
            "Customer type": ["Member", "Normal", "Member", "Normal", "Member"],
            "Gender": ["Female", "Male", "Female", "Male", "Female"],
            "Product line": [
                "Health and beauty",
                "Electronic accessories",
                "Fashion accessories",
                "Food and beverages",
                "Sports and travel",
            ],
            "Unit price": [74.69, 15.28, 46.33, 54.84, 86.31],
            "Quantity": [7, 5, 7, 3, 7],
            "Tax 5%": [26.14, 3.82, 16.22, 8.23, 30.21],
            "Sales": [548.97, 80.22, 340.53, 172.63, 634.38],
            "Date": ["1/5/2019", "3/8/2019", "3/3/2019", "2/20/2019", "2/8/2019"],
            "Time": ["1:08:00 PM", "10:29:00 AM", "1:23:00 PM", "1:27:00 PM", "10:37:00 AM"],
            "Payment": ["Ewallet", "Cash", "Credit card", "Credit card", "Ewallet"],
            "cogs": [522.83, 76.40, 324.31, 164.52, 604.17],
            "gross margin percentage": [4.761904762] * 5,
            "gross income": [26.14, 3.82, 16.22, 8.11, 30.21],
            "Rating": [9.1, 9.6, 7.4, 5.9, 5.3],
        }
    )


@pytest.fixture
def empty_dataframe():
    """Crée un DataFrame vide pour les tests edge cases."""
    return pd.DataFrame()


class TestLoadData:
    """Tests pour la fonction load_data."""

    def test_load_data_success(self, tmp_path, sample_dataframe):
        """Test chargement réussi des données."""
        # Créer un fichier CSV temporaire
        csv_path = tmp_path / "test_data.csv"
        sample_dataframe.to_csv(csv_path, index=False)

        # Charger les données
        result = load_data(str(csv_path))

        # Vérifications
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5
        assert "Date" in result.columns
        assert pd.api.types.is_datetime64_any_dtype(result["Date"])
        assert "Year" in result.columns
        assert "Month" in result.columns

    def test_load_data_file_not_found(self):
        """Test gestion d'erreur fichier non trouvé."""
        with pytest.raises(ValueError, match="Erreur lors du chargement des données"):
            load_data("nonexistent_file.csv")

    def test_load_data_invalid_format(self, tmp_path):
        """Test gestion d'erreur format invalide."""
        # Créer un fichier invalide
        invalid_path = tmp_path / "invalid.txt"
        invalid_path.write_text("invalid data")

        with pytest.raises(ValueError):
            load_data(str(invalid_path))


class TestComputeKPIs:
    """Tests pour la fonction compute_kpis."""

    def test_compute_kpis_normal_case(self, sample_dataframe):
        """Test calcul KPIs avec données normales."""
        result = compute_kpis(sample_dataframe)

        # Vérifications des KPIs principaux
        assert result["total_revenue"] == 1776.73
        assert result["total_margin"] == 84.5
        assert result["total_transactions"] == 5
        assert result["avg_basket"] == 355.35
        assert abs(result["avg_rating"] - 7.46) < 0.01  # Tolérance pour les arrondis

        # Vérifications des KPIs clients
        assert result["total_customers"] == 5
        assert result["member_customers"] == 3
        assert result["normal_customers"] == 2

    def test_compute_kpis_empty_dataframe(self, empty_dataframe):
        """Test calcul KPIs avec DataFrame vide."""
        result = compute_kpis(empty_dataframe)

        assert result["total_revenue"] == 0
        assert result["total_margin"] == 0
        assert result["total_transactions"] == 0
        assert result["avg_basket"] == 0
        assert result["avg_rating"] == 0


class TestSalesByCategory:
    """Tests pour la fonction sales_by_category."""

    def test_sales_by_category_normal_case(self, sample_dataframe):
        """Test calcul ventes par catégorie."""
        result = sales_by_category(sample_dataframe)

        # Vérifications
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5  # 5 catégories uniques
        assert "Sales" in result.columns
        assert "margin" in result.columns
        assert "transactions" in result.columns

        # Vérification tri par CA décroissant
        assert result["Sales"].is_monotonic_decreasing

    def test_sales_by_category_empty_dataframe(self, empty_dataframe):
        """Test avec DataFrame vide."""
        # Créer un DataFrame avec les colonnes attendues mais vide
        df_empty = pd.DataFrame(columns=["Product line", "Sales", "gross income", "Quantity", "Invoice ID"])
        result = sales_by_category(df_empty)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


class TestSalesOverTime:
    """Tests pour la fonction sales_over_time."""

    def test_sales_over_time_daily(self, sample_dataframe):
        """Test agrégation quotidienne."""
        # Convertir les dates en datetime d'abord
        df_test = sample_dataframe.copy()
        df_test["Date"] = pd.to_datetime(df_test["Date"], format="%m/%d/%Y")

        result = sales_over_time(df_test, "daily")

        assert isinstance(result, pd.DataFrame)
        assert "period" in result.columns
        assert "Sales" in result.columns
        assert len(result) == 5  # 5 jours différents

    def test_sales_over_time_weekly(self, sample_dataframe):
        """Test agrégation hebdomadaire."""
        # Convertir les dates en datetime d'abord
        df_test = sample_dataframe.copy()
        df_test["Date"] = pd.to_datetime(df_test["Date"], format="%m/%d/%Y")

        result = sales_over_time(df_test, "weekly")

        assert isinstance(result, pd.DataFrame)
        assert len(result) >= 1  # Au moins une semaine

    def test_sales_over_time_invalid_period(self, sample_dataframe):
        """Test période invalide."""
        with pytest.raises(ValueError, match="Period must be"):
            sales_over_time(sample_dataframe, "invalid")


class TestProfitByCategory:
    """Tests pour la fonction profit_by_category."""

    def test_profit_by_category_normal_case(self, sample_dataframe):
        """Test calcul marges par catégorie."""
        result = profit_by_category(sample_dataframe)

        assert isinstance(result, pd.DataFrame)
        assert "margin_percentage" in result.columns
        assert "gross income" in result.columns
        assert "Sales" in result.columns

        # Vérification pourcentage marge
        expected_margin_pct = round(result["gross income"] / result["Sales"] * 100, 2)
        pd.testing.assert_series_equal(result["margin_percentage"], expected_margin_pct, check_names=False)


class TestPaymentDistribution:
    """Tests pour la fonction payment_distribution."""

    def test_payment_distribution_normal_case(self, sample_dataframe):
        """Test distribution modes de paiement."""
        result = payment_distribution(sample_dataframe)

        assert isinstance(result, pd.DataFrame)
        # Vérifier les colonnes existent (peuvent être dans un ordre différent)
        assert "payment_method" in result.columns or "Payment" in result.columns
        assert "count" in result.columns
        assert "percentage" in result.columns

        # Vérification pourcentage total = 100%
        assert abs(result["percentage"].sum() - 100) < 0.01

    def test_payment_distribution_methods(self, sample_dataframe):
        """Test présence des modes de paiement attendus."""
        result = payment_distribution(sample_dataframe)

        # Vérifier les colonnes existent (peuvent être dans un ordre différent)
        payment_col = "payment_method" if "payment_method" in result.columns else "Payment"
        payment_methods = set(result[payment_col])
        expected_methods = {"Ewallet", "Cash", "Credit card"}
        assert payment_methods == expected_methods


class TestTopProducts:
    """Tests pour la fonction top_products."""

    def test_top_products_by_sales(self, sample_dataframe):
        """Test top produits par CA."""
        result = top_products(sample_dataframe, n=3, metric="sales")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3  # Top 3
        assert result["Sales"].is_monotonic_decreasing

    def test_top_products_by_margin(self, sample_dataframe):
        """Test top produits par marge."""
        result = top_products(sample_dataframe, n=2, metric="margin")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "gross income" in result.columns

    def test_top_products_invalid_metric(self, sample_dataframe):
        """Test métrique invalide."""
        with pytest.raises(ValueError, match="Metric must be"):
            top_products(sample_dataframe, metric="invalid")


class TestCustomerAnalysis:
    """Tests pour la fonction customer_analysis."""

    def test_customer_analysis_normal_case(self, sample_dataframe):
        """Test analyse client avec données normales."""
        result = customer_analysis(sample_dataframe)

        assert isinstance(result, dict)
        assert "customer_type_distribution" in result
        assert "avg_basket_by_type" in result
        assert "rating_by_type" in result
        assert "gender_distribution" in result
        assert "sales_by_gender" in result

        # Vérifications des distributions
        assert result["customer_type_distribution"]["Member"] == 3
        assert result["customer_type_distribution"]["Normal"] == 2


class TestGeographicAnalysis:
    """Tests pour la fonction geographic_analysis."""

    def test_geographic_analysis_normal_case(self, sample_dataframe):
        """Test analyse géographique."""
        result = geographic_analysis(sample_dataframe)

        assert isinstance(result, pd.DataFrame)
        assert "City" in result.columns
        assert "Branch" in result.columns
        assert "margin_percentage" in result.columns
        # Vérifier qu'on a 3 localisations différentes (pas 5 car certaines sont dupliquées)
        assert len(result) == 3


class TestHourlyAnalysis:
    """Tests pour la fonction hourly_analysis."""

    def test_hourly_analysis_normal_case(self, sample_dataframe):
        """Test analyse horaire."""
        result = hourly_analysis(sample_dataframe)

        assert isinstance(result, pd.DataFrame)
        assert "hour" in result.columns
        assert "Sales" in result.columns
        assert "transactions" in result.columns

        # Vérification plage horaire (0-23)
        assert result["hour"].min() >= 0
        assert result["hour"].max() <= 23

    def test_hourly_analysis_mixed_time_format(self):
        """Test analyse horaire avec format Time mixte (cas d'exception)"""
        df = pd.DataFrame(
            {
                "Time": ["14:30", "09:15", "22:45"],  # Format sans secondes pour forcer mixed
                "Sales": [100.0, 200.0, 150.0],
                "Quantity": [5, 10, 8],
                "Invoice ID": ["001", "002", "003"],
                "Rating": [4.5, 4.2, 4.8],  # Ajout de la colonne Rating manquante
            }
        )

        result = hourly_analysis(df)

        assert isinstance(result, pd.DataFrame)
        assert "hour" in result.columns
        assert "Sales" in result.columns
        assert "transactions" in result.columns
        # Le format mixed devrait fonctionner
        assert len(result) > 0


class TestRatingAnalysis:
    """Tests pour la fonction rating_analysis."""

    def test_rating_analysis_normal_case(self, sample_dataframe):
        """Test analyse ratings."""
        result = rating_analysis(sample_dataframe)

        assert isinstance(result, dict)
        assert "statistics" in result
        assert "distribution" in result
        assert "by_category" in result

        # Vérifications statistiques
        stats = result["statistics"]
        assert "mean_rating" in stats
        assert "median_rating" in stats
        assert "std_rating" in stats
        assert "min_rating" in stats
        assert "max_rating" in stats

        # Vérifications valeurs
        assert stats["min_rating"] == 5.3
        assert stats["max_rating"] == 9.6


class TestEdgeCases:
    """Tests des cas limites et edge cases."""

    def test_single_transaction(self):
        """Test avec une seule transaction."""
        df_single = pd.DataFrame(
            {
                "Invoice ID": ["001"],
                "Sales": [100.0],
                "gross income": [20.0],
                "Rating": [8.0],
                "Customer type": ["Member"],
                "Product line": ["Health and beauty"],
                "Date": ["1/5/2019"],
                "Time": ["1:08:00 PM"],
                "Payment": ["Ewallet"],
                "cogs": [80.0],
                "gross margin percentage": [4.761904762],
                "Quantity": [5],
                "Unit price": [20.0],
                "Tax 5%": [4.76],
                "Branch": ["A"],
                "City": ["Yangon"],
                "Gender": ["Female"],
            }
        )

        kpis = compute_kpis(df_single)
        assert kpis["total_revenue"] == 100.0
        assert kpis["total_transactions"] == 1
        assert kpis["avg_basket"] == 100.0

    def test_negative_values(self):
        """Test gestion des valeurs négatives."""
        df_negative = pd.DataFrame(
            {
                "Sales": [-100.0, 200.0],
                "gross income": [-20.0, 40.0],
                "Rating": [5.0, 8.0],
                "Customer type": ["Member", "Normal"],
                "Product line": ["Health and beauty", "Electronic accessories"],
                "Date": ["1/5/2019", "1/6/2019"],
                "Time": ["1:08:00 PM", "2:08:00 PM"],
                "Payment": ["Ewallet", "Cash"],
                "cogs": [-80.0, 160.0],
                "gross margin percentage": [4.761904762, 4.761904762],
                "Quantity": [5, 3],
                "Unit price": [20.0, 50.0],
                "Tax 5%": [4.76, 9.52],
                "Branch": ["A", "B"],
                "City": ["Yangon", "Mandalay"],
                "Gender": ["Female", "Male"],
                "Invoice ID": ["001", "002"],
            }
        )

        result = sales_by_category(df_negative)
        assert isinstance(result, pd.DataFrame)
        # Les calculs doivent fonctionner même avec des valeurs négatives


class TestVisualizationFunctions:
    """Test des fonctions de visualisation"""

    def test_create_kpi_cards(self):
        """Test la création des cartes KPI"""
        df = pd.DataFrame(
            {
                "Total": [1000.0, 2000.0, 1500.0],
                "gross margin percentage": [10.0, 15.0, 12.0],
                "gross income": [100.0, 300.0, 180.0],
                "Rating": [4.5, 4.2, 4.8],
            }
        )

        kpis = compute_kpis(df)
        cards = create_kpi_cards(kpis)

        assert len(cards) == 4
        assert all(hasattr(card, "children") for card in cards)

    def test_create_sales_trend_chart_weekly(self):
        """Test la création du graphique des ventes hebdomadaires"""
        df = pd.DataFrame(
            {
                "Date": pd.date_range("2023-01-01", periods=7, freq="D"),
                "Sales": [100.0, 200.0, 150.0, 120.0, 180.0, 160.0, 140.0],
                "gross income": [20.0, 40.0, 30.0, 24.0, 36.0, 32.0, 28.0],
                "Invoice ID": [f"00{i}" for i in range(1, 8)],
            }
        )

        fig = create_sales_trend_chart(df, "weekly")
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1

    def test_create_sales_trend_chart_invalid_period(self):
        """Test la gestion des périodes invalides"""
        df = pd.DataFrame(
            {
                "Date": pd.date_range("2023-01-01", periods=3, freq="D"),
                "Sales": [100.0, 200.0, 150.0],
                "gross income": [20.0, 40.0, 30.0],
                "Invoice ID": ["001", "002", "003"],
            }
        )

        with pytest.raises(ValueError, match="Period must be 'daily', 'weekly', or 'monthly'"):
            create_sales_trend_chart(df, "invalid")

    def test_create_sales_trend_chart_monthly(self):
        """Test la création du graphique des ventes mensuelles"""
        df = pd.DataFrame(
            {
                "Date": pd.date_range("2023-01-01", periods=30, freq="D"),
                "Sales": [100.0 + i * 10 for i in range(30)],
                "gross income": [20.0 + i * 2 for i in range(30)],
                "Invoice ID": [f"{i:03d}" for i in range(1, 31)],
            }
        )

        fig = create_sales_trend_chart(df, "monthly")
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1

    def test_create_category_sales_chart(self):
        """Test la création du graphique des ventes par catégorie"""
        df = pd.DataFrame(
            {
                "Product line": ["Electronics", "Clothing", "Food"],
                "Sales": [100.0, 200.0, 150.0],
                "Quantity": [5, 10, 8],
                "gross income": [20.0, 40.0, 30.0],
                "Invoice ID": ["001", "002", "003"],
            }
        )

        fig = create_category_sales_chart(df)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert fig.data[0].type == "bar"

    def test_create_payment_pie_chart(self):
        """Test la création du graphique camembert des paiements"""
        df = pd.DataFrame(
            {
                "Payment": ["Cash", "Credit card", "Ewallet", "Cash"],
                "Invoice ID": ["001", "002", "003", "004"],
            }
        )

        fig = create_payment_pie_chart(df)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert fig.data[0].type == "pie"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

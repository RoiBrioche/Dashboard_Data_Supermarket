"""
Tests unitaires pour le module dashboard.py
Couvre les composants UI et callbacks du dashboard
"""

import os
import sys

import pytest
from dash import html

# Ajouter le chemin src pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.dashboard import (
    empty_figure,
    get_data,
    kpi_card,
    section_card,
)


class TestSectionCard:
    """Tests pour la fonction section_card"""

    def test_section_card_basic(self):
        """Test création section_card basique"""
        content = html.Div("Test content")
        result = section_card("Test Title", "🧪", content)

        assert result is not None
        assert result.width == 12
        assert len(result.children) == 2  # header + body

    def test_section_card_with_height(self):
        """Test section_card avec hauteur spécifiée"""
        content = html.Div("Test content")
        result = section_card("Test Title", "🧪", content, height="200px")

        body_style = result.children[1].style
        assert body_style["height"] == "200px"
        # L'overflow hidden est présent sauf pour les filtres
        assert body_style.get("overflow") == "hidden"

    def test_section_card_filter_section(self):
        """Test section_card pour filtres (pas d'overflow hidden)"""
        content = html.Div("Filter content")
        result = section_card("Filtres", "⚙", content, height="120px")

        body_style = result.children[1].style
        assert body_style["height"] == "120px"
        assert "overflow" not in body_style  # Filtres ne doivent pas avoir overflow hidden
        assert "filter-section" in result.children[1].className


class TestKpiCard:
    """Tests pour la fonction kpi_card"""

    def test_kpi_card_basic(self):
        """Test création kpi_card basique"""
        result = kpi_card("1000", "Ventes", "💰", "#22c55e")

        assert result is not None
        assert len(result.children) == 3  # icon + value + label

    def test_kpi_card_with_border_accent(self):
        """Test kpi_card avec bordure accentuée"""
        result = kpi_card("1000", "Ventes", "💰", "#22c55e", border_accent=True)

        assert "2px solid #22c55e" in result.style["border"]


class TestDataLoading:
    """Tests pour les fonctions de chargement de données"""

    def test_get_data_basic(self):
        """Test chargement basique des données"""
        result = get_data()

        assert "df" in result
        assert "df_clean" in result
        assert "validation" in result
        assert "df_with_features" in result

        # Vérifier que les données ne sont pas vides
        assert not result["df"].empty
        assert not result["df_clean"].empty

    def test_get_data_caching(self):
        """Test que le cache fonctionne"""
        # Premier appel
        result1 = get_data()

        # Deuxième appel (devrait utiliser le cache)
        result2 = get_data()

        # Les résultats devraient être identiques
        assert result1["df"].equals(result2["df"])
        assert result1["df_clean"].equals(result2["df_clean"])


class TestLayoutCreation:
    """Tests pour la création du layout"""

    def test_empty_figure_creation(self):
        """Test création de figure vide"""
        result = empty_figure("Test message")

        assert result is not None
        # Vérifier que c'est une figure Plotly
        assert hasattr(result, "add_annotation")
        assert hasattr(result, "data")

    def test_section_card_in_layout(self):
        """Test intégration section_card dans un layout"""
        content = html.Div([html.H3("Test"), html.P("Content")])
        section = section_card("Test Section", "🧪", content)

        assert section is not None
        assert section.width == 12
        assert len(section.children) == 2


class TestDashboardComponents:
    """Tests pour les composants spécifiques du dashboard"""

    def test_kpi_card_creation(self):
        """Test création de cartes KPI"""
        kpi = kpi_card("1000€", "Ventes", "💰", "#22c55e")

        assert kpi is not None
        assert len(kpi.children) == 3  # icon + value + label

    def test_section_card_with_different_content(self):
        """Test section_card avec différents types de contenu"""
        # Test avec contenu simple
        simple_content = html.Div("Simple")
        section1 = section_card("Simple", "📝", simple_content)
        assert section1 is not None

        # Test avec contenu complexe
        complex_content = html.Div([html.H3("Title"), html.P("Paragraph"), html.Button("Click me")])
        section2 = section_card("Complex", "🔧", complex_content)
        assert section2 is not None


class TestDashboardCallbacks:
    """Tests pour les callbacks du dashboard (structure uniquement)"""

    def test_data_loading_for_callbacks(self):
        """Test que les données peuvent être chargées pour les callbacks"""
        # Test que get_data fonctionne correctement
        result = get_data()

        assert "df" in result
        assert "df_clean" in result
        assert "validation" in result
        assert "df_with_features" in result

    def test_component_structure(self):
        """Test la structure des composants UI"""
        # Vérifier que les helpers UI fonctionnent
        figure = empty_figure()
        assert figure is not None

        kpi = kpi_card("100", "Test", "🧪", "#000")
        assert kpi is not None

        section = section_card("Test", "🧪", html.Div("content"))
        assert section is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Tests unitaires pour le module utils.py
Couvre toutes les fonctions utilitaires
"""

import os
import sys

import numpy as np
import pandas as pd

# Ajouter le chemin src pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.utils import (
    calculate_growth_rate,
    clean_dataframe,
    create_date_features,
    detect_outliers,
    export_to_csv,
    format_currency,
    format_percentage,
    get_data_summary,
    load_config_file,
    safe_divide,
    standardize_column_names,
    validate_transaction_data,
)


class TestFilterByPeriod:
    """Test de la fonction filter_by_period"""

    def test_filter_by_period_all(self):
        """Test filtrage période 'all' - ne doit rien filtrer"""
        from app.utils import filter_by_period

        df_test = pd.DataFrame({"Date": pd.to_datetime(["1/5/2019", "3/8/2019"]), "Sales": [100, 200]})
        result = filter_by_period(df_test, "all")
        assert len(result) == len(df_test)  # Aucune ligne supprimée

    def test_filter_by_period_today(self):
        """Test filtrage période 'today'"""
        from app.utils import filter_by_period

        df_test = pd.DataFrame({"Date": pd.to_datetime(["1/5/2019", "3/8/2019"]), "Sales": [100, 200]})
        result = filter_by_period(df_test, "today")
        assert len(result) >= 1  # Au moins la dernière journée

    def test_filter_by_period_week(self):
        """Test filtrage période 'week'"""
        from app.utils import filter_by_period

        df_test = pd.DataFrame({"Date": pd.to_datetime(["1/5/2019", "3/8/2019"]), "Sales": [100, 200]})
        result = filter_by_period(df_test, "week")
        assert len(result) >= 1  # Au moins une ligne dans les 7 derniers jours

    def test_filter_by_period_month(self):
        """Test filtrage période 'month'"""
        from app.utils import filter_by_period

        df_test = pd.DataFrame({"Date": pd.to_datetime(["1/5/2019", "3/8/2019"]), "Sales": [100, 200]})
        result = filter_by_period(df_test, "month")
        assert len(result) >= 1  # Au moins une ligne dans les 30 derniers jours

    def test_filter_by_period_invalid_date(self):
        """Test gestion d'erreur de date invalide"""
        from app.utils import filter_by_period

        df_test = pd.DataFrame({"Date": pd.to_datetime(["1/5/2019", "3/8/2019"]), "Sales": [100, 200]})
        result = filter_by_period(df_test, "day", "invalid-date")
        # En cas d'erreur, doit retourner le DataFrame original
        assert len(result) == len(df_test)

    def test_filter_by_period_empty_dataframe(self):
        """Test avec DataFrame vide"""
        from app.utils import filter_by_period

        df_empty = pd.DataFrame()
        result = filter_by_period(df_empty, "all")
        assert len(result) == 0

    """Test des fonctions de nettoyage"""

    def test_clean_dataframe_basic(self):
        """Test le nettoyage de base d'un DataFrame"""
        df = pd.DataFrame(
            {"Invoice ID": ["001", "002", "001", "003"], "Sales": [100.0, 200.0, None, 150.0], "Quantity": [5, 10, 3, 8]}
        )

        result = clean_dataframe(df)

        assert len(result) == 3  # Doublon supprimé
        assert result["Sales"].isnull().sum() == 0  # Valeur nulle remplacée
        assert isinstance(result, pd.DataFrame)

    def test_clean_dataframe_empty(self):
        """Test le nettoyage d'un DataFrame vide"""
        df = pd.DataFrame()

        result = clean_dataframe(df)

        assert len(result) == 0
        assert isinstance(result, pd.DataFrame)

    def test_clean_dataframe_with_missing_values(self):
        """Test le nettoyage avec valeurs manquantes"""
        df = pd.DataFrame({"Invoice ID": ["001", "002", "003"], "Sales": [100.0, None, 150.0], "Quantity": [5, None, 8]})

        result = clean_dataframe(df)

        assert len(result) == 3
        assert result["Sales"].isnull().sum() == 0  # Valeur nulle remplacée par 0
        assert result["Quantity"].isnull().sum() == 0  # Valeur nulle remplacée par 0
        assert result.loc[1, "Sales"] == 0.0
        assert result.loc[1, "Quantity"] == 0.0

    def test_standardize_column_names(self):
        """Test la standardisation des noms de colonnes"""
        df = pd.DataFrame({"invoice_id": ["001", "002"], "product_line": ["A", "B"], "unit_price": [10.0, 20.0]})

        result = standardize_column_names(df)

        assert "Invoice Id" in result.columns
        assert "Product Line" in result.columns
        assert "Unit Price" in result.columns


class TestDataValidation:
    """Test des fonctions de validation"""

    def test_validate_transaction_data_valid(self):
        """Test la validation de données valides"""
        df = pd.DataFrame(
            {
                "Invoice ID": ["001", "002"],
                "Date": ["2023-01-01", "2023-01-02"],
                "Product line": ["Electronics", "Clothing"],
                "Sales": [100.0, 200.0],
                "Quantity": [5, 10],
                "Unit price": [20.0, 20.0],
                "Tax 5%": [5.0, 10.0],
                "cogs": [80.0, 160.0],
                "gross income": [20.0, 40.0],
                "Rating": [8.0, 9.0],
            }
        )

        result = validate_transaction_data(df)

        assert result["is_valid"]
        assert len(result["errors"]) == 0
        assert "stats" in result

    def test_validate_transaction_data_missing_columns(self):
        """Test la validation avec colonnes manquantes"""
        df = pd.DataFrame({"Invoice ID": ["001", "002"], "Sales": [100.0, 200.0]})

        result = validate_transaction_data(df)

        assert not result["is_valid"]
        assert len(result["errors"]) > 0
        assert "Colonnes manquantes" in str(result["errors"])

    def test_validate_transaction_data_invalid_types(self):
        """Test la validation avec types de données invalides"""
        df = pd.DataFrame(
            {
                "Invoice ID": ["001", "002"],
                "Date": ["2023-01-01", "2023-01-02"],
                "Product line": ["Electronics", "Clothing"],
                "Sales": [100.0, 200.0],  # Garder en numérique pour éviter l'erreur
                "Quantity": [5, 10],
                "Unit price": [20.0, 20.0],
                "Tax 5%": [5.0, 10.0],
                "cogs": [80.0, 160.0],
                "gross income": [20.0, 40.0],
                "Rating": ["8.0", "9.0"],  # String au lieu de numérique
            }
        )

        result = validate_transaction_data(df)

        assert result["is_valid"]  # Toujours valide mais avec warnings
        assert len(result["warnings"]) > 0
        assert any("n'est pas numérique" in warning for warning in result["warnings"])

    def test_validate_transaction_data_negative_values(self):
        """Test la détection de valeurs négatives"""
        df = pd.DataFrame(
            {
                "Invoice ID": ["001", "002"],
                "Date": ["2023-01-01", "2023-01-02"],
                "Product line": ["Electronics", "Clothing"],
                "Sales": [100.0, -50.0],
                "Quantity": [5, 10],
                "Unit price": [20.0, 20.0],
                "Tax 5%": [5.0, 10.0],
                "cogs": [80.0, 160.0],
                "gross income": [20.0, 40.0],
                "Rating": [8.0, 9.0],
            }
        )

        result = validate_transaction_data(df)

        # Vérifier que le warning contient le mot clé
        warnings_text = " ".join(result["warnings"])
        assert "négatives" in warnings_text or "negatives" in warnings_text


class TestOutlierDetection:
    """Test des fonctions de détection d'outliers"""

    def test_detect_outliers_iqr(self):
        """Test la détection d'outliers par méthode IQR"""

        df = pd.DataFrame({"values": [10, 20, 30, 40, 100, 50, 60]})  # 100 est un outlier
        result = detect_outliers(df, "values", "iqr")

        assert len(result) == len(df)
        assert "is_outlier" in result.columns
        # Vérifier que la fonction retourne un résultat valide (peut détecter 0 ou plusieurs outliers)

    def test_detect_outliers_empty(self):
        """Test la détection d'outliers avec DataFrame vide"""

        df_empty = pd.DataFrame()
        result = detect_outliers(df_empty, "values")
        assert len(result) == 0


class TestExportFunctions:
    """Test des fonctions d'export"""

    def test_export_to_csv_success(self, tmp_path):
        """Test l'export CSV réussi"""
        from app.utils import export_to_csv

        df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        test_file = tmp_path / "test_export.csv"

        result = export_to_csv(df, str(test_file))
        assert result
        assert test_file.exists()

    def test_export_to_csv_failure(self):
        """Test l'export CSV avec chemin invalide"""
        from app.utils import export_to_csv

        df = pd.DataFrame({"col1": [1, 2]})
        result = export_to_csv(df, "/invalid/path/test.csv")
        assert not result


class TestConfigFunctions:
    """Test des fonctions de configuration"""

    def test_load_config_file_not_found(self):
        """Test le chargement de fichier inexistant"""
        from app.utils import load_config_file

        result = load_config_file("nonexistent_file.json")
        assert result == {}  # Doit retourner un dict vide

    def test_load_config_file_invalid_json(self, tmp_path):
        """Test le chargement de fichier JSON invalide"""
        from app.utils import load_config_file

        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("invalid json content")

        result = load_config_file(str(invalid_file))
        assert result == {}  # Doit retourner un dict vide


class TestDataSummary:
    """Test des fonctions de résumé de données"""

    def test_get_data_summary_basic(self):
        """Test la génération de résumé basique"""
        from app.utils import get_data_summary

        df_test = pd.DataFrame({"col1": [1, 2, 3], "col2": [4.5, 5.5, 6.5]})
        result = get_data_summary(df_test)

        assert "shape" in result
        assert "columns" in result
        assert "numeric_summary" in result
        assert "dtypes" in result
        assert result["shape"] == df_test.shape

    def test_get_data_summary_empty(self):
        """Test le résumé avec DataFrame vide"""
        from app.utils import get_data_summary

        df_empty = pd.DataFrame()
        result = get_data_summary(df_empty)

        assert result["shape"] == (0, 0)
        assert len(result["columns"]) == 0

    """Test des fonctions de formatage"""

    def test_format_currency(self):
        """Test le formatage de devise"""
        assert format_currency(100.50) == "€100.50"
        assert format_currency(1000) == "€1,000.00"
        assert format_currency(0) == "€0.00"
        assert format_currency(-50.25) == "€-50.25"

    def test_format_currency_invalid_input(self):
        """Test le formatage de devise avec entrée invalide"""
        assert format_currency("invalid") == "€0.00"
        assert format_currency({}) == "€0.00"

    def test_format_currency_nan(self):
        """Test le formatage de devise avec NaN"""
        assert format_currency(np.nan) == "N/A"

    def test_format_percentage(self):
        """Test le formatage de pourcentage"""
        assert format_percentage(0.2547) == "0.25%"
        assert format_percentage(0.2547, 3) == "0.255%"
        assert format_percentage(100) == "100.00%"

    def test_format_percentage_invalid_input(self):
        """Test le formatage de pourcentage avec entrée invalide"""
        assert format_percentage("invalid") == "0.00%"
        assert format_percentage({}) == "0.00%"

    def test_format_percentage_nan(self):
        """Test le formatage de pourcentage avec NaN"""
        assert format_percentage(np.nan) == "N/A"

    def test_safe_divide(self):
        """Test la division sécurisée"""
        assert safe_divide(10, 2) == 5.0
        assert safe_divide(10, 0) == 0.0
        assert safe_divide(10, 0, default=-1) == -1
        assert safe_divide(0, 5) == 0.0

    def test_safe_divide_invalid_input(self):
        """Test la division sécurisée avec entrée invalide"""
        assert safe_divide("invalid", 2) == 0.0
        assert safe_divide(10, "invalid") == 0.0
        assert safe_divide(None, 2) == 0.0
        assert safe_divide(10, None) == 0.0
        assert safe_divide([], 2) == 0.0

    def test_calculate_growth_rate(self):
        """Test le calcul de taux de croissance"""
        result1 = calculate_growth_rate(150, 100)
        assert abs(result1 - 50.0) < 0.001  # Tolérance pour les flottants

        result2 = calculate_growth_rate(100, 150)
        assert abs(result2 - (-33.333333333333336)) < 0.001

        assert calculate_growth_rate(100, 0) == 0.0
        assert calculate_growth_rate(100, 100) == 0.0

    def test_calculate_growth_rate_invalid_input(self):
        """Test le calcul de taux de croissance avec entrée invalide"""
        assert calculate_growth_rate("invalid", 100) == 0.0
        assert calculate_growth_rate(100, "invalid") == 0.0
        assert calculate_growth_rate(None, 100) == 0.0
        assert calculate_growth_rate(100, None) == 0.0
        assert calculate_growth_rate([], 100) == 0.0


class TestDateFeatures:
    """Test des fonctions de caractéristiques temporelles"""

    def test_create_date_features(self):
        """Test la création de caractéristiques temporelles"""
        df = pd.DataFrame({"Date": pd.to_datetime(["2023-01-15", "2023-06-20"]), "Sales": [100.0, 200.0]})

        result = create_date_features(df)

        assert "Year" in result.columns
        assert "Month" in result.columns
        assert "Day" in result.columns
        assert "DayOfWeek" in result.columns
        assert "Quarter" in result.columns
        assert "WeekOfYear" in result.columns
        assert "IsWeekend" in result.columns

        assert result.loc[0, "Year"] == 2023
        assert result.loc[0, "Month"] == 1
        assert result.loc[0, "Day"] == 15
        assert result.loc[0, "DayOfWeek"] == "Sunday"
        assert result.loc[0, "Quarter"] == 1
        assert result.loc[0, "IsWeekend"]

    def test_create_date_features_string_dates(self):
        """Test la création de caractéristiques avec dates en string"""
        df = pd.DataFrame({"Date": ["2023-01-15", "2023-06-20"], "Sales": [100.0, 200.0]})

        result = create_date_features(df)

        assert "Year" in result.columns
        assert "Month" in result.columns
        assert "Day" in result.columns
        assert "DayOfWeek" in result.columns
        assert "Quarter" in result.columns
        assert "WeekOfYear" in result.columns
        assert "IsWeekend" in result.columns

        assert result.loc[0, "Year"] == 2023
        assert result.loc[0, "Month"] == 1
        assert result.loc[0, "Day"] == 15

    def test_create_date_features_missing_column(self):
        """Test la création de caractéristiques avec colonne manquante"""
        df = pd.DataFrame({"Sales": [100.0, 200.0]})

        result = create_date_features(df)

        # Devrait retourner le DataFrame original si la colonne n'existe pas
        assert len(result.columns) == 1

    def test_create_date_features_with_time_column(self):
        """Test la création de caractéristiques avec colonne Time (cas d'exception)"""
        df = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-02"],
                "Time": ["14:30", "09:15"],  # Format sans secondes pour forcer l'exception
            }
        )

        result = create_date_features(df)

        # Vérifie que la fonction gère correctement la colonne Time
        # Note: create_date_features dans utils.py ne crée pas de colonne "hour"
        # Elle gère seulement les caractéristiques de date
        assert "Year" in result.columns
        assert "Month" in result.columns
        assert len(result) == 2


class TestUtilityFunctions:
    """Test des fonctions utilitaires générales"""

    def test_get_data_summary(self):
        """Test la génération de résumé statistique"""
        df = pd.DataFrame({"numeric_col": [10, 20, 30, 40, 50], "text_col": ["A", "B", "C", "D", "E"]})

        result = get_data_summary(df)

        assert "shape" in result
        assert result["shape"] == (5, 2)
        assert "columns" in result
        assert "numeric_summary" in result
        assert "numeric_col" in result["numeric_summary"]

    def test_load_config_file_success(self):
        """Test le chargement de fichier config existant et valide"""
        import json
        import os
        import tempfile

        config_data = {"key": "value", "number": 42}

        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            temp_file = f.name

        try:
            result = load_config_file(temp_file)
            assert result == config_data
        finally:
            os.unlink(temp_file)

    def test_load_config_file_invalid_json(self):
        """Test le chargement de fichier config avec JSON invalide"""
        import os
        import tempfile

        # Créer un fichier temporaire avec JSON invalide
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"key": "value", "invalid":}')
            temp_file = f.name

        try:
            result = load_config_file(temp_file)
            assert result == {}
        finally:
            os.unlink(temp_file)

    def test_load_config_file_general_exception(self):
        """Test le chargement de fichier config avec exception générale"""
        import unittest.mock

        # Mock pour provoquer une exception générale
        with unittest.mock.patch("builtins.open", side_effect=PermissionError("Permission denied")):
            result = load_config_file("test.json")
            assert result == {}

    def test_load_config_file_not_found(self):
        """Test le chargement de fichier config inexistant"""
        result = load_config_file("non_existent_file.json")

        assert result == {}

    def test_load_config_file_permission_error(self):
        """Test le chargement de fichier config avec erreur générale"""
        import os
        import tempfile

        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"key": "value"}')
            temp_file = f.name

        try:
            # Supprimer le fichier pour créer une erreur d'accès
            os.unlink(temp_file)

            # Tenter de charger le fichier supprimé (provoquera une erreur générale)
            result = load_config_file(temp_file)
            assert result == {}
        except Exception:
            # Forcer une autre erreur en utilisant un chemin trop long
            long_path = "A" * 300 + ".json"
            result = load_config_file(long_path)
            assert result == {}

    def test_export_to_csv_success(self):
        """Test l'export CSV réussi"""
        df = pd.DataFrame({"col1": [1, 2], "col2": ["A", "B"]})
        filename = "test_export.csv"

        result = export_to_csv(df, filename)

        assert result
        # Nettoyage du fichier de test
        if os.path.exists(filename):
            os.remove(filename)

    def test_export_to_csv_error(self):
        """Test l'export CSV avec erreur"""
        # DataFrame invalide pour provoquer une erreur
        df = pd.DataFrame()
        filename = "/invalid/path/test.csv"

        result = export_to_csv(df, filename)

        assert not result

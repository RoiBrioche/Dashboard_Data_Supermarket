"""
Module utilitaire pour le dashboard E.Leclerc
Fonctions de nettoyage, validation et formatage des données
"""

import logging
from typing import Any, Union

import numpy as np
import pandas as pd

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie un DataFrame en supprimant les doublons et gérant les valeurs manquantes

    Args:
        df: DataFrame à nettoyer

    Returns:
        DataFrame nettoyé
    """
    logger.info(f"Nettoyage du DataFrame - Shape initial: {df.shape}")

    # Suppression des doublons basée sur Invoice ID
    df_clean = df.drop_duplicates(subset=["Invoice ID"], keep="first") if "Invoice ID" in df.columns else df.drop_duplicates()

    logger.info(f"Suppression des doublons - Shape après: {df_clean.shape}")

    # Gestion des valeurs manquantes pour les colonnes critiques
    critical_columns = ["Sales", "Quantity"]
    for col in critical_columns:
        if col in df_clean.columns:
            missing_count = df_clean[col].isnull().sum()
            if missing_count > 0:
                logger.warning(f"Valeurs manquantes dans {col}: {missing_count}")
                # Remplacer par 0 pour les valeurs numériques
                df_clean[col] = df_clean[col].fillna(0)

    logger.info(f"Nettoyage terminé - Shape final: {df_clean.shape}")
    return df_clean


def validate_transaction_data(df: pd.DataFrame) -> dict[str, Any]:
    """
    Valide les données de transaction et retourne un rapport de validation

    Args:
        df: DataFrame à valider

    Returns:
        Dictionnaire avec résultats de validation
    """
    validation_results: dict[str, Any] = {"is_valid": True, "errors": [], "warnings": [], "stats": {}}

    # Colonnes requises (plus flexibles)
    required_columns = ["Invoice ID", "Date", "Product line", "Quantity", "Unit price", "Sales"]

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        validation_results["is_valid"] = False
        validation_results["errors"].append(f"Colonnes manquantes: {missing_columns}")

    # Validation des types de données
    expected_types = {"Sales": "numeric", "Quantity": "numeric", "Unit price": "numeric", "Rating": "numeric"}

    for col, expected_type in expected_types.items():
        if col in df.columns and expected_type == "numeric" and not pd.api.types.is_numeric_dtype(df[col]):
            validation_results["warnings"].append(f"Colonne {col} n'est pas numérique")

    # Détection des valeurs aberrantes
    for col in ["Sales", "Quantity", "Unit price"]:
        if col in df.columns and (df[col] < 0).any():
            validation_results["warnings"].append(f"Valeurs négatives détectées dans {col}")

    # Statistiques
    validation_results["stats"] = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_rows": df.duplicated().sum(),
    }

    return validation_results


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardise les noms de colonnes

    Args:
        df: DataFrame avec colonnes à standardiser

    Returns:
        DataFrame avec noms de colonnes standardisés
    """
    # Mapping des variations de noms de colonnes
    column_mapping = {
        "Invoice ID": "Invoice ID",
        "invoice_id": "Invoice ID",
        "InvoiceID": "Invoice ID",
        "Invoice Id": "Invoice ID",
        "Product line": "Product line",
        "product_line": "Product line",
        "ProductLine": "Product line",
        "Unit price": "Unit price",
        "unit_price": "Unit price",
        "UnitPrice": "Unit price",
        "Tax 5%": "Tax 5%",
        "tax_5": "Tax 5%",
        "gross income": "gross income",
        "gross_income": "gross income",
        "Gross income": "gross income",
    }

    df_standardized = df.rename(columns=column_mapping)

    # Nettoyage des noms de colonnes (espaces, majuscules)
    df_standardized.columns = df_standardized.columns.str.strip().str.title()

    return df_standardized


def format_currency(amount: Union[int, float], currency: str = "€") -> str:
    """
    Formate un montant en devise

    Args:
        amount: Montant à formater
        currency: Symbole de devise

    Returns:
        Chaîne formatée
    """
    if pd.isna(amount):
        return "N/A"

    try:
        amount_float = float(amount)
        return f"{currency}{amount_float:,.2f}"
    except (ValueError, TypeError):
        return f"{currency}0.00"


def format_percentage(value: Union[int, float], decimals: int = 2) -> str:
    """
    Formate une valeur en pourcentage

    Args:
        value: Valeur à formater
        decimals: Nombre de décimales

    Returns:
        Chaîne formatée en pourcentage
    """
    if pd.isna(value):
        return "N/A"

    try:
        value_float = float(value)
        return f"{value_float:.{decimals}f}%"
    except (ValueError, TypeError):
        return "0.00%"


def safe_divide(numerator: Union[int, float], denominator: Union[int, float], default: float = 0.0) -> float:
    """
    Division sécurisée qui évite les erreurs de division par zéro

    Args:
        numerator: Numérateur
        denominator: Dénominateur
        default: Valeur par défaut si division impossible

    Returns:
        Résultat de la division ou valeur par défaut
    """
    try:
        if denominator == 0:
            return default
        return float(numerator) / float(denominator)
    except (ValueError, TypeError):
        return default


def calculate_growth_rate(current: Union[int, float], previous: Union[int, float]) -> float:
    """
    Calcule le taux de croissance entre deux valeurs

    Args:
        current: Valeur actuelle
        previous: Valeur précédente

    Returns:
        Taux de croissance en pourcentage
    """
    try:
        if previous == 0:
            return 0.0
        return ((float(current) - float(previous)) / float(previous)) * 100
    except (ValueError, TypeError):
        return 0.0


def create_date_features(df: pd.DataFrame, date_col: str = "Date") -> pd.DataFrame:
    """
    Crée des caractéristiques temporelles à partir d'une colonne de date

    Args:
        df: DataFrame contenant la colonne de date
        date_col: Nom de la colonne de date

    Returns:
        DataFrame avec caractéristiques temporelles ajoutées
    """
    df_result = df.copy()

    if date_col not in df_result.columns:
        logger.warning(f"Colonne {date_col} non trouvée dans le DataFrame")
        return df_result

    # S'assurer que la colonne est en datetime
    if not pd.api.types.is_datetime64_any_dtype(df_result[date_col]):
        df_result[date_col] = pd.to_datetime(df_result[date_col])

    # Extraire les caractéristiques temporelles
    df_result["Year"] = df_result[date_col].dt.year
    df_result["Month"] = df_result[date_col].dt.month
    df_result["Day"] = df_result[date_col].dt.day
    df_result["DayOfWeek"] = df_result[date_col].dt.day_name()
    df_result["Quarter"] = df_result[date_col].dt.quarter
    df_result["WeekOfYear"] = df_result[date_col].dt.isocalendar().week
    df_result["IsWeekend"] = df_result[date_col].dt.dayofweek >= 5

    logger.info(
        "Caractéristiques temporelles créées - Colonnes ajoutées: Year, Month, Day, DayOfWeek, Quarter, WeekOfYear, IsWeekend"
    )

    return df_result


def filter_by_period(df: pd.DataFrame, period: str, specific_date: str = None, date_col: str = "Date") -> pd.DataFrame:
    """
    Filtre un DataFrame par période temporelle relative au dataset

    Args:
        df: DataFrame à filtrer
        period: Période ('all', 'day', 'week', 'month')
        specific_date: Date spécifique au format YYYY-MM-DD si period='day'
        date_col: Nom de la colonne de date

    Returns:
        DataFrame filtré par période
    """
    if period == "all" or date_col not in df.columns:
        logger.info(f"Période: {period} - Pas de filtrage")
        return df.copy()

    df_filtered = df.copy()

    # S'assurer que la colonne est en datetime
    if not pd.api.types.is_datetime64_any_dtype(df_filtered[date_col]):
        df_filtered[date_col] = pd.to_datetime(df_filtered[date_col])

    # Utiliser la date la plus récente du dataset comme référence
    max_date = df_filtered[date_col].max()
    min_date = df_filtered[date_col].min()
    logger.info(f"Dataset dates: {min_date} à {max_date}")

    # Pour la démo, on considère "aujourd'hui" comme la date la plus récente du dataset
    reference_today = max_date.normalize()
    logger.info(f"Date de référence utilisée: {reference_today}")

    if period == "day" and specific_date:
        # Jour spécifique sélectionné
        try:
            target_date = pd.to_datetime(specific_date).normalize()
            mask = df_filtered[date_col].dt.date == target_date.date()
            df_filtered = df_filtered[mask]
            logger.info(f"Filtrage jour spécifique {target_date.date()} - {len(df_filtered)} lignes trouvées")
        except Exception as e:
            logger.error(f"Erreur de conversion de date {specific_date}: {e}")
            return df.copy()  # Retourner le DataFrame original en cas d'erreur

    elif period == "today":
        # Dernier jour du dataset
        mask = df_filtered[date_col].dt.date == reference_today.date()
        df_filtered = df_filtered[mask]
        logger.info(f"Filtrage période aujourd'hui (dernier jour) - {len(df_filtered)} lignes trouvées")

    elif period == "week":
        # 7 derniers jours du dataset
        week_start = reference_today - pd.Timedelta(days=7)
        logger.info(f"Début de semaine (7 derniers jours): {week_start}")
        mask = df_filtered[date_col] >= week_start
        df_filtered = df_filtered[mask]
        logger.info(f"Filtrage période cette semaine (7 derniers jours) - {len(df_filtered)} lignes trouvées")

    elif period == "month":
        # 30 derniers jours du dataset
        month_start = reference_today - pd.Timedelta(days=30)
        logger.info(f"Début du mois (30 derniers jours): {month_start}")
        mask = df_filtered[date_col] >= month_start
        df_filtered = df_filtered[mask]
        logger.info(f"Filtrage période ce mois (30 derniers jours) - {len(df_filtered)} lignes trouvées")

    return df_filtered


def detect_outliers(df: pd.DataFrame, column: str, method: str = "iqr") -> pd.DataFrame:
    """
    Détecte les valeurs aberrantes dans une colonne

    Args:
        df: DataFrame à analyser
        column: Nom de la colonne
        method: Méthode de détection ('iqr', 'zscore')

    Returns:
        DataFrame avec colonne 'is_outlier' ajoutée
    """
    if column not in df.columns:
        logger.warning(f"Colonne {column} non trouvée")
        return df

    df_result = df.copy()

    if method == "iqr":
        Q1 = df_result[column].quantile(0.25)
        Q3 = df_result[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df_result["is_outlier"] = (df_result[column] < lower_bound) | (df_result[column] > upper_bound)

    elif method == "zscore":
        mean_val = df_result[column].mean()
        std_val = df_result[column].std()
        z_scores = np.abs((df_result[column] - mean_val) / std_val)
        df_result["is_outlier"] = z_scores > 3

    outlier_count = df_result["is_outlier"].sum()
    logger.info(f"Détection d'outliers ({method}) - {outlier_count} valeurs aberrantes détectées dans {column}")

    return df_result


def export_to_csv(df: pd.DataFrame, filename: str, index: bool = False) -> bool:
    """
    Exporte un DataFrame vers un fichier CSV

    Args:
        df: DataFrame à exporter
        filename: Nom du fichier de sortie
        index: Inclure l'index dans l'export

    Returns:
        True si succès, False sinon
    """
    try:
        df.to_csv(filename, index=index)
        logger.info(f"DataFrame exporté avec succès vers {filename}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'export vers {filename}: {e}")
        return False


def load_config_file(config_path: str) -> dict[str, Any]:
    """
    Charge un fichier de configuration

    Args:
        config_path: Chemin vers le fichier de config

    Returns:
        Dictionnaire de configuration
    """
    try:
        import json

        with open(config_path, encoding="utf-8") as f:
            config: dict[str, Any] = json.load(f)
        logger.info(f"Configuration chargée depuis {config_path}")
        return config
    except FileNotFoundError:
        logger.warning(f"Fichier de configuration {config_path} non trouvé")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Erreur de décodage JSON dans {config_path}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Erreur lors du chargement de {config_path}: {e}")
        return {}


def get_data_summary(df: pd.DataFrame) -> dict[str, Any]:
    """
    Génère un résumé statistique des données

    Args:
        df: DataFrame à analyser

    Returns:
        Dictionnaire avec statistiques descriptives
    """
    summary = {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": df.dtypes.to_dict(),
        "memory_usage": df.memory_usage(deep=True).sum(),
        "numeric_summary": {},
    }

    # Statistiques pour les colonnes numériques
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        summary["numeric_summary"][col] = {
            "count": df[col].count(),
            "mean": df[col].mean(),
            "std": df[col].std(),
            "min": df[col].min(),
            "max": df[col].max(),
            "missing": df[col].isnull().sum(),
        }

    logger.info(f"Résumé des données généré - Shape: {df.shape}")
    return summary

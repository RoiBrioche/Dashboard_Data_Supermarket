"""
Tests pour le module __init__.py
"""

import os
import sys

# Ajouter le chemin src pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

def test_version():
    """Test que la version est définie"""
    from src import __version__
    assert __version__ == "0.1.0"
    assert isinstance(__version__, str)

def test_author():
    """Test que l'auteur est défini"""
    from src import __author__
    assert __author__ == "RoiBrioche"
    assert isinstance(__author__, str)

def test_module_import():
    """Test que le module peut être importé"""
    import src

    assert hasattr(src, '__version__')
    assert hasattr(src, '__author__')
    assert hasattr(src, '__doc__')

    # Vérifier que le docstring n'est pas vide
    assert src.__doc__ is not None
    assert len(src.__doc__.strip()) > 0

# 🚀 Ruff - Outil de Qualité de Code

## Qu'est-ce que Ruff ?

**Ruff** est un linter et formateur Python ultra-rapide écrit en Rust. Il combine les fonctionnalités de plusieurs outils en un seul.

## 🎯 Pourquoi Ruff dans ce projet ?

### ⚡ Performance extrême
- **10-100x plus rapide** que les outils Python traditionnels
- Analyse complète du projet en millisecondes

### 🛠️ Tout-en-un
Remplace efficacement :
- `flake8` (linting)
- `black` (formatage)
- `isort` (tri des imports)

### 🔧 Utilisation courante

```bash
# Vérifier les problèmes de code
ruff check .

# Corriger automatiquement les problèmes
ruff check --fix .

# Formater tout le code
ruff format .

# Vérifier que le code est bien formaté
ruff format --check .
```

## ⚙️ Configuration

La configuration se trouve dans `pyproject.toml` :
- Ligne de 127 caractères
- Compatible Python 3.8-3.11
- Règles de qualité de code activées (E, W, F, I, UP, B, C4, SIM)
- Formatage avec guillemets doubles et indentation espaces

## 🔄 Dans le CI/CD

Ruff s'exécute dans le pipeline GitHub Actions pour garantir :
- Code propre et cohérent
- Performance des tests
- Qualité avant chaque merge

## 📦 Version

- Version utilisée : `ruff>=0.1.0`
- Pre-commit hook : v0.1.0 (fixé pour stabilité)

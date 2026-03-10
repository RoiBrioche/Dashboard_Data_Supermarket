# 🛒 Dashboard E.Leclerc Analytics

[![CI](https://github.com/RoiBrioche/Dashboard_Data_Supermarket/workflows/CI/badge.svg)](https://github.com/RoiBrioche/Dashboard_Data_Supermarket/actions)
[![codecov](https://codecov.io/gh/RoiBrioche/Dashboard_Data_Supermarket/branch/main/graph/badge.svg)](https://codecov.io/gh/RoiBrioche/Dashboard_Data_Supermarket)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Dashboard interactif d'analyse des performances commerciales E.Leclerc**
>
> Application web moderne de visualisation de données conçue pour analyser les ventes, les tendances et les KPIs d'un supermarché E.Leclerc.

## 🎯 Objectifs du Projet

Ce dashboard a été développé pour répondre à plusieurs besoins business :

- **📊 Analyse en temps réel** : Visualisation des données de ventes avec des filtres dynamiques
- **🎯 Prise de décision** : KPIs clés pour optimiser les performances commerciales
- **📈 Tendances** : Identification des patterns de vente par période, catégorie et mode de paiement
- **🏪 Performance par ville** : Analyse comparative entre les différents emplacements
- **💼 Portfolio** : Démonstration technique pour recruteurs et collaborateurs

## 🚀 Démo en Ligne

👉 **[Dashboard E.Leclerc - Démo Live](https://dashboard-leclerc.onrender.com)**
*(Déployé sur Render, temps de démarrage ~30s pour le plan gratuit)*

## ✨ Fonctionnalités Principales

### 📋 **Tableau de Bord Complet**
- KPIs en temps réel (CA, marge, transactions, panier moyen, satisfaction)
- Graphiques interactifs avec Plotly
- Design responsive et moderne

### 🔍 **Filtres Avancés**
- **Période temporelle** : Aujourd'hui, cette semaine, ce mois, tout
- **Catégories de produits** : Filtrage par ligne de produits
- **Modes de paiement** : Carte, espèces, portefeuille électronique
- **Villes** : Analyse multi-magasins avec sélection multiple

### 📊 **Visualisations**
- **Évolution des ventes** : Graphique temporel avec agrégation flexible
- **Répartition des paiements** : Diagramme circulaire interactif
- **Ventes par catégorie** : Bar chart avec valeurs détaillées
- **Activité horaire** : Analyse des pics d'activité
- **Top catégories** : Tableau des meilleures performances
- **Analyse par ville** : Comparaison des magasins

### 🎨 **Design & UX**
- **Charte graphique E.Leclerc** : Bleu corporate et orange dynamique
- **Interface moderne** : Dash Bootstrap Components
- **Responsive** : Compatible desktop et mobile
- **Animations fluides** : Transitions et interactions soignées

## 🛠️ Stack Technique

### **Backend**
- **Python 3.11** : Langage principal
- **Dash 2.0+** : Framework web analytique
- **Pandas** : Manipulation et analyse de données
- **Plotly** : Visualisations interactives

### **Frontend**
- **Dash Bootstrap Components** : Composants UI modernes
- **HTML/CSS** : Structure et style personnalisé
- **Google Fonts** : Typographie DM Sans

### **Déploiement**
- **Render** : Hébergement cloud (production)
- **GitHub Actions** : CI/CD automatisé
- **Poetry** : Gestion des dépendances

## 📁 Structure du Projet

```
Dashboard_Data_Supermarket/
├── 📄 src/
│   ├── app/
│   │   ├── dashboard.py      # Application principale Dash
│   │   ├── analysis.py       # Fonctions d'analyse de données
│   │   └── utils.py          # Utilitaires de traitement
│   └── assets/
│       ├── colors.py         # Charte graphique E.Leclerc
│       ├── *.css             # Styles personnalisés
│       └── *.png             # Logo et images
├── 📊 data/
│   └── supermarket_analysis.csv  # Dataset des ventes
├── 🧪 tests/                 # Tests unitaires complets
├── ⚙️ .github/workflows/     # CI/CD GitHub Actions
└── 📋 requirements.txt       # Dépendances Python
```

## 🚀 Installation & Démarrage Local

### **Prérequis**
- Python 3.11+
- Git

### **Installation**
```bash
# Cloner le repository
git clone https://github.com/RoiBrioche/Dashboard_Data_Supermarket.git
cd Dashboard_Data_Supermarket

# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### **Démarrage**
```bash
# Lancer le dashboard
python src/app/dashboard.py

# Accéder à l'application
# http://localhost:8050
```

## 📊 Dataset & Données

Le dashboard utilise un dataset CSV de ventes supermarché contenant :

- **Transactions** : ~1000 enregistrements de ventes
- **Colonnes** : Date, Ville, Catégorie, Prix, Quantité, Mode de paiement, Satisfaction client
- **Période** : Plusieurs mois d'activité
- **Localisations** : 3 villes (Yangon, Naypyitaw, Mandalay)

### **Format des données**
```csv
Date,Invoice ID,City,Customer type,Gender,Product line,Unit price,Quantity,Payment,Rating,gross margin percentage,gross income,Total
1/5/2019,750-67-8428,Yangon,Member,Female,Health and beauty,74.69,7,Ewallet,9.1,4.761904762,524.83,523.83
...
```

## 🧪 Tests & Qualité

### **Tests Unitaires**
```bash
# Exécuter tous les tests
pytest

# Avec couverture de code
pytest --cov=src --cov-report=html
```

### **Qualité Code**
- **Ruff** : Linting et formatage automatique
- **MyPy** : Vérification des types
- **Pre-commit** : Hooks de qualité
- **GitHub Actions** : CI automatisé

### **Couverture**
- Tests unitaires : 95%+ de couverture
- Tests d'intégration : Dashboard complet
- Tests edge cases : Gestion des erreurs

## 🔧 Configuration & Personnalisation

### **Ajouter de nouvelles données**
1. Placer le fichier CSV dans `data/`
2. Mettre à jour le chemin dans `src/app/dashboard.py`
3. Adapter les colonnes dans `src/app/analysis.py`

### **Personnaliser les couleurs**
```python
# src/assets/colors.py
LECLERC_BLUE = "#0471b6"
LECLERC_ORANGE = "#ff6b35"
```

### **Ajouter des graphiques**
1. Créer la fonction d'analyse dans `src/app/analysis.py`
2. Ajouter le callback dans `src/app/dashboard.py`
3. Intégrer dans le layout

## 🚀 Déploiement

### **Render (Production)**
```bash
# Configuration automatique via GitHub
# Build: pip install -r requirements.txt
# Start: python src/app/dashboard.py
```

### **Variables d'environnement**
- `PORT` : Port d'écoute (automatique sur Render)
- `ENVIRONMENT` : Mode production/development

## 🤝 Contributeurs

- **[RoiBrioche](https://github.com/RoiBrioche)** - Développeur principal

## 📄 Licence

Ce projet est sous licence **MIT** - voir le fichier [LICENSE](LICENSE) pour les détails.

## 🙏 Remerciements

- **E.Leclerc** : Pour l'inspiration de la charte graphique
- **Plotly Team** : Pour l'excellente librairie de visualisation
- **Dash Community** : Pour les composants et documentation

---

## 📞 Contact

**Pour toute question ou collaboration :**
- 📧 [GitHub Issues](https://github.com/RoiBrioche/Dashboard_Data_Supermarket/issues)
- 🔗 [LinkedIn](https://linkedin.com/in/votre-profil) *(à personnaliser)*
- 🌐 [Portfolio](https://votre-site.com) *(à personnaliser)*

---

> **💡 Note** : Ce dashboard est un projet de démonstration conçu pour présenter mes compétences en développement Python, analyse de données et création d'applications web interactives.

**Made with ❤️ using Python, Dash & Plotly**

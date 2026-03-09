# Assets Graphiques

Ce dossier contient tous les éléments visuels pour le dashboard E.Leclerc.

## 📁 Contenu

- `E.Leclerc_logo.png` : Logo officiel E.Leclerc pour l'entête du dashboard
- `style.css` : Feuille de style complète avec charte graphique E.Leclerc
- `colors.py` : Module Python avec les couleurs et configurations graphiques
- `readme_assets.md` : Documentation des assets (ce fichier)

## 🎨 Charte graphique E.Leclerc

### Couleurs principales
- **Orange E.Leclerc** : `#ee8c11`
- **Bleu E.Leclerc** : `#0471b6` 
- **Blanc E.Leclerc** : `#ffffff`

### Couleurs secondaires
- **Gris clair** : `#f5f5f5`
- **Gris moyen** : `#e0e0e0`
- **Gris foncé** : `#333333`

### Configuration
- **Layout** : Streamlit en mode "wide"
- **Typographie** : Arial, sans-serif
- **Animations** : Transitions douces et hover effects

## 🚀 Utilisation

### Dans Streamlit
```python
from src.assets.colors import LECLERC_ORANGE, LECLERC_BLUE, STREAMLIT_THEME
st.set_page_config(layout="wide", initial_sidebar_state="expanded")
```

### Dans Plotly
```python
from src.assets.colors import COLOR_PATTERNS, PLOTLY_LAYOUT_CONFIG
fig.update_layout(template="plotly_white", colorway=COLOR_PATTERNS["primary"])
```

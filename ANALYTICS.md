# Système d'Analytics Swiftly

## Vue d'ensemble

Le système d'analytics de Swiftly permet de suivre et d'analyser les visiteurs de chaque site déployé. Les données sont collectées automatiquement, cryptées et stockées dans une base de données JSON par site.

## Fonctionnalités

### 1. Tracking automatique des visiteurs

Lorsqu'un visiteur accède à un site, les informations suivantes sont collectées :

- **IP** : Adresse IP du visiteur
- **Pays** : Géolocalisation approximative (basique, à améliorer en production)
- **Système d'exploitation** : Windows, macOS, Linux, Android, iOS
- **Navigateur** : Chrome, Firefox, Safari, Edge, Opera
- **User Agent** : Chaîne complète pour analyse détaillée
- **Referrer** : Site d'origine du visiteur
- **Horodatage** : Date et heure précise de la visite
- **Langue** : Langue préférée du navigateur

### 2. Sécurité et cryptage

- Toutes les données sensibles sont **cryptées avec Fernet** (cryptographie symétrique)
- La clé de cryptage est stockée dans `swiftly/config.py`
- **IMPORTANT** : En production, stocker la clé dans une variable d'environnement

### 3. Dashboard par site

Chaque site dispose de son propre dashboard accessible via `/dashboard/site/<nom_du_site>` avec :

- **KPIs** : Visites totales, visiteurs uniques, nombre de pays
- **Graphiques circulaires** : Répartition navigateurs et OS
- **Répartition géographique** : Liste des pays avec compteurs
- **Sources de trafic** : Referrers avec barres de progression
- **Graphique temporel** : Visites quotidiennes (ligne)

### 4. Stockage des données

Les analytics sont stockées dans un fichier `.analytics.json` dans le dossier de chaque site :

```
sites/
  mon-site/
    index.html
    .analytics.json  ← Base de données analytics
```

Structure du fichier `.analytics.json` :

```json
{
  "visits": [
    {
      "id": 1,
      "data": "encrypted_data_here",
      "timestamp": "2026-01-14T10:30:00"
    }
  ],
  "created_at": "2026-01-14T10:00:00"
}
```

## Installation

### Dépendances

Installer la bibliothèque de cryptage :

```bash
pip install cryptography==41.0.7
```

Ou installer toutes les dépendances :

```bash
pip install -r requirements.txt
```

### Configuration

1. **Générer une nouvelle clé de cryptage** (recommandé en production) :

```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())
```

2. **Mettre à jour la clé** dans `swiftly/config.py` :

```python
ANALYTICS_ENCRYPTION_KEY = b'votre_nouvelle_cle_generee'
```

3. **En production**, utiliser une variable d'environnement :

```python
import os
ANALYTICS_ENCRYPTION_KEY = os.environ.get('ANALYTICS_KEY', b'default_key').encode()
```

## Utilisation

### Accéder au dashboard d'un site

1. Connectez-vous au dashboard principal : `/dashboard`
2. Cliquez sur "Analytics" sous le nom du site
3. Ou accédez directement : `/dashboard/site/<nom_du_site>`

### Initialisation automatique

La base de données analytics est automatiquement créée lors du déploiement d'un nouveau site.

### Tracking des visites

Le tracking se fait automatiquement lors de l'accès à `index.html` d'un site. Aucune action requise.

## Architecture

### Fichiers principaux

- **`swiftly/analytics.py`** : Module de tracking et stats
  - `track_visit()` : Enregistre une visite
  - `get_analytics()` : Récupère les données (décryptées)
  - `get_analytics_stats()` : Calcule les statistiques
  
- **`swiftly/routes/main.py`** : Route de service des sites
  - Appelle `track_visit()` lors de l'accès à index.html
  
- **`swiftly/routes/dashboard.py`** : Routes du dashboard
  - `/dashboard/site/<site>` : Affiche le dashboard analytics
  
- **`templates/dashboard_site.html`** : Template du dashboard
  - Utilise Chart.js pour les visualisations

### Flux de données

1. Visiteur accède à `/sites/<site>/`
2. `serve_site()` appelle `track_visit(site_name)`
3. `track_visit()` collecte les données via `get_visitor_data()`
4. Données cryptées avec `encrypt_data()`
5. Enregistrement dans `.analytics.json`
6. Dashboard lit avec `get_analytics()` (décryptage auto)
7. Stats calculées avec `get_analytics_stats()`

## Améliorations possibles

### Court terme

- [ ] Ajouter rate limiting sur le tracking (éviter spam)
- [ ] Géolocalisation avancée avec service externe (ipapi.co, MaxMind GeoIP2)
- [ ] Filtrage par période (7j, 30j, 90j, custom)
- [ ] Export des données (CSV, JSON)

### Moyen terme

- [ ] Tracking des pages internes (pas seulement index.html)
- [ ] Temps de visite / durée de session
- [ ] Événements personnalisés (clics, conversions)
- [ ] A/B testing

### Long terme

- [ ] Système de notifications (alertes de trafic)
- [ ] Comparaison de périodes
- [ ] Heatmaps
- [ ] Migration vers base de données SQL (PostgreSQL, MySQL)

## Sécurité

### Points d'attention

- **Clé de cryptage** : Ne jamais commiter la clé en production
- **RGPD** : Vérifier la conformité selon votre juridiction
- **Anonymisation** : Option de hacher les IPs pour anonymiser
- **Rétention** : Définir une politique de suppression des anciennes données

### Recommandations production

1. Utiliser HTTPS obligatoire
2. Stocker la clé dans un gestionnaire de secrets (AWS Secrets Manager, HashiCorp Vault)
3. Implémenter un système de rotation de clés
4. Ajouter un consentement cookies/tracking
5. Logger les accès aux analytics (audit trail)

## API Module Analytics

### Fonctions principales

```python
# Initialiser la DB pour un site
init_analytics_db(site_name: str) -> bool

# Enregistrer une visite
track_visit(site_name: str) -> bool

# Récupérer les analytics brutes
get_analytics(site_name: str, decrypt: bool = True) -> dict

# Calculer les statistiques
get_analytics_stats(site_name: str) -> dict

# Utilitaires de cryptage
encrypt_data(data: dict) -> str
decrypt_data(encrypted_hex: str) -> dict
```

### Exemple d'utilisation

```python
from swiftly.analytics import get_analytics_stats

# Obtenir les stats d'un site
stats = get_analytics_stats('mon-site')

print(f"Visites totales: {stats['total_visits']}")
print(f"Visiteurs uniques: {stats['unique_ips']}")
print(f"Navigateurs: {stats['browsers']}")
```

## Support

Pour toute question ou amélioration, contactez l'équipe Swiftly.

# 🚀 Swiftly

<div align="center">

**L'Alternative Open Source à Netlify**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-black.svg)](https://flask.palletsprojects.com/)

*Déployez vos sites statiques instantanément avec une API simple et un CLI*

Créé à l'origine pour [Flavortown Hack Club](https://flavortown.hackclub.com/) 🍔

[Fonctionnalités](#fonctionnalités) • [Démarrage Rapide](#-démarrage-rapide) • [Documentation API](#-documentation-api) • [Utilisation CLI](#-utilisation-cli)

**[🇬🇧 English Version](README.md)**

</div>

---

## 📖 À Propos

**Swiftly** est une plateforme légère et open-source pour déployer et héberger des sites HTML statiques. Construit avec Flask, il fournit une API REST simple et un outil CLI pour gérer vos déploiements.

Ce projet a été créé à l'origine pour la communauté [Flavortown Hack Club](https://flavortown.hackclub.com/) afin de fournir un moyen simple de déployer et partager des sites statiques.

Parfait pour :
- 🎨 Portfolios personnels
- 📝 Blogs statiques
- 🌐 Pages d'atterrissage
- 🧪 Démos de prototypes
- 🏫 Projets étudiants

## ✨ Fonctionnalités

- **🚀 API Simple** - Uploadez et déployez des fichiers HTML via l'API REST
- **💻 Outil CLI** - Interface en ligne de commande pour un déploiement facile
- **📦 Upload de Fichiers** - Support de l'upload direct de fichiers HTML
- **📦 Upload de Fichiers et Dossiers** - Support de l'upload direct de fichiers HTML et upload de dossiers complets (préserve l'arborescence)
- **📊 Interface Dashboard** - Gestion via une interface web (connexion, déploiement, suppression)
- **📊 Système d'Analytics** - Collecte chiffrée des visites par site avec dashboard intégré
- **🗂️ Gestion de Sites** - Listez, ajoutez et supprimez des sites facilement
- **🔒 Sécurisé** - Validation et sécurisation des noms de fichiers
- **📊 Base de Données JSON** - Stockage simple basé sur des fichiers
- **🆓 100% Open Source** - Licence MIT

## 🏁 Démarrage Rapide

### Prérequis

- Python 3.8+

### 🚀 Méthode la Plus Facile (Recommandée)

#### Sur Linux/macOS
```bash
./swiftly.sh
```

#### Sur Windows
Double-clique sur `swiftly.bat` ou lance-le dans l'invite de commande:
```cmd
swiftly.bat
```

C'est tout! Les scripts vont automatiquement:
- ✅ Vérifier l'installation de Python
- 📦 Installer `requests` si nécessaire
- 🚀 Lancer le CLI

### Installation Manuelle (Pour Configuration Serveur)

1. **Cloner le dépôt**
```bash
git clone https://github.com/ruikdev/Swiftly.git
cd Swiftly
```

2. **Créer un environnement virtuel**
```bash
python3 -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Lancer le serveur**
```bash
python app.py
```

Le serveur démarrera sur `http://localhost:5000` 🎉

## 🖥️ Dashboard Web

Swiftly inclut désormais une interface web pour gérer vos sites sans passer par le CLI.

- **URL**: `http://localhost:5000/dashboard`
- **Fonctionnalités**:
  - Connexion / Inscription via le navigateur
  - Liste de vos sites (aperçu, nombre de fichiers)
  - Déploiement via formulaire (upload de dossier complet ou fichiers individuels)
  - Suppression de site

Le dashboard conserve la même charte visuelle que la page d'accueil (Tailwind). Pour l'utiliser, démarrez le serveur (`python app.py`) puis rendez-vous sur l'URL ci-dessus. Le formulaire de déploiement gère maintenant le drag & drop de dossiers et vérifie la présence d'un `index.html`.

## 🔌 Documentation API

### URL de Base
```
http://localhost:5000
```

### Points de Terminaison

#### **GET** `/health`
Vérifier si l'API fonctionne.

**Réponse :**
```json
{
  "status": "ok"
}
```

---

#### **GET** `/api/sites`
Lister tous les sites déployés.

**Réponse :**
```json
{
  "sites": {
    "mon-site": "mon-site.html",
    "blog": "blog.html"
  }
}
```

---

#### **POST** `/api/sites`
Uploader et déployer un nouveau site.

**Content-Type:** `multipart/form-data`

**Paramètres :**
- `name` (string, requis) : Le nom/identifiant du site
- `file` (file, requis) : Fichier HTML à uploader

**Exemple avec curl :**
```bash
curl -X POST http://localhost:5000/api/sites \
  -F "name=mon-super-site" \
  -F "file=@index.html"
```

**Réponse de Succès (201) :**
```json
{
  "message": "Site 'mon-super-site' ajouté avec succès",
  "site": {
    "mon-super-site": "mon-super-site.html"
  },
  "url": "/sites/mon-super-site"
}
```

**Réponses d'Erreur :**
- `400` - Champs requis manquants ou fichier invalide
- `404` - Aucun fichier dans la requête
- `409` - Le nom du site existe déjà

---

#### **DELETE** `/api/sites/<site_name>`
Supprimer un site déployé.

**Exemple :**
```bash
curl -X DELETE http://localhost:5000/api/sites/mon-site
```

**Réponse de Succès (200) :**
```json
{
  "message": "Site 'mon-site' supprimé avec succès"
}
```

---

#### **GET** `/sites/<site_name>`
Accéder à un site déployé.

**Exemple :**
```
http://localhost:5000/sites/mon-super-site
```

## 📊 Analytics

Swiftly intègre un système d'analytics léger qui collecte et chiffre les visites par site. Voici les routes et fonctions principales (voir `swiftly/analytics.py` et `templates/dashboard_site.html`).

- Routes :
  - `GET /dashboard/site/<site_name>` — dashboard analytics d'un site.
  - L'accès à `index.html` d'un site (via `/sites/<site_name>/`) déclenche `track_visit()` pour enregistrer la visite.

- Module `swiftly.analytics` (fonctions principales) :
  - `init_analytics_db(site_name: str) -> bool` — crée le `.analytics.json` pour un site.
  - `track_visit(site_name: str) -> bool` — enregistre une visite (appelé lors du service de la page).
  - `get_analytics(site_name: str, decrypt: bool = True) -> dict` — récupère les analytics brutes.
  - `get_analytics_stats(site_name: str) -> dict` — calcule KPIs et statistiques pour le dashboard.
  - `encrypt_data(data: dict) -> str` / `decrypt_data(encrypted_hex: str) -> dict` — utilitaires de chiffrement Fernet.

- Stockage : les analytics sont stockées par site dans `sites/<site>/.analytics.json`.

- Sécurité : les champs sensibles sont chiffrés avec Fernet. Configurer `ANALYTICS_ENCRYPTION_KEY` dans `swiftly/config.py` ou via une variable d'environnement en production.

## 🌐 Sous-domaines génériques

Swiftly prend désormais en charge les sous-domaines génériques ! Cela signifie que vous pouvez déployer vos sites sur des sous-domaines comme `exemple.swiftly.ruikdev.me` sans effort. Configurez simplement vos paramètres DNS et laissez Swiftly s'occuper du reste.

### Avantages clés :
- Certificats SSL automatiques pour les sous-domaines génériques.
- Routage transparent pour les fichiers statiques et les ressources.
- Configuration facile avec Cloudflare DNS.

Consultez la [Documentation API](#-documentation-api) pour des instructions détaillées.

## 💻 Utilisation CLI

Swiftly est livré avec un outil CLI interactif et puissant pour gérer vos déploiements. Le CLI peut être utilisé indépendamment du serveur !

### Installation Rapide (CLI Uniquement)

Si vous voulez utiliser uniquement le CLI (sans lancer le serveur) :

1. **Télécharger le fichier CLI :**
```bash
curl -O https://raw.githubusercontent.com/ruikdev/Swiftly/main/swiftly_cli.py
```

Ou copiez `swiftly_cli.py` depuis le dépôt.

2. **Installer la seule dépendance requise :**
```bash
pip install requests
```

3. **Lancer le CLI :**
```bash
python3 swiftly_cli.py
```

### Installation Complète (Avec Serveur)

Si vous voulez lancer à la fois le serveur et le CLI :

```bash
git clone https://github.com/ruikdev/Swiftly.git
cd Swiftly
pip install -r requirements.txt
```

### Lancer le CLI

Démarrez le CLI interactif :

```bash
python3 swiftly_cli.py
```

Au premier lancement, vous serez invité à sélectionner votre langue :
- 🇫🇷 Français
- 🇬🇧 English

### Fonctionnalités

Le CLI offre un menu interactif avec les options suivantes :

**Gestion du Compte :**
- Créer un nouveau compte (email + mot de passe)
- Se connecter
- Voir votre profil
- Modifier votre email
- Modifier votre mot de passe
- Se déconnecter

**Gestion des Sites :**
- Lister tous vos sites déployés
- Déployer un nouveau site (télécharger un fichier HTML)
- Supprimer un site

**Autre :**
- Vérifier la santé de l'API
- Changer de langue à tout moment (option 9)

### Flux d'Utilisation Exemple

```
1. Démarrer le CLI : python3 swiftly_cli.py
2. Sélectionner votre langue (Français ou Anglais)
3. Créer un compte ou se connecter
4. Déployer vos fichiers HTML
5. Lister vos sites
6. Partager vos URLs de site !
```

### Stockage des Identifiants

Vos identifiants sont stockés de manière sécurisée localement dans `~/.swiftly_config.json` avec des permissions restreintes (600). Vous n'aurez pas besoin de vous reconnecter sur la même machine.

### Headers d'Authentification

Toutes les requêtes API effectuées par le CLI incluent automatiquement vos identifiants dans ces headers :
- `X-User-Email`: Votre email
- `X-User-Password`: Votre mot de passe

---

## 💻 Utilisation CLI

Swiftly est livré avec un puissant outil CLI pour tester et gérer vos déploiements.

### Installation
```bash
pip install requests
```

### Commandes

**Vérifier la santé de l'API :**
```bash
python cli_api_test.py health
```

**Lister tous les sites :**
```bash
python cli_api_test.py list
```

**Déployer un nouveau site :**
```bash
python cli_api_test.py add mon-blog index.html
```

**Supprimer un site :**
```bash
python cli_api_test.py delete mon-blog
```

**Afficher l'aide :**
```bash
python cli_api_test.py help
```

## 📁 Structure du Projet

```
Swiftly/
├── ANALYTICS.md
├── app.py
├── LICENSE
├── README.fr.md
├── README.md
├── requirements.txt
├── swiftly_cli.py
├── swiftly.bat
├── swiftly.sh
├── db/
│   └── sites.json
├── sites/
├── static/
│   └── images/
├── swiftly/
│   ├── __init__.py
│   ├── analytics.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── site.py
│   │   └── user.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── main.py
│   │   ├── sites.py
│   │   └── user.py
│   └── utils/
│       ├── __init__.py
│       └── decorators.py
└── templates/
  ├── base.html
  ├── dashboard_layout.html
  ├── dashboard_home.html
  ├── dashboard_site.html
  ├── dashboard_deploy.html
  ├── dashboard_profile.html
  ├── auth_login.html
  └── auth_register.html
```

## 🛠️ Configuration

L'application utilise les valeurs par défaut suivantes :

- **Hôte :** `0.0.0.0`
- **Port :** `5000`
- **Base de données :** `db/sites.json`
- **Dossier des sites :** `sites/`

Vous pouvez modifier ces valeurs dans [app.py](app.py).

## 🔐 Fonctionnalités de Sécurité

- ✅ Sécurisation des noms de fichiers avec `secure_filename()`
- ✅ Validation des fichiers HTML
- ✅ Prévention des noms en double
- ✅ Protection contre la traversée de chemin

## 🗺️ Feuille de Route

### À Venir
- [ ] Support des domaines personnalisés
- [ ] Automatisation des certificats SSL/TLS
- [ ] Déploiement multi-fichiers (répertoires entiers)
- [ ] Intégration Git pour déploiements automatiques
- [ ] Support des variables d'environnement
- [ ] Analytiques de site
- [ ] Intégration CDN
- [ ] Support des webhooks pour CI/CD
- [ ] Ajout d'un système de page dashboard par site (système de login site, et autre)

## 🤝 Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à :

1. Forker le dépôt
2. Créer une branche de fonctionnalité (`git checkout -b feature/fonctionnalite-incroyable`)
3. Commiter vos changements (`git commit -m 'Ajout fonctionnalité incroyable'`)
4. Pousser vers la branche (`git push origin feature/fonctionnalite-incroyable`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- Construit avec [Flask](https://flask.palletsprojects.com/)
- Inspiré par [Netlify](https://www.netlify.com/)
- Stylisé avec [Tailwind CSS](https://tailwindcss.com/)
- Créé pour la communauté [Flavortown Hack Club](https://flavortown.hackclub.com/)

---

<div align="center">

Fait avec ❤️ par [ruikdev](https://github.com/ruikdev)

⭐ Mettez une étoile si vous trouvez ce projet utile !

</div>

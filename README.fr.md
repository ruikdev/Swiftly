# 🚀 Swiftly

<div align="center">

**L'Alternative Open Source à Netlify**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-black.svg)](https://flask.palletsprojects.com/)

*Déployez vos sites statiques instantanément avec une API simple et un CLI*

Créé à l'origine pour [Flavortown Hack Club](https://flavortown.hackclub.com/) 🍔

[Fonctionnalités](#fonctionnalités) • [Démarrage Rapide](#démarrage-rapide) • [Documentation API](#documentation-api) • [Utilisation CLI](#utilisation-cli)

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
- **🗂️ Gestion de Sites** - Listez, ajoutez et supprimez des sites facilement
- **🔒 Sécurisé** - Validation et sécurisation des noms de fichiers
- **📊 Base de Données JSON** - Stockage simple basé sur des fichiers
- **🆓 100% Open Source** - Licence MIT

## 🏁 Démarrage Rapide

### Prérequis

- Python 3.8+
- pip

### Installation

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
├── app.py                 # Application Flask principale
├── cli_api_test.py        # Outil CLI pour tester
├── requirements.txt       # Dépendances Python
├── db/
│   └── sites.json        # Base de données des sites
├── sites/                # Fichiers HTML déployés
├── templates/
│   └── base.html         # Page d'accueil
└── README.md
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
- [ ] Interface Dashboard pour la gestion des sites
- [ ] Support des variables d'environnement
- [ ] Analytiques de site
- [ ] Intégration CDN
- [ ] Support des webhooks pour CI/CD
- [ ] Système d'authentification utilisateur
- [ ] Fonctionnalités de sécurité améliorées

### En Cours
- [x] Déploiement basique de fichiers HTML
- [x] API REST
- [x] Outil CLI
- [x] Upload de fichiers via API

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

# 🚀 Swiftly v0.9.0 — Première Release Stable

**Date de sortie :** 16 janvier 2026  
**Type de release :** Stable  

---

## 📖 À propos de cette release

Nous sommes ravis d'annoncer la **première version stable de Swiftly** ! 🎉

**Swiftly** est une alternative open source à Netlify, conçue pour déployer et héberger facilement des sites statiques HTML. Développé initialement pour la communauté [Flavortown Hack Club](https://flavortown.hackclub.com/), Swiftly offre une plateforme légère et complète avec API REST, CLI interactif et interface web.

Cette version v0.9.0 représente un projet mature et prêt pour la production, incluant toutes les fonctionnalités essentielles pour gérer vos déploiements de sites statiques en toute simplicité.

---

## ✨ Fonctionnalités principales

### 🌐 **Gestion de sites statiques**
- **API REST complète** pour le déploiement et la gestion de sites via HTTP
- **Upload de fichiers individuels** ou **dossiers complets** avec préservation de la structure
- **Correction automatique des chemins** : transformation des chemins absolus en chemins relatifs dans les fichiers HTML, CSS et JS
- **Hébergement instantané** : accès aux sites déployés via `/sites/<nom-du-site>`
- **Support des sous-domaines wildcard** avec configuration DNS Cloudflare et SSL automatique

### 💻 **CLI Interactif multilingue**
- Interface en ligne de commande moderne et conviviale
- **Support bilingue** : Français et Anglais
- **Scripts d'installation simplifiés** : `swiftly.sh` (Linux/macOS) et `swiftly.bat` (Windows)
- Gestion complète :
  - Création de compte et authentification
  - Déploiement de sites (fichiers ou dossiers)
  - Liste des sites déployés
  - Suppression de sites
  - Gestion du profil (email, mot de passe)
  - Vérification de l'état de l'API
- **Stockage sécurisé des identifiants** dans `~/.swiftly_config.json` (permissions 600)

### 📊 **Dashboard Web**
- Interface web complète accessible via `/dashboard`
- **Authentification** : pages de connexion et inscription stylisées avec Tailwind CSS
- **Gestion visuelle des sites** :
  - Liste des sites avec aperçu et compteur de fichiers
  - Déploiement via formulaire avec support du drag & drop
  - Suppression de sites
- **Responsive design** : interface moderne et cohérente avec la landing page
- **Analytics intégrées** : page dédiée pour chaque site avec statistiques détaillées

### 📈 **Système d'Analytics**
- **Collecte automatique** des visites lors de l'accès aux sites déployés
- **Chiffrement des données** avec Fernet (cryptography) pour protéger les informations sensibles
- **Données collectées** :
  - Timestamp de visite
  - Adresse IP (chiffrée)
  - Pays estimé
  - Système d'exploitation (Windows, macOS, Linux, Android, iOS)
  - Navigateur (Chrome, Firefox, Safari, Edge, Opera)
  - Referrer et chemin d'accès
  - User-Agent et langue
- **Dashboard d'analytics** : statistiques agrégées (nombre de visites, top OS, top navigateurs, etc.)
- **Stockage par site** : fichiers `.analytics.json` chiffrés dans chaque dossier de site

### 🔐 **Sécurité**
- **Hachage des mots de passe** avec bcrypt (algorithme robuste)
- **Authentification** via headers HTTP (`X-User-Email`, `X-User-Password`)
- **Validation et sanitization** des noms de fichiers avec `secure_filename()`
- **Protection contre la traversée de répertoires**
- **Prévention des doublons** de noms de sites
- **Chiffrement des données analytics** avec clé configurée (`ANALYTICS_ENCRYPTION_KEY`)

### 🗂️ **Base de données**
- **Stockage JSON** simple et efficace (`db/sites.json`)
- Structure de données claire pour utilisateurs et sites
- Pas de dépendance externe (PostgreSQL, MySQL, etc.)

---

## 🛠️ Architecture technique

### **Stack technologique**
- **Backend** : Flask 3.0.0 (Python 3.8+)
- **Sécurité** : bcrypt 4.1.2, cryptography 41.0.7
- **HTTP Client** : requests 2.31.0
- **Frontend** : Tailwind CSS (dashboard et templates)

### **Structure du projet**
```
swiftly/
├── __init__.py           # Factory pattern pour l'app Flask
├── config.py             # Configuration (host, port, clés de chiffrement)
├── database.py           # Gestion de la base JSON (CRUD utilisateurs/sites)
├── analytics.py          # Module de tracking et chiffrement des visites
├── models/               # Modèles de données (Site, User)
├── routes/               # Blueprints Flask (auth, sites, dashboard, user, main)
└── utils/                # Décorateurs (require_auth)
```

### **Routes API principales**
- `GET /health` — Statut de l'API
- `POST /api/auth/register` — Création de compte
- `POST /api/auth/login` — Authentification
- `GET /api/sites` — Liste des sites de l'utilisateur
- `POST /api/sites` — Déploiement d'un nouveau site
- `DELETE /api/sites/<site_name>` — Suppression de site
- `GET /sites/<site_name>/` — Accès au site déployé
- `GET /dashboard/site/<site_name>` — Analytics du site

---

## 🎯 Cas d'usage

Swiftly est parfait pour :
- 🎨 **Portfolios personnels**
- 📝 **Blogs statiques**
- 🌐 **Landing pages**
- 🧪 **Démos de prototypes**
- 🏫 **Projets étudiants**
- 🚀 **Déploiements rapides** lors de hackathons

---

## 📦 Installation et démarrage

### **Installation rapide (CLI uniquement)**
```bash
curl -O https://raw.githubusercontent.com/ruikdev/Swiftly/main/swiftly_cli.py
pip install requests
python3 swiftly_cli.py
```

### **Installation complète (Serveur + CLI)**
```bash
git clone https://github.com/ruikdev/Swiftly.git
cd Swiftly
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Le serveur démarre sur `http://localhost:5000` 🎉

### **Utilisation des scripts d'installation**
- **Linux/macOS** : `./swiftly.sh`
- **Windows** : `swiftly.bat`

---

## 🐛 Corrections et améliorations

### **Corrections majeures**
- ✅ Correction du bug de création de site en base de données locale
- ✅ Remplacement de SHA256 par bcrypt pour le hachage des mots de passe (sécurité renforcée)
- ✅ Amélioration de la détection de Python dans les scripts d'installation
- ✅ Gestion des erreurs améliorée lors du téléchargement de `swiftly_cli.py`
- ✅ Correction des chemins absolus transformés automatiquement en relatifs pour éviter les liens cassés

### **Améliorations**
- 🔄 Refactorisation complète du code pour améliorer la lisibilité et la maintenabilité
- 🎨 Harmonisation du design du dashboard avec la landing page
- 📱 Amélioration de la responsivité des templates
- 🌍 Support complet de l'internationalisation (FR/EN) dans le CLI
- 🔗 Ajout de liens de contact dans les footers des templates
- 📖 Documentation complète du système d'analytics (`ANALYTICS.md`)

---

## 🚧 Breaking Changes

**Aucun breaking change** pour cette première release stable.

Si vous migrez depuis une version de développement antérieure :
- Les mots de passe doivent être **réinitialisés** si vous aviez utilisé une version avec SHA256 (migration vers bcrypt)
- La base de données JSON reste compatible

---

## 📚 Documentation

- **README principal** : [README.md](README.md)
- **README français** : [README.fr.md](README.fr.md)
- **Documentation Analytics** : [ANALYTICS.md](ANALYTICS.md) (si disponible)
- **Configuration des domaines personnalisés** : [CUSTOM_DOMAINS.md](CUSTOM_DOMAINS.md) (si disponible)

---

## 🗺️ Roadmap future

Fonctionnalités prévues pour les prochaines versions :
- [ ] Support complet des domaines personnalisés
- [ ] Automatisation des certificats SSL/TLS
- [ ] Intégration Git pour déploiements automatiques
- [ ] Variables d'environnement par site
- [ ] Intégration CDN
- [ ] Webhooks pour CI/CD
- [ ] API v2 avec authentification JWT

---

## 👥 Contributeurs

**Total de commits** : 64 commits

---

## 🙏 Remerciements

- Projet construit avec [Flask](https://flask.palletsprojects.com/)
- Inspiré par [Netlify](https://www.netlify.com/)
- Stylisé avec [Tailwind CSS](https://tailwindcss.com/)
- Créé pour la communauté [Flavortown Hack Club](https://flavortown.hackclub.com/) 🍔

---

## 📄 Licence

Ce projet est sous licence **MIT** — voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🎉 Comment démarrer ?

1. **Cloner le repo** : `git clone https://github.com/ruikdev/Swiftly.git`
2. **Installer les dépendances** : `pip install -r requirements.txt`
3. **Lancer le serveur** : `python app.py`
4. **Accéder au dashboard** : `http://localhost:5000/dashboard`
5. **Ou utiliser le CLI** : `python3 swiftly_cli.py`

---

<div align="center">

**Made with ❤️ by [@ruikdev](https://github.com/ruikdev)**

⭐ **N'oubliez pas de star le repo si Swiftly vous est utile !**

[GitHub](https://github.com/ruikdev/Swiftly) • [Issues](https://github.com/ruikdev/Swiftly/issues) • [Flavortown Hack Club](https://flavortown.hackclub.com/)

</div>

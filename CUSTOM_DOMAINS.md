# Configuration Automatisée des Domaines (Namecheap) - Swiftly

## 📋 Vue d'ensemble

Ce document explique le fonctionnement du système de domaines personnalisés **100% automatisé**. 
En tant qu'utilisateur, vous n'avez qu'une seule action à faire : ajouter le domaine via le CLI ou l'API.

Swiftly s'occupe automatiquement (via des scripts en arrière-plan) de :
1.  📡 Configurer le DNS chez Namecheap (A Record).
2.  🔐 Générer et installer le certificat SSL (Let's Encrypt).
3.  ⚙️ Configurer Nginx pour le routage.

## 🔄 Architecture Automatisée

```
┌─────────────────┐      1. Requête API        ┌──────────────────────┐
│  Utilisateur    │ ─────────────────────────> │      Swiftly API     │
└─────────────────┘      (Ajout domaine)       │  (Task Queue Async)  │
                                               └──────────┬───────────┘
                                                          │
         ┌────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────┐      2. API Call       ┌──────────────────────┐
│  Configurateur DNS   │ ─────────────────────> │   Namecheap API      │
│  (Python Script)     │ <───────────────────── │ (Update A Record)    │
└──────────────────────┘      Confirm OK        └──────────────────────┘
         │
         │ 3. Attente propagation (polling)
         ▼
┌──────────────────────┐      4. Shell Cmd      ┌──────────────────────┐
│  Configurateur SSL   │ ─────────────────────> │  Certbot & Nginx     │
│  (Sudo Wrapper)      │                        │ (Gen Cert + Reload)  │
└──────────────────────┘                        └──────────────────────┘
```

## ⚙️ Configuration Serveur (Admin)

Pour que l'automatisation fonctionne, le serveur Swiftly doit être configuré avec les accès Namecheap.

### 1. Variables d'environnement / Config

Ajoutez ces configurations dans `swiftly/config.py` ou `.env` :

```python
# Configuration Namecheap
NAMECHEAP_API_USER = "votre_username"
NAMECHEAP_API_KEY = "votre_api_key"
NAMECHEAP_USERNAME = "votre_username"
NAMECHEAP_CLIENT_IP = "IP_DE_VOTRE_SERVEUR"  # Doit être whitelistée chez Namecheap
NAMECHEAP_SANDBOX = False  # True pour tester

# Configuration Serveur
SERVER_PUBLIC_IP = "XXX.XXX.XXX.XXX"  # L'IP vers laquelle Pointer les DNS
```

### 2. Permissions Système

Le processus web (Flask) a besoin de droits spécifiques pour recharger Nginx et lancer Certbot. 
Ajoutez ceci au fichier `/etc/sudoers` :

```bash
# Autoriser l'utilisateur 'swiftly_user' à lancer le script d'auto-config
swiftly_user ALL=(root) NOPASSWD: /usr/bin/certbot, /usr/sbin/nginx, /path/to/swiftly/scripts/configure_domain.sh
```

## 🚀 Utilisation (Pour l'utilisateur)

### Ajouter un domaine (C'est tout !)

C'est la seule étape requise.

**Via CLI :**
```bash
python swiftly_cli.py
# Menu → 8. Configurer Domaines Personnalisés
# Entrer: mon-super-site.com
```

**Via API :**
```bash
POST /api/sites/mon-site/domains
{
  "domain": "mon-super-site.com"
}
```

---
*Une fois la commande lancée, le statut du domaine passera de `PENDING` à `ACTIVE` en quelques minutes (temps de propagation DNS et génération SSL).*
---

## 🛠 Ce que fait le code en arrière-plan

Dès réception de la demande, Swiftly exécute la séquence suivante :

### 1. Automatisation DNS (Namecheap)
Le système utilise l'API `namecheap.domains.dns.setHosts` pour :
*   Récupérer les enregistrements existants du domaine.
*   Ajouter un enregistrement `A` (`@`) pointant vers `SERVER_PUBLIC_IP`.
*   Ajouter un enregistrement `CNAME` (`www`) pointant vers `mon-super-site.com`.

### 2. Automatisation SSL & Nginx
Une fois le DNS propagé (vérification par boucle de test DNS locale), le système :
*   Appelle Certbot : `certbot certonly --nginx -d mon-super-site.com --non-interactive`
*   Crée/Met à jour le fichier de config Nginx `/etc/nginx/sites-available/swiftly_custom_domains` :
    ```nginx
    server {
        listen 443 ssl;
        server_name mon-super-site.com;
        ssl_certificate /etc/letsencrypt/live/mon-super-site.com/fullchain.pem;
        # ... options SSL ...
        location / {
            proxy_pass http://127.0.0.1:5000/sites/mon-site/;
        }
    }
    ```
*   Recharge Nginx : `sudo nginx -s reload`

## 📡 Statuts du domaine

L'API retourne l'état de la configuration :

*   **PENDING_DNS** : En attente de propagation DNS.
*   **PENDING_SSL** : DNS OK, en attente de génération du certificat.
*   **ACTIVE** : Domaine opérationnel et sécurisé.
*   **ERROR** : Une intervention manuelle est requise (voir logs).

## ⚠️ Limitations & Sécurité

1.  **Whitelist IP** : Votre IP serveur DOIT être whitelistée dans le panel Namecheap API.
2.  **Temps d'attente** : La propagation DNS peut prendre de 1 à 30 minutes. L'utilisateur doit être prévenu.
3.  **Rate Limits** : Attention aux limites de l'API Namecheap et de Let's Encrypt (5 certificats par semaine pour le même domaine racine).

---

**Version:** 2.0 (Auto-Pilot) | **Date:** Jan 2026

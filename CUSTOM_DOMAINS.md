# Configuration des Sous-Domaines Automatiques (Wildcard) - Swiftly

## 📋 Vue d'ensemble

Ce document explique comment configurer Swiftly pour que chaque site déployé obtienne **automatiquement et instantanément** son propre sous-domaine.

Exemple : 
*   Site déployé : `mon-projet`
*   URL générée : `mon-projet.swiftly.ruikdev.me` (ou votre propre sous-domaine)

Contrairement aux domaines personnalisés externes, ici **aucune action n'est requise** à chaque déploiement. L'infrastructure est prête à accueillir n'importe quel nom de site.

## 🔄 Comment ça fonctionne (La méthode Wildcard)

Au lieu de créer un enregistrement DNS pour chaque site via l'API (ce qui serait lent à propager), nous utilisons une entrée **Wildcard DNS**.

```
┌────────────────────────────────────────────────────────────┐
│                  DNS (Cloudflare)                          │
│  Record: *.swiftly  ───A───>  IP_DU_SERVEUR                │
└──────────────────────────┬─────────────────────────────────┘
                           │
             ┌─────────────▼──────────────┐
             │   Tout trafic *.swiftly    │
             │   arrive ici               │
             └─────────────┬──────────────┘
                           │
             ┌─────────────▼──────────────┐
             │   Nginx (Reverse Proxy)    │
             │   Server: *.swiftly...     │
             │   RegEx extrait le nom     │
             └─────────────┬──────────────┘
                           │
             ┌─────────────▼──────────────┐
             │   Swiftly API              │
             │   Serve /sites/mon-projet  │
             └────────────────────────────┘
```

### Avantages
1.  **Instantané** : Le sous-domaine marche dès la seconde où le site est créé.
2.  **Zéro API Call** : Pas besoin d'appeler Namecheap à chaque création de site.
3.  **Certificat Unique** : Un seul certificat SSL Wildcard couvre tout.

## ⚙️ Configuration Requise (Admin)

### 1. Configuration DNS (Cloudflare)

Allez dans Cloudflare → **DNS** et ajoutez **une seule fois** cet enregistrement pour votre domaine principal (ex: `ruikdev.me`) :

| Type | Name | Content | TTL | Proxy |
|------|------|---------|-----|-------|
| A Record | *.swiftly | 123.456.789.000 (IP Serveur) | Automatic | DNS Only (Nuage gris) |

*(Si votre base est `ruikdev.me` directement, mettez `*` dans Name.)*

Note importante : laissez le statut en **DNS Only** (nuage gris). Si vous activez le proxy Cloudflare (nuage orange), les certificats et le routage ne fonctionneront pas correctement pour `*.swiftly.ruikdev.me`.

### 2. Configuration SSL Wildcard (Certbot + Cloudflare)

Puisque Cloudflare gère maintenant vos DNS, utilisez le plugin Cloudflare pour Certbot afin d'obtenir un certificat Let's Encrypt valide pour `swiftly.ruikdev.me` et `*.swiftly.ruikdev.me` :

1.  **Installer le plugin Cloudflare pour Certbot :**
    ```bash
    sudo apt-get update
    sudo apt-get install -y python3-certbot-dns-cloudflare
    # ou via pip si besoin
    sudo pip install certbot-dns-cloudflare
    ```

2.  **Créer un API Token Cloudflare :**
    * Cloudflare → Mon profil → API Tokens → Create Token
    * Choisissez le template **"Edit zone DNS"** et limitez-le au ou aux zones nécessaires.

3.  **Créer le fichier de credentials :**
    ```ini
    # ~/.secrets/certbot/cloudflare.ini
    dns_cloudflare_api_token = VOTRE_TOKEN_ICI
    ```
    Puis sécurisez le fichier :
    ```bash
    chmod 600 ~/.secrets/certbot/cloudflare.ini
    ```

4.  **Générer le certificat :**
    ```bash
    sudo certbot certonly \
      --dns-cloudflare \
      --dns-cloudflare-credentials ~/.secrets/certbot/cloudflare.ini \
      -d 'swiftly.ruikdev.me' \
      -d '*.swiftly.ruikdev.me'
    ```

Après exécution, Certbot indiquera le chemin des certificats (généralement `/etc/letsencrypt/live/swiftly.ruikdev.me/`).

### 3. Configuration Nginx

Modifiez votre configuration Nginx pour intercepter tous les sous-domaines dynamiquement.

```nginx
# /etc/nginx/sites-available/swiftly_wildcard

server {
    listen 443 ssl http2;
    server_name ~^(?<site_name>.+)\.swiftly\.ruikdev\.me$;

    # Certificat Wildcard
    ssl_certificate /etc/letsencrypt/live/swiftly.ruikdev.me/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/swiftly.ruikdev.me/privkey.pem;

    # Logs séparés (optionnel)
    access_log /var/log/nginx/swiftly_access.log;
    error_log /var/log/nginx/swiftly_error.log;

    location / {
        # Proxy vers Swiftly en injectant le nom du site
        proxy_pass http://127.0.0.1:5000/sites/$site_name/;
        
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Gestion des erreurs si le site n'existe pas
        proxy_intercept_errors on;
        error_page 404 = @not_found;
    }

    location @not_found {
        return 404 "Site introuvable ou non déployé sur Swiftly.";
    }
}

# Redirection HTTP -> HTTPS
server {
    listen 80;
    server_name *.swiftly.ruikdev.me;
    return 301 https://$host$request_uri;
}
```

## 🚀 Utilisation (Pour l'utilisateur)

**Absolument rien à faire !**

Dès qu'un utilisateur crée un site nommé `super-app` :
1.  Swiftly crée le dossier `/sites/super-app`.
2.  L'utilisateur peut immédiatement aller sur `https://super-app.swiftly.ruikdev.me`.
3.  Le DNS Wildcard dirige vers le serveur.
4.  Le Certificat Wildcard sécurise la connexion.
5.  Nginx extrait `super-app` et demande le contenu à Swiftly.

## ✅ Checklist Mise en Place

- [ ] DNS Wildcard (`*.votresousdomaine`) pointé vers l'IP (Cloudflare, `DNS Only`).
- [ ] API Token Cloudflare créé et fichier de credentials configuré.
- [ ] Certificat SSL Wildcard généré avec `certbot-dns-cloudflare`.
- [ ] Config Nginx avec Regex `server_name` en place.

---

**Version:** 3.0 (Wildcard Subdomains) | **Date:** Jan 2026

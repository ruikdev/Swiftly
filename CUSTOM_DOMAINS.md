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
│                  DNS (Namecheap)                           │
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

### 1. Configuration DNS (Namecheap)

Connectez-vous à votre panel Namecheap et ajoutez **une seule fois** cet enregistrement pour votre domaine principal (ex: `ruikdev.me`) :

| Type | Host | Value | TTL |
|------|------|-------|-----|
| A Record | *.swiftly | 123.456.789.000 (Ip Serveur) | Automatic |

*(Si votre base est juste `ruikdev.me` directement, mettez `*` dans Host)*

### 2. Configuration SSL Wildcard (Certbot + Namecheap)

Pour avoir HTTPS sur `*.swiftly.ruikdev.me`, il faut un certificat Wildcard. Cela requiert une validation DNS (d'où le besoin de l'API Namecheap).

1.  **Installer le plugin Namecheap pour Certbot :**
    ```bash
    sudo pip install certbot-dns-namecheap
    ```

2.  **Créer un fichier de credentials `namecheap.ini` :**
    ```ini
    dns_namecheap_username = votre_username
    dns_namecheap_api_key = votre_api_key
    ```
    *Note: Sécurisez ce fichier (`chmod 600`).*

3.  **Générer le certificat :**
    ```bash
    sudo certbot certonly \
      --dns-namecheap \
      --dns-namecheap-credentials /path/to/namecheap.ini \
      -d 'swiftly.ruikdev.me' \
      -d '*.swiftly.ruikdev.me'
    ```

Cette commande créera un certificat valide pour `tout-ce-que-vous-voulez.swiftly.ruikdev.me`.

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

- [ ] DNS Wildcard (`*.votresousdomaine`) pointé vers l'IP.
- [ ] API Key Namecheap activée et IP whitelistée (pour Certbot).
- [ ] Certificat SSL Wildcard généré avec `certbot-dns-namecheap`.
- [ ] Config Nginx avec Regex `server_name` en place.

---

**Version:** 3.0 (Wildcard Subdomains) | **Date:** Jan 2026

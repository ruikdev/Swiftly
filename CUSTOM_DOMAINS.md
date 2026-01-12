# Configuration des Domaines Personnalisés - Swiftly

## 📋 Vue d'ensemble

Ce document explique comment configurer et utiliser les domaines personnalisés dans Swiftly. Au lieu de servir vos sites uniquement via `swiftly.ruikdev.me/sites/lesite`, vous pouvez associer vos propres domaines (ex: `mon-site.fr`) qui redirigent automatiquement vers votre site Swiftly.

## 🔄 Comment ça fonctionne

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Votre Domaine                            │
│                      mon-site.fr                                │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ DNS A Record pointant vers votre serveur (même IP)     │  │
│  └─────────────────────────────────────────────────────────┘  │
│                           │                                     │
│                           ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Nginx Reverse Proxy (Écoute mon-site.fr)              │  │
│  │ Rewrite: mon-site.fr/* → /sites/mon-site/*            │  │
│  └─────────────────────────────────────────────────────────┘  │
│                           │                                     │
│                           ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Swiftly API                                            │  │
│  │ GET /sites/mon-site/index.html                         │  │
│  └─────────────────────────────────────────────────────────┘  │
│                           │                                     │
│                           ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Fichiers du site stockés dans /sites/mon-site/        │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Points clés

1. **Swiftly stocke les domaines** — Chaque site peut avoir plusieurs domaines associés
2. **Nginx fait le routage** — Nginx reçoit les requêtes sur les domaines perso et les redirige via reverse proxy
3. **DNS pointe vers votre serveur** — Tous les domaines perso pointent vers la même IP que `swiftly.ruikdev.me`
4. **URLs parallèles** — `/sites/lesite` ET `lesite.com` accèdent au même contenu

## 🚀 Démarrage rapide

### 1️⃣ Ajouter un domaine à votre site (CLI)

```bash
python swiftly_cli.py
# Menu → Voir mon profil → Gérer domaines
# Entrer: mon-site.fr
```

Ou via **API**:
```bash
curl -X POST http://swiftly.ruikdev.me/api/sites/mon-site/domains \
  -H "X-User-Email: user@example.com" \
  -H "X-User-Password: votre_mot_de_passe" \
  -H "Content-Type: application/json" \
  -d '{"domain": "mon-site.fr"}'
```

### 2️⃣ Configurer le DNS

Chez votre registraire DNS (OVH, Cloudflare, etc.):

```
Type:  A
Nom:   mon-site.fr (ou @)
IP:    XXX.XXX.XXX.XXX  (même IP que swiftly.ruikdev.me)
TTL:   3600
```

Attendez 10-30min de propagation DNS.

### 3️⃣ Configurer Nginx

Ajouter un nouveau `server` block dans votre config Nginx:

```nginx
# /etc/nginx/sites-available/custom-domains

server {
    listen 80;
    listen [::]:80;
    
    # Accepter tous les domaines personnalisés
    server_name ~^(?<domain>.+)\.(?:fr|com|io|dev)$;
    
    # Redirection HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    
    # Accepter tous les domaines personnalisés
    server_name ~^(?<domain>.+)\.(?:fr|com|io|dev)$;
    
    # Certificats SSL (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/swiftly.ruikdev.me/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/swiftly.ruikdev.me/privkey.pem;
    
    # Configuration SSL standard
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Reverse proxy vers Swiftly
    location / {
        # Extraire le nom du site du domaine
        # Ex: mon-site.fr → mon-site
        set $site_name $domain;
        
        # Passer au service Swiftly interne
        proxy_pass http://localhost:5000/sites/$site_name/;
        
        # Headers nécessaires
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Buffering
        proxy_buffering off;
    }
}
```

Activer et redémarrer Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/custom-domains /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4️⃣ SSL/HTTPS automatique

Si vous avez déjà Certbot configuré pour `swiftly.ruikdev.me`:

```bash
# Renouveler les certificats avec les nouveaux domaines
sudo certbot renew --expand --cert-name swiftly.ruikdev.me \
  -d swiftly.ruikdev.me \
  -d mon-site.fr \
  -d autre-site.io
```

Ou générer un certificat wildcard:
```bash
sudo certbot certonly --nginx -d '*.ruikdev.me'
```

## 📡 Gestion des domaines - API Référence

### Lister les domaines d'un site

**Requête:**
```bash
GET /api/sites/mon-site
Headers:
  X-User-Email: user@example.com
  X-User-Password: mot_de_passe
```

**Réponse:**
```json
{
  "sites": {
    "mon-site": {
      "folder": "mon-site",
      "owner": "user@example.com",
      "domains": ["mon-site.fr", "www.mon-site.fr"],
      "primary_domain": "mon-site.fr"
    }
  }
}
```

### Ajouter un domaine

**Requête:**
```bash
POST /api/sites/mon-site/domains
Headers:
  X-User-Email: user@example.com
  X-User-Password: mot_de_passe
  Content-Type: application/json

Body:
{
  "domain": "mon-site.fr"
}
```

**Réponse (201):**
```json
{
  "message": "Domaine ajouté avec succès",
  "domain": "mon-site.fr"
}
```

### Retirer un domaine

**Requête:**
```bash
DELETE /api/sites/mon-site/domains/mon-site.fr
Headers:
  X-User-Email: user@example.com
  X-User-Password: mot_de_passe
```

**Réponse (200):**
```json
{
  "message": "Domaine supprimé avec succès"
}
```

### Définir le domaine principal

**Requête:**
```bash
PUT /api/sites/mon-site/domains/primary
Headers:
  X-User-Email: user@example.com
  X-User-Password: mot_de_passe
  Content-Type: application/json

Body:
{
  "primary_domain": "www.mon-site.fr"
}
```

## ✅ Checklist Configuration

- [ ] Site créé dans Swiftly et déployé
- [ ] Domaine personnalisé ajouté via API ou CLI
- [ ] Enregistrement DNS A configuré (pointe vers votre serveur)
- [ ] DNS propagé (vérifier avec `nslookup mon-site.fr`)
- [ ] Config Nginx ajoutée et testée (`nginx -t`)
- [ ] Nginx redémarré
- [ ] Certificat SSL/TLS valide et à jour
- [ ] HTTPS redirige correctement (test avec browser)
- [ ] Site accessible via domaine personnalisé

## 🔍 Vérification & Troubleshooting

### Vérifier la propagation DNS
```bash
nslookup mon-site.fr
dig mon-site.fr +short
```

### Tester le reverse proxy Nginx
```bash
curl -H "Host: mon-site.fr" http://localhost/
# Devrait retourner le contenu du site
```

### Vérifier les logs Nginx
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Vérifier la config Nginx
```bash
sudo nginx -t -c /etc/nginx/nginx.conf
```

### Problème: "Site not found" (404)

1. Vérifier que le site existe dans Swiftly: `/api/sites`
2. Vérifier que le domaine est enregistré: `GET /api/sites/mon-site`
3. Vérifier que le `site_name` dans Nginx config correspond au nom Swiftly

### Problème: Certificat SSL invalide

```bash
# Renouveler les certificats
sudo certbot renew --force-renewal

# Ou ajouter un nouveau domaine
sudo certbot certonly --nginx -d mon-site.fr
```

### Problème: Erreur "Connection refused"

1. Vérifier que Swiftly tourne: `curl http://localhost:5000/health`
2. Vérifier la configuration Nginx `proxy_pass`
3. Vérifier les logs Nginx et Swiftly

## 📚 Exemples complets

### Exemple 1: Site portfolio perso

```bash
# 1. Créer le site
swiftly_cli.py → Déployer un nouveau site
Nom: portfolio
Dossier: ~/projects/portfolio

# 2. Ajouter les domaines
POST /api/sites/portfolio/domains
  {"domain": "john-doe.fr"}

POST /api/sites/portfolio/domains
  {"domain": "www.john-doe.fr"}

# 3. Config DNS
A record: john-doe.fr → 203.0.113.42

# 4. Config Nginx déjà faite (voir section Configuration)

# 5. Accès
- https://swiftly.ruikdev.me/sites/portfolio/
- https://john-doe.fr/
- https://www.john-doe.fr/
```

### Exemple 2: Blog avec sous-domaine

```bash
# Site: mon-blog
POST /api/sites/mon-blog/domains
  {"domain": "blog.example.com"}

# DNS:
CNAME blog.example.com → swiftly.ruikdev.me
# OU
A blog.example.com → 203.0.113.42

# Accès: https://blog.example.com/
```

## 🔒 Sécurité

### Points importants

1. **Validation de domaine** — Seuls les propriétaires de site peuvent ajouter des domaines
2. **Authentification** — L'API requiert email + mot de passe
3. **HTTPS obligatoire** — Tous les domaines servis via SSL/TLS
4. **Isolation des sites** — Nginx vérifie les permissions avant de servir

### À faire

- [ ] Implémenter rate-limiting sur les endpoints de domaines
- [ ] Ajouter logs d'audit pour les modifications de domaines
- [ ] Vérifier la propriété du domaine (optionnel: validation email)

## 📞 Support & Questions

Pour des questions ou issues:
1. Vérifier la section Troubleshooting
2. Consulter les logs (`/var/log/nginx/`, Swiftly app logs)
3. Tester avec `curl` et les headers appropriés

---

**Version:** 1.0 | **Date:** Jan 2026

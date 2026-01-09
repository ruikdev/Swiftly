from flask import Flask, jsonify, request, send_from_directory, abort, render_template
import json
import os
import hashlib
from functools import wraps

app = Flask(__name__)
db_sites = "db/sites.json"
db_users = "db/users.json"
sites_folder = "sites"

# ========== Gestion des utilisateurs ==========

def load_users():
    if os.path.exists(db_users):
        with open(db_users, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

users = load_users()

def save_users():
    try:
        os.makedirs("db", exist_ok=True)
        with open(db_users, 'w') as f:
            json.dump(users, f, indent=4)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des utilisateurs : {e}")

def hash_password(password):
    """Hasher un mot de passe avec SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(email, password):
    """Créer un nouvel utilisateur"""
    if email in users:
        return False
    users[email] = {
        "password": hash_password(password),
        "sites": []
    }
    save_users()
    return True

def verify_user(email, password):
    """Vérifier les identifiants d'un utilisateur"""
    if email not in users:
        return False
    return users[email]["password"] == hash_password(password)

def update_user_email(old_email, new_email, password):
    """Mettre à jour l'email d'un utilisateur"""
    if old_email not in users or new_email in users:
        return False
    if not verify_user(old_email, password):
        return False
    users[new_email] = users.pop(old_email)
    # Mettre à jour les sites liés à cet utilisateur
    for site_name, site_data in sites.items():
        if site_data.get("owner") == old_email:
            site_data["owner"] = new_email
    save_users()
    save_db()
    return True

def update_user_password(email, old_password, new_password):
    """Mettre à jour le mot de passe d'un utilisateur"""
    if not verify_user(email, old_password):
        return False
    users[email]["password"] = hash_password(new_password)
    save_users()
    return True

# Décorateur pour protéger les routes
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_email = request.headers.get('X-User-Email')
        auth_password = request.headers.get('X-User-Password')
        
        if not auth_email or not auth_password:
            return jsonify(error="Authentification requise. Utilisez les headers 'X-User-Email' et 'X-User-Password'"), 401
        
        if not verify_user(auth_email, auth_password):
            return jsonify(error="Email ou mot de passe incorrect"), 401
        
        # Passer l'email à la fonction
        return f(auth_email, *args, **kwargs)
    return decorated_function

# ========== Gestion des sites ==========

# Charger la base de données dans une variable
def load_db():
    if os.path.exists(db_sites):
        with open(db_sites, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {} # Retourne un dictionnaire vide si le fichier est mal formé
    return {}

sites = load_db()

def save_db():
    try:
        os.makedirs("db", exist_ok=True)
        with open(db_sites, 'w') as f:
            json.dump(sites, f, indent=4)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde : {e}")

def add_site_to_db(name, filename, owner):
    sites[name] = {
        "filename": filename,
        "owner": owner
    }
    if owner in users:
        if name not in users[owner]["sites"]:
            users[owner]["sites"].append(name)
        save_users()
    save_db()
    return True

def get_all_sites():
    return sites

def get_user_sites(email):
    """Retourner uniquement les sites d'un utilisateur"""
    user_sites = {}
    for name, data in sites.items():
        # Support ancien format (string) et nouveau format (dict)
        if isinstance(data, dict):
            if data.get("owner") == email:
                user_sites[name] = data
        # Ignorer les sites en ancien format (sans propriétaire)
    return user_sites

def delete_site_from_db(name, owner=None):
    if name in sites:
        # Vérifier si l'utilisateur est le propriétaire
        if owner and sites[name].get("owner") != owner:
            return False
        
        # Retirer le site de la liste de l'utilisateur
        site_owner = sites[name].get("owner")
        if site_owner and site_owner in users:
            if name in users[site_owner]["sites"]:
                users[site_owner]["sites"].remove(name)
            save_users()
        
        del sites[name]
        save_db()
        return True
    return False

@app.route("/")
def index():
    return render_template("base.html")

@app.route("/health")
def health():
    return jsonify(status="ok")

# ========== Routes d'authentification ==========

@app.route("/api/auth/register", methods=["POST"])
def register():
    """Créer un nouveau compte utilisateur"""
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify(error="Email et mot de passe requis"), 400
    
    email = data['email']
    password = data['password']
    
    if len(password) < 6:
        return jsonify(error="Le mot de passe doit contenir au moins 6 caractères"), 400
    
    if create_user(email, password):
        return jsonify(message=f"Compte créé avec succès pour {email}"), 201
    else:
        return jsonify(error=f"Un compte avec l'email {email} existe déjà"), 409

@app.route("/api/auth/login", methods=["POST"])
def login():
    """Vérifier les identifiants de connexion"""
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify(error="Email et mot de passe requis"), 400
    
    email = data['email']
    password = data['password']
    
    if verify_user(email, password):
        return jsonify(message="Connexion réussie", email=email), 200
    else:
        return jsonify(error="Email ou mot de passe incorrect"), 401

@app.route("/api/user/profile", methods=["GET"])
@require_auth
def get_profile(auth_email):
    """Obtenir le profil de l'utilisateur connecté"""
    user_data = users.get(auth_email, {})
    return jsonify(
        email=auth_email,
        sites=user_data.get("sites", []),
        total_sites=len(user_data.get("sites", []))
    ), 200

@app.route("/api/user/update-email", methods=["PUT"])
@require_auth
def update_email(auth_email):
    """Mettre à jour l'email de l'utilisateur"""
    data = request.get_json()
    
    if not data or 'new_email' not in data or 'password' not in data:
        return jsonify(error="Nouvel email et mot de passe requis"), 400
    
    new_email = data['new_email']
    password = data['password']
    
    if update_user_email(auth_email, new_email, password):
        return jsonify(message=f"Email mis à jour avec succès. Nouvel email: {new_email}"), 200
    else:
        return jsonify(error="Impossible de mettre à jour l'email. Vérifiez que le mot de passe est correct et que le nouvel email n'est pas déjà utilisé"), 400

@app.route("/api/user/update-password", methods=["PUT"])
@require_auth
def update_password(auth_email):
    """Mettre à jour le mot de passe de l'utilisateur"""
    data = request.get_json()
    
    if not data or 'old_password' not in data or 'new_password' not in data:
        return jsonify(error="Ancien et nouveau mot de passe requis"), 400
    
    old_password = data['old_password']
    new_password = data['new_password']
    
    if len(new_password) < 6:
        return jsonify(error="Le nouveau mot de passe doit contenir au moins 6 caractères"), 400
    
    if update_user_password(auth_email, old_password, new_password):
        return jsonify(message="Mot de passe mis à jour avec succès"), 200
    else:
        return jsonify(error="Ancien mot de passe incorrect"), 400

# ========== Routes pour les sites ==========

# Route pour servir les sites statiques
@app.route("/sites/<site_name>")
def serve_site(site_name):
    """Servir une page HTML depuis le dossier sites/"""
    # Vérifier si le site existe dans la DB
    if site_name not in sites:
        abort(404, description=f"Le site '{site_name}' n'existe pas")

    site_data = sites[site_name]
    # Support ancien format (string) et nouveau format (dict)
    filename = site_data if isinstance(site_data, str) else site_data.get("filename")
    filepath = os.path.join(sites_folder, filename)

    # Vérifier si le fichier existe
    if not os.path.exists(filepath):
        abort(404, description=f"Le fichier '{filename}' n'existe pas")

    # Servir le fichier HTML
    return send_from_directory(sites_folder, filename)

# API : Lister tous les sites
@app.route("/api/sites", methods=["GET"])
@require_auth
def list_sites(auth_email):
    """Retourner la liste des sites de l'utilisateur connecté"""
    return jsonify(sites=get_user_sites(auth_email))

# API : Ajouter un nouveau site
@app.route("/api/sites", methods=["POST"])
@require_auth
def create_site(auth_email):
    """Ajouter un nouveau site avec upload de fichier HTML"""
    
    # Vérifier si un fichier est présent dans la requête
    if 'file' in request.files:
        # Mode upload: on reçoit le fichier HTML
        file = request.files['file']
        name = request.form.get('name')
        
        # Validation
        if not name:
            return jsonify(error="Le champ 'name' est requis"), 400
        
        if file.filename == '':
            return jsonify(error="Aucun fichier sélectionné"), 400
        
        # Vérifier si le site existe déjà
        if name in sites:
            return jsonify(error=f"Le site '{name}' existe déjà"), 409
        
        # Vérifier l'extension du fichier
        if not file.filename.endswith('.html'):
            return jsonify(error="Le fichier doit être un fichier HTML (.html)"), 400
        
        # Générer un nom de fichier sécurisé
        from werkzeug.utils import secure_filename
        filename = secure_filename(file.filename)
        
        # Si le nom du site est différent du nom de fichier, on peut utiliser le nom du site
        # Pour éviter les conflits, on peut utiliser: name.html
        filename = f"{secure_filename(name)}.html"
        
        # Sauvegarder le fichier
        filepath = os.path.join(sites_folder, filename)
        
        # Créer le dossier sites s'il n'existe pas
        os.makedirs(sites_folder, exist_ok=True)
        
        try:
            file.save(filepath)
        except Exception as e:
            return jsonify(error=f"Erreur lors de la sauvegarde du fichier: {str(e)}"), 500
        
        # Ajouter le site à la DB avec le propriétaire
        add_site_to_db(name, filename, auth_email)
        return jsonify(
            message=f"Site '{name}' ajouté avec succès",
            site={name: {"filename": filename, "owner": auth_email}},
            url=f"/sites/{name}"
        ), 201
    
    else:
        return jsonify(error=f"Votre requete ne contient pas de fichier html"), 404

# API : Supprimer un site
@app.route("/api/sites/<site_name>", methods=["DELETE"])
@require_auth
def remove_site(auth_email, site_name):
    """Supprimer un site (uniquement si l'utilisateur en est le propriétaire)"""
    if delete_site_from_db(site_name, auth_email):
        # Supprimer aussi le fichier physique
        try:
            site_data = sites.get(site_name, {})
            filename = site_data if isinstance(site_data, str) else site_data.get("filename")
            if filename:
                filepath = os.path.join(sites_folder, filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
        except Exception as e:
            print(f"Erreur lors de la suppression du fichier: {e}")
        
        return jsonify(message=f"Site '{site_name}' supprimé avec succès")
    return jsonify(error=f"Le site '{site_name}' n'existe pas ou vous n'en êtes pas le propriétaire"), 404



if __name__ == "__main__":
    # Créer les dossiers nécessaires
    os.makedirs("db", exist_ok=True)
    os.makedirs(sites_folder, exist_ok=True)
    
    # Recharger les données
    sites = load_db()
    users = load_users()
    
    app.run(host="0.0.0.0", port=5000, debug=True)
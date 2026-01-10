from flask import Flask, jsonify, request, send_from_directory, abort, render_template
import json
import os
import hashlib
import shutil
from functools import wraps
from werkzeug.utils import secure_filename

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

def add_site_to_db(name, folder, owner):
    sites[name] = {
        "folder": folder,
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
@app.route("/sites/<site_name>/")
@app.route("/sites/<site_name>/<path:subpath>")
def serve_site(site_name, subpath=None):
    """Servir les fichiers d'un site depuis son dossier dédié"""
    # Vérifier si le site existe dans la DB
    if site_name not in sites:
        abort(404, description=f"Le site '{site_name}' n'existe pas")

    site_data = sites[site_name]
    
    # Nouveau format: dossier dédié
    if isinstance(site_data, dict) and "folder" in site_data:
        folder = site_data["folder"]
        site_folder = os.path.join(sites_folder, folder)
        
        # Si pas de sous-chemin, rediriger vers la version avec slash si nécessaire
        if not subpath:
            # Vérifier si l'URL se termine par un slash
            if not request.path.endswith('/'):
                from flask import redirect
                return redirect(request.path + '/', code=301)
            
            index_path = os.path.join(site_folder, "index.html")
            if os.path.exists(index_path):
                return send_from_directory(site_folder, "index.html")
            else:
                abort(404, description=f"index.html introuvable pour le site '{site_name}'")
        
        # Servir le fichier demandé
        file_path = os.path.join(site_folder, subpath)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            # Sécurité: vérifier qu'on ne sort pas du dossier du site
            if os.path.commonpath([site_folder]) == os.path.commonpath([site_folder, file_path]):
                return send_from_directory(site_folder, subpath)
        
        abort(404, description=f"Fichier '{subpath}' introuvable")
    
    # Support ancien format (fichier unique) pour compatibilité
    elif isinstance(site_data, dict) and "filename" in site_data:
        filename = site_data.get("filename")
        filepath = os.path.join(sites_folder, filename)
        if os.path.exists(filepath):
            return send_from_directory(sites_folder, filename)
        abort(404, description=f"Le fichier '{filename}' n'existe pas")
    
    abort(404, description=f"Configuration invalide pour le site '{site_name}'")

# API : Lister tous les sites
@app.route("/api/sites", methods=["GET"])
@require_auth
def list_sites(auth_email):
    """Retourner la liste des sites de l'utilisateur connecté"""
    user_sites = get_user_sites(auth_email)
    # Enrichir avec le nombre de fichiers pour chaque site
    for site_name, site_data in user_sites.items():
        if isinstance(site_data, dict) and "folder" in site_data:
            folder_path = os.path.join(sites_folder, site_data["folder"])
            if os.path.exists(folder_path):
                file_count = sum([len(files) for _, _, files in os.walk(folder_path)])
                site_data["file_count"] = file_count
    return jsonify(sites=user_sites)

# API : Ajouter un nouveau site
@app.route("/api/sites", methods=["POST"])
@require_auth
def create_site(auth_email):
    """Ajouter un nouveau site avec upload de dossier complet"""
    
    name = request.form.get('name')
    
    # Validation du nom
    if not name:
        return jsonify(error="Le champ 'name' est requis"), 400
    
    # Vérifier si le site existe déjà
    if name in sites:
        return jsonify(error=f"Le site '{name}' existe déjà"), 409
    
    # Vérifier si des fichiers sont présents
    if not request.files:
        return jsonify(error="Aucun fichier reçu. Vous devez uploader au moins index.html"), 400
    
    # Créer le dossier du site
    site_folder_name = secure_filename(name)
    site_path = os.path.join(sites_folder, site_folder_name)
    
    # Sécurité: supprimer le dossier s'il existe déjà
    if os.path.exists(site_path):
        shutil.rmtree(site_path)
    
    os.makedirs(site_path, exist_ok=True)
    
    # Récupérer tous les fichiers uploadés
    files_list = request.files.getlist('files')
    has_index = False
    uploaded_files = []
    
    try:
        for file in files_list:
            if file.filename == '':
                continue
            
            # Extraire le chemin relatif (peut contenir des sous-dossiers)
            relative_path = file.filename
            
            # Vérifier si c'est index.html
            if relative_path == 'index.html' or relative_path.endswith('/index.html'):
                has_index = True
            
            # Sécuriser le chemin
            safe_path = secure_filename(relative_path.replace('/', '_SEP_')).replace('_SEP_', '/')
            file_path = os.path.join(site_path, safe_path)
            
            # Créer les sous-dossiers si nécessaire
            file_dir = os.path.dirname(file_path)
            if file_dir:
                os.makedirs(file_dir, exist_ok=True)
            
            # Sauvegarder le fichier
            file.save(file_path)
            uploaded_files.append(relative_path)
        
        # Validation: index.html obligatoire
        if not has_index:
            # Supprimer le dossier créé
            shutil.rmtree(site_path)
            return jsonify(
                error="Le site doit contenir un fichier 'index.html' à la racine",
                uploaded_files=uploaded_files
            ), 400
        
        # Ajouter le site à la DB
        add_site_to_db(name, site_folder_name, auth_email)
        
        return jsonify(
            message=f"Site '{name}' déployé avec succès",
            site={name: {"folder": site_folder_name, "owner": auth_email}},
            url=f"/sites/{name}",
            files_uploaded=len(uploaded_files),
            files=uploaded_files
        ), 201
    
    except Exception as e:
        # En cas d'erreur, nettoyer le dossier
        if os.path.exists(site_path):
            shutil.rmtree(site_path)
        return jsonify(error=f"Erreur lors du déploiement: {str(e)}"), 500

# API : Supprimer un site
@app.route("/api/sites/<site_name>", methods=["DELETE"])
@require_auth
def remove_site(auth_email, site_name):
    """Supprimer un site (uniquement si l'utilisateur en est le propriétaire)"""
    if site_name not in sites:
        return jsonify(error=f"Le site '{site_name}' n'existe pas"), 404
    
    site_data = sites[site_name]
    
    if delete_site_from_db(site_name, auth_email):
        # Supprimer le dossier ou fichier physique
        try:
            # Nouveau format: dossier
            if isinstance(site_data, dict) and "folder" in site_data:
                folder_path = os.path.join(sites_folder, site_data["folder"])
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path)
            # Ancien format: fichier unique
            elif isinstance(site_data, dict) and "filename" in site_data:
                filepath = os.path.join(sites_folder, site_data["filename"])
                if os.path.exists(filepath):
                    os.remove(filepath)
        except Exception as e:
            print(f"Erreur lors de la suppression: {e}")
        
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
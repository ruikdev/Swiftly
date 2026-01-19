"""Routes d'administration"""

from flask import Blueprint, jsonify, request, render_template, session, redirect
from swiftly.database import (
    get_user_by_email, get_all_users, get_all_sites, 
    create_user, delete_user, set_user_admin_status, 
    admin_update_password, delete_site_from_db
)
from swiftly.utils.decorators import require_auth
from swiftly.config import *
import os
import shutil

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
admin_api_bp = Blueprint('admin_api', __name__, url_prefix='/api/admin')

def require_admin(f):
    """Décorateur pour vérifier que l'utilisateur est admin"""
    def decorated_function(*args, **kwargs):
        email = session.get('email')
        if not email:
            return jsonify(error="Non authentifié"), 401
        
        user = get_user_by_email(email)
        if not user or not user.get('is_admin'):
            return jsonify(error="Accès non autorisé - admin requis"), 403
        
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Routes Web
@admin_bp.route('/')
def admin_panel():
    """Page du panel d'administration"""
    email = session.get('email')
    if not email:
        return redirect('/auth')
    
    user = get_user_by_email(email)
    if not user or not user.get('is_admin'):
        return redirect('/dashboard')
    
    return render_template('admin_panel.html')

# Routes API
@admin_api_bp.route('/users', methods=['GET'])
@require_admin
def list_users():
    """Lister tous les utilisateurs"""
    users = get_all_users()
    return jsonify(users=users)

@admin_api_bp.route('/users', methods=['POST'])
@require_admin
def create_user_route():
    """Créer un nouvel utilisateur"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    is_admin = data.get('is_admin', False)
    
    if not email or not password:
        return jsonify(error="Email et mot de passe requis"), 400
    
    if create_user(email, password, is_admin):
        return jsonify(message=f"Utilisateur {email} créé avec succès"), 201
    return jsonify(error="L'utilisateur existe déjà"), 409

@admin_api_bp.route('/users/<email>', methods=['DELETE'])
@require_admin
def delete_user_route(email):
    """Supprimer un utilisateur"""
    # Empêcher la suppression de son propre compte
    current_email = session.get('email')
    if current_email == email:
        return jsonify(error="Vous ne pouvez pas supprimer votre propre compte"), 400
    
    if delete_user(email):
        return jsonify(message=f"Utilisateur {email} supprimé avec succès")
    return jsonify(error="Utilisateur non trouvé"), 404

@admin_api_bp.route('/users/<email>/admin', methods=['PUT'])
@require_admin
def toggle_admin_route(email):
    """Changer le statut admin d'un utilisateur"""
    data = request.get_json()
    is_admin = data.get('is_admin', False)
    
    # Empêcher de se retirer soi-même les droits admin
    current_email = session.get('email')
    if current_email == email and not is_admin:
        return jsonify(error="Vous ne pouvez pas retirer vos propres droits admin"), 400
    
    if set_user_admin_status(email, is_admin):
        status = "admin" if is_admin else "utilisateur standard"
        return jsonify(message=f"{email} est maintenant {status}")
    return jsonify(error="Utilisateur non trouvé"), 404

@admin_api_bp.route('/users/<email>/password', methods=['PUT'])
@require_admin
def admin_change_password_route(email):
    """Changer le mot de passe d'un utilisateur (admin)"""
    data = request.get_json()
    new_password = data.get('new_password')
    
    if not new_password:
        return jsonify(error="Nouveau mot de passe requis"), 400
    
    if admin_update_password(email, new_password):
        return jsonify(message=f"Mot de passe de {email} modifié avec succès")
    return jsonify(error="Utilisateur non trouvé"), 404

@admin_api_bp.route('/sites', methods=['GET'])
@require_admin
def list_all_sites():
    """Lister tous les sites"""
    sites = get_all_sites()
    return jsonify(sites=sites)

@admin_api_bp.route('/sites/<site_name>', methods=['DELETE'])
@require_admin
def admin_delete_site(site_name):
    """Supprimer un site (admin)"""
    from swiftly.database import get_site_by_name
    from swiftly.utils.ssh_manager import remove_subdomain
    
    site = get_site_by_name(site_name)
    if not site:
        return jsonify(error="Site non trouvé"), 404
    
    # Supprimer le domaine custom si configuré
    if site.get('custom_domain') and ENABLE_SSH_MANAGEMENT:
        remove_subdomain(site['custom_domain'])
    
    # Supprimer de la DB (sans vérifier le propriétaire)
    if delete_site_from_db(site_name, owner_email=None):
        # Supprimer le dossier physique
        try:
            folder_path = os.path.join(SITES_FOLDER, site['folder'])
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
        except Exception as e:
            print(f"Erreur lors de la suppression: {e}")
        
        return jsonify(message=f"Site {site_name} supprimé avec succès")
    return jsonify(error="Erreur lors de la suppression"), 500

@admin_api_bp.route('/config', methods=['GET'])
@require_admin
def get_config():
    """Récupérer la configuration du serveur"""
    config = {
        "DOMAIN": DOMAIN,
        "BASE_URL": BASE_URL,
        "SUBDOMAIN_BASE": SUBDOMAIN_BASE,
        "ENABLE_SSH_MANAGEMENT": ENABLE_SSH_MANAGEMENT,
        "SSH_HOST": SSH_HOST,
        "SSH_PORT": SSH_PORT,
        "SSH_USER": SSH_USER,
        "NGINX_SITES_AVAILABLE": NGINX_SITES_AVAILABLE,
        "NGINX_SITES_ENABLED": NGINX_SITES_ENABLED,
        "DOCKER_CONTAINER_IP": DOCKER_CONTAINER_IP,
        "DOCKER_CONTAINER_PORT": DOCKER_CONTAINER_PORT,
        "DEBUG": DEBUG,
        "HOST": HOST,
        "PORT": PORT
    }
    return jsonify(config=config)

@admin_api_bp.route('/config', methods=['PUT'])
@require_admin
def update_config():
    """Mettre à jour la configuration (écrit dans le .env)"""
    data = request.get_json()
    
    # Lire le fichier .env actuel
    env_path = '.env'
    if not os.path.exists(env_path):
        return jsonify(error="Fichier .env non trouvé"), 404
    
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    # Mapping des clés modifiables
    allowed_keys = [
        'DOMAIN', 'BASE_URL', 'SUBDOMAIN_BASE', 'ENABLE_SSH_MANAGEMENT',
        'SSH_HOST', 'SSH_PORT', 'SSH_USER', 'SSH_PASSWORD', 'SSH_KEY_PATH',
        'NGINX_SITES_AVAILABLE', 'NGINX_SITES_ENABLED',
        'DOCKER_CONTAINER_IP', 'DOCKER_CONTAINER_PORT',
        'DEBUG', 'HOST', 'PORT'
    ]
    
    # Mettre à jour les lignes
    new_lines = []
    updated_keys = set()
    
    for line in lines:
        if '=' in line and not line.strip().startswith('#'):
            key = line.split('=')[0].strip()
            if key in allowed_keys and key in data:
                new_lines.append(f"{key}={data[key]}\n")
                updated_keys.add(key)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    # Ajouter les nouvelles clés qui n'existaient pas
    for key in allowed_keys:
        if key in data and key not in updated_keys:
            new_lines.append(f"{key}={data[key]}\n")
    
    # Écrire le fichier
    with open(env_path, 'w') as f:
        f.writelines(new_lines)
    
    return jsonify(message="Configuration mise à jour. Redémarrez le serveur pour appliquer les changements.")

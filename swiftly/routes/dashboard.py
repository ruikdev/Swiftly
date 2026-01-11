"""Routes du dashboard web"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from swiftly.database import load_sites, get_user_sites, delete_site_from_db
from swiftly.utils.decorators import require_auth
from werkzeug.utils import secure_filename
import os
import shutil
from swiftly.config import SITES_FOLDER
from swiftly.database import sites, add_site_to_db

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

def require_web_auth(f):
    """Décorateur pour vérifier l'authentification web"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            flash('Vous devez être connecté pour accéder à cette page', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@dashboard_bp.route('/')
@require_web_auth
def home():
    """Page d'accueil du dashboard"""
    email = session.get('email')
    user_sites = get_user_sites(email)
    
    # Enrichir avec le nombre de fichiers
    for site_name, site_data in user_sites.items():
        if isinstance(site_data, dict) and "folder" in site_data:
            folder_path = os.path.abspath(os.path.join(SITES_FOLDER, site_data["folder"]))
            if os.path.exists(folder_path):
                file_count = sum([len(files) for _, _, files in os.walk(folder_path)])
                site_data["file_count"] = file_count
    
    return render_template('dashboard_home.html', sites=user_sites)

@dashboard_bp.route('/deploy', methods=['GET', 'POST'])
@require_web_auth
def deploy():
    """Page de déploiement de site"""
    if request.method == 'GET':
        return render_template('dashboard_deploy.html')
    
    # POST - Déployer le site
    email = session.get('email')
    name = request.form.get('name')
    
    if not name:
        return jsonify(error="Le champ 'name' est requis"), 400
    
    # Recharger les sites
    current_sites = load_sites()
    
    if name in current_sites:
        return jsonify(error=f"Le site '{name}' existe déjà"), 409
    
    if not request.files:
        return jsonify(error="Aucun fichier reçu"), 400
    
    # Créer le dossier du site
    site_folder_name = secure_filename(name)
    site_path = os.path.abspath(os.path.join(SITES_FOLDER, site_folder_name))
    
    if os.path.exists(site_path):
        shutil.rmtree(site_path)
    
    os.makedirs(site_path, exist_ok=True)
    
    files_list = request.files.getlist('files')
    has_index = False
    uploaded_files = []
    
    try:
        for file in files_list:
            if file.filename == '':
                continue
            
            relative_path = file.filename
            
            if relative_path == 'index.html' or relative_path.endswith('/index.html'):
                has_index = True
            
            safe_path = secure_filename(relative_path.replace('/', '_SEP_')).replace('_SEP_', '/')
            file_path = os.path.join(site_path, safe_path)
            
            file_dir = os.path.dirname(file_path)
            if file_dir:
                os.makedirs(file_dir, exist_ok=True)
            
            file.save(file_path)
            uploaded_files.append(relative_path)
        
        # Corriger les chemins absolus
        from swiftly.routes.sites import fix_absolute_paths_in_file
        fixed_files = []
        for root, dirs, files in os.walk(site_path):
            for file in files:
                file_full_path = os.path.join(root, file)
                if fix_absolute_paths_in_file(file_full_path, site_folder_name):
                    rel_path = os.path.relpath(file_full_path, site_path)
                    fixed_files.append(rel_path)
        
        if not has_index:
            shutil.rmtree(site_path)
            return jsonify(error="Le site doit contenir un fichier 'index.html' à la racine"), 400
        
        add_site_to_db(name, site_folder_name, email)
        
        response_data = {
            "message": f"Site '{name}' déployé avec succès",
            "url": f"/sites/{name}",
            "files_uploaded": len(uploaded_files)
        }
        
        if fixed_files:
            response_data["warning"] = "Chemins absolus convertis en chemins relatifs"
            response_data["fixed_files"] = fixed_files
        
        return jsonify(response_data), 201
    
    except Exception as e:
        if os.path.exists(site_path):
            shutil.rmtree(site_path)
        return jsonify(error=f"Erreur lors du déploiement: {str(e)}"), 500

@dashboard_bp.route('/delete/<site_name>', methods=['POST'])
@require_web_auth
def delete_site(site_name):
    """Supprimer un site"""
    email = session.get('email')
    current_sites = load_sites()
    
    if site_name not in current_sites:
        return jsonify(error=f"Le site '{site_name}' n'existe pas"), 404
    
    site_data = current_sites[site_name]
    
    if delete_site_from_db(site_name, email):
        try:
            if isinstance(site_data, dict) and "folder" in site_data:
                folder_path = os.path.abspath(os.path.join(SITES_FOLDER, site_data["folder"]))
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path)
        except Exception as e:
            print(f"Erreur lors de la suppression: {e}")
        
        return jsonify(message=f"Site '{site_name}' supprimé avec succès")
    
    return jsonify(error="Vous n'êtes pas le propriétaire de ce site"), 403

@dashboard_bp.route('/profile')
@require_web_auth
def profile():
    """Page de profil"""
    email = session.get('email')
    user_sites = get_user_sites(email)
    
    return render_template('dashboard_profile.html', 
                         email=email, 
                         site_count=len(user_sites))

@dashboard_bp.route('/profile/update-email', methods=['POST'])
@require_web_auth
def update_email():
    """Mettre à jour l'email"""
    from swiftly.database import update_user_email
    
    old_email = session.get('email')
    new_email = request.form.get('new_email')
    password = request.form.get('password')
    
    if not new_email or not password:
        flash('Tous les champs sont requis', 'error')
        return redirect(url_for('dashboard.profile'))
    
    if update_user_email(old_email, new_email, password):
        session['email'] = new_email
        flash('Email mis à jour avec succès', 'success')
    else:
        flash('Erreur: email déjà utilisé ou mot de passe incorrect', 'error')
    
    return redirect(url_for('dashboard.profile'))

@dashboard_bp.route('/profile/update-password', methods=['POST'])
@require_web_auth
def update_password():
    """Mettre à jour le mot de passe"""
    from swiftly.database import update_user_password
    
    email = session.get('email')
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    
    if not old_password or not new_password:
        flash('Tous les champs sont requis', 'error')
        return redirect(url_for('dashboard.profile'))
    
    if len(new_password) < 6:
        flash('Le mot de passe doit contenir au moins 6 caractères', 'error')
        return redirect(url_for('dashboard.profile'))
    
    if update_user_password(email, old_password, new_password):
        flash('Mot de passe mis à jour avec succès', 'success')
    else:
        flash('Ancien mot de passe incorrect', 'error')
    
    return redirect(url_for('dashboard.profile'))

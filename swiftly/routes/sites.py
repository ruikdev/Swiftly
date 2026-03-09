"""Routes pour les sites"""

from flask import Blueprint, jsonify, request, send_from_directory, abort
from werkzeug.utils import secure_filename
import os
import shutil
import re
from swiftly.database import sites, users, add_site_to_db, get_user_sites, delete_site_from_db
from swiftly.config import SITES_FOLDER
from swiftly.utils.decorators import require_auth

sites_bp = Blueprint('sites', __name__, url_prefix='/api/sites')

def detect_spa(file_list):
    """
    Détecter si les fichiers uploadés correspondent à une SPA (Single Page Application)
    Heuristiques :
    - Présence de index.html
    - Fichiers .js ou .css avec hash dans le nom (ex: main-ABC123.js)
    - Absence de fichiers de backend (.php, .py, .jsp, etc.)
    
    Retourne True si au moins 2 heuristiques sont satisfaites
    """
    has_index_html = False
    has_hashed_assets = False
    has_no_backend = True
    
    backend_extensions = {'.php', '.py', '.jsp', '.asp', '.aspx', '.rb', '.go', '.java'}
    
    for file_name in file_list:
        # Vérifier index.html
        if file_name == 'index.html' or file_name.endswith('/index.html'):
            has_index_html = True
        
        # Tester fichiers de backend
        if any(file_name.endswith(ext) for ext in backend_extensions):
            has_no_backend = False
        
        # Détecter les fichiers hashés (pattern: name-HASH.ext)
        # Exemple: main-6V5E6UC3.js, styles-5INURTSO.css
        if re.search(r'-[a-zA-Z0-9]{6,}\.(js|css)$', file_name):
            has_hashed_assets = True
    
    # Compter les heuristiques satisfaites
    spa_indicators = sum([
        has_index_html,
        has_hashed_assets,
        has_no_backend
    ])
    
    return spa_indicators >= 2

def fix_absolute_paths_in_file(file_path, site_name):
    """
    Remplace les chemins absolus du type /sites/*/... par des chemins relatifs
    dans les fichiers HTML, CSS et JS
    """
    if not file_path.endswith(('.html', '.css', '.js')):
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern pour détecter /sites/quelquechose/chemin
        pattern = r'/sites/[^/"\'\s]+/'
        
        # Vérifier si le pattern existe
        if re.search(pattern, content):
            # Remplacer tous les chemins absolus par des chemins relatifs
            # /sites/xyz/css/style.css -> css/style.css
            # /sites/xyz/js/app.js -> js/app.js
            new_content = re.sub(r'/sites/[^/"\'\s]+/', '', content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True  # Indique qu'une correction a été faite
    except Exception as e:
        print(f"Erreur lors de la correction de {file_path}: {e}")
    
    return False

@sites_bp.route('', methods=['GET'])
@require_auth
def list_sites_route(auth_email):
    """Retourner la liste des sites de l'utilisateur connecté"""
    user_sites = get_user_sites(auth_email)
    # Enrichir avec le nombre de fichiers pour chaque site
    for site_name, site_data in user_sites.items():
        if isinstance(site_data, dict) and "folder" in site_data:
            folder_path = os.path.join(SITES_FOLDER, site_data["folder"])
            if os.path.exists(folder_path):
                file_count = sum([len(files) for _, _, files in os.walk(folder_path)])
                site_data["file_count"] = file_count
    return jsonify(sites=user_sites)

@sites_bp.route('', methods=['POST'])
@require_auth
def create_site_route(auth_email):
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
    site_path = os.path.join(SITES_FOLDER, site_folder_name)
    
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
        
        # Corriger automatiquement les chemins absolus dans tous les fichiers
        fixed_files = []
        for root, dirs, files in os.walk(site_path):
            for file in files:
                file_full_path = os.path.join(root, file)
                if fix_absolute_paths_in_file(file_full_path, site_folder_name):
                    rel_path = os.path.relpath(file_full_path, site_path)
                    fixed_files.append(rel_path)
        
        # Validation: index.html obligatoire
        if not has_index:
            # Supprimer le dossier créé
            shutil.rmtree(site_path)
            return jsonify(
                error="Le site doit contenir un fichier 'index.html' à la racine",
                uploaded_files=uploaded_files
            ), 400
        
        # Détecter si c'est une SPA
        is_spa = detect_spa(uploaded_files)
        
        # Ajouter le site à la DB
        add_site_to_db(name, site_folder_name, auth_email, is_spa=is_spa)
        
        response_data = {
            "message": f"Site '{name}' déployé avec succès",
            "site": {name: {"folder": site_folder_name, "owner": auth_email}},
            "url": f"/sites/{name}",
            "files_uploaded": len(uploaded_files),
            "files": uploaded_files
        }
        
        # Ajouter un avertissement si des chemins ont été corrigés
        if fixed_files:
            response_data["warning"] = "Chemins absolus détectés et automatiquement convertis en chemins relatifs"
            response_data["fixed_files"] = fixed_files
        
        return jsonify(response_data), 201
    
    except Exception as e:
        # En cas d'erreur, nettoyer le dossier
        if os.path.exists(site_path):
            shutil.rmtree(site_path)
        return jsonify(error=f"Erreur lors du déploiement: {str(e)}"), 500

@sites_bp.route('/<site_name>', methods=['DELETE'])
@require_auth
def remove_site_route(auth_email, site_name):
    """Supprimer un site (uniquement si l'utilisateur en est le propriétaire)"""
    if site_name not in sites:
        return jsonify(error=f"Le site '{site_name}' n'existe pas"), 404
    
    site_data = sites[site_name]
    
    if delete_site_from_db(site_name, auth_email):
        # Supprimer le dossier ou fichier physique
        try:
            # Nouveau format: dossier
            if isinstance(site_data, dict) and "folder" in site_data:
                folder_path = os.path.join(SITES_FOLDER, site_data["folder"])
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path)
            # Ancien format: fichier unique
            elif isinstance(site_data, dict) and "filename" in site_data:
                filepath = os.path.join(SITES_FOLDER, site_data["filename"])
                if os.path.exists(filepath):
                    os.remove(filepath)
        except Exception as e:
            print(f"Erreur lors de la suppression: {e}")
        
        return jsonify(message=f"Site '{site_name}' supprimé avec succès")
    return jsonify(error=f"Le site '{site_name}' n'existe pas ou vous n'en êtes pas le propriétaire"), 404

@sites_bp.route('/<site_name>', methods=['PATCH'])
@require_auth
def update_site_route(auth_email, site_name):
    """Mettre à jour les propriétés d'un site (ex: is_spa)"""
    if site_name not in sites:
        return jsonify(error=f"Le site '{site_name}' n'existe pas"), 404
    
    site_data = sites[site_name]
    
    # Vérifier que l'utilisateur est propriétaire
    if site_data.get("owner") != auth_email:
        return jsonify(error="Vous n'êtes pas le propriétaire de ce site"), 403
    
    # Récupérer les données à mettre à jour
    data = request.get_json() or {}
    
    # Permettre de mettre à jour is_spa
    if "is_spa" in data:
        site_data["is_spa"] = bool(data["is_spa"])
        from swiftly.database import save_sites
        save_sites()
        return jsonify(message=f"Site '{site_name}' mis à jour", site={site_name: site_data}), 200
    
    return jsonify(error="Aucune propriété valide à mettre à jour"), 400

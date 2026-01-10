"""Routes pour les sites"""

from flask import Blueprint, jsonify, request, send_from_directory, abort
from werkzeug.utils import secure_filename
import os
import shutil
from swiftly.database import sites, users, add_site_to_db, get_user_sites, delete_site_from_db
from swiftly.config import SITES_FOLDER
from swiftly.utils.decorators import require_auth

sites_bp = Blueprint('sites', __name__, url_prefix='/api/sites')

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

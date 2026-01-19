"""Routes pour les sites"""

from flask import Blueprint, jsonify, request, send_from_directory, abort
from werkzeug.utils import secure_filename
import os
import shutil
import re
from swiftly.database import get_site_by_name, get_user_sites, add_site_to_db, delete_site_from_db
from swiftly.config import SITES_FOLDER, ENABLE_SSH_MANAGEMENT
from swiftly.utils.decorators import require_auth
from swiftly.utils.ssh_manager import setup_subdomain, remove_subdomain, get_dns_instructions

sites_bp = Blueprint('sites', __name__, url_prefix='/api/sites')

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
    from swiftly.config import SUBDOMAIN_BASE
    
    name = request.form.get('name')
    custom_domain = request.form.get('custom_domain', '').strip()
    
    # Générer le sous-domaine automatique
    auto_subdomain = f"{name}.{SUBDOMAIN_BASE}"
    
    # Validation du nom
    if not name:
        return jsonify(error="Le champ 'name' est requis"), 400
    
    # Vérifier si le site existe déjà
    if get_site_by_name(name):
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
        
        # Configurer le domaine custom si fourni
        dns_info_auto = get_dns_instructions(auto_subdomain, is_custom=False)
        dns_info_custom = None
        custom_domain_status = None
        
        if custom_domain:
            if ENABLE_SSH_MANAGEMENT:
                success, message = setup_subdomain(custom_domain, name)
                custom_domain_status = {"success": success, "message": message}
            dns_info_custom = get_dns_instructions(custom_domain, is_custom=True)
        
        # Ajouter le site à la DB
        success = add_site_to_db(
            name, 
            site_folder_name, 
            auth_email, 
            auto_subdomain=auto_subdomain,
            custom_domain=custom_domain if custom_domain else None
        )
        
        if not success:
            # Nettoyer en cas d'échec
            if os.path.exists(site_path):
                shutil.rmtree(site_path)
            if custom_domain and ENABLE_SSH_MANAGEMENT:
                remove_subdomain(custom_domain)
            return jsonify(error="Erreur lors de l'ajout du site à la base de données"), 500
        
        response_data = {
            "message": f"Site '{name}' déployé avec succès",
            "site": {
                "name": name,
                "folder": site_folder_name,
                "owner": auth_email,
                "auto_subdomain": auto_subdomain,
                "custom_domain": custom_domain if custom_domain else None
            },
            "urls": {
                "local": f"/sites/{name}/",
                "subdomain": f"https://{auto_subdomain}" if ENABLE_SSH_MANAGEMENT else f"http://{auto_subdomain}",
                "custom": f"https://{custom_domain}" if custom_domain else None
            },
            "files_uploaded": len(uploaded_files),
            "files": uploaded_files
        }
        
        # Ajouter les informations DNS pour le sous-domaine auto
        response_data["auto_subdomain_info"] = dns_info_auto
        
        # Ajouter les informations DNS pour le domaine custom
        if dns_info_custom:
            response_data["custom_domain_info"] = dns_info_custom
        
        # Ajouter le statut du domaine custom
        if custom_domain_status:
            response_data["custom_domain_setup"] = custom_domain_status
        
        # Ajouter un avertissement si des fichiers ont été corrigés
        if fixed_files:
            response_data["warning"] = "Chemins absolus détectés et automatiquement convertis en chemins relatifs"
            response_data["fixed_files"] = fixed_files
        
        return jsonify(response_data), 201
    
    except Exception as e:
        # En cas d'erreur, nettoyer le dossier et la config nginx
        if os.path.exists(site_path):
            shutil.rmtree(site_path)
        if custom_domain and ENABLE_SSH_MANAGEMENT:
            remove_subdomain(custom_domain)
        return jsonify(error=f"Erreur lors du déploiement: {str(e)}"), 500

@sites_bp.route('/<site_name>', methods=['DELETE'])
@require_auth
def delete_site_route(auth_email, site_name):
    """Supprimer un site (seulement si l'utilisateur en est le propriétaire)"""
    site = get_site_by_name(site_name)
    
    if not site:
        return jsonify(error=f"Le site '{site_name}' n'existe pas"), 404
    
    # Supprimer le domaine custom si configuré
    if site.get('custom_domain') and ENABLE_SSH_MANAGEMENT:
        remove_subdomain(site['custom_domain'])
    
    # Supprimer de la base de données
    if delete_site_from_db(site_name, auth_email):
        # Supprimer le dossier physique
        try:
            folder_path = os.path.join(SITES_FOLDER, site['folder'])
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
        except Exception as e:
            print(f"Erreur lors de la suppression: {e}")
        
        return jsonify(message=f"Site '{site_name}' supprimé avec succès")
    
    return jsonify(error=f"Le site '{site_name}' n'existe pas ou vous n'en êtes pas le propriétaire"), 404

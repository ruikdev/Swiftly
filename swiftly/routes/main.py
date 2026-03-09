"""Routes principales"""

from flask import Blueprint, render_template, jsonify, request, send_from_directory, abort
import os
from swiftly.config import SITES_FOLDER
from swiftly.database import load_sites
from swiftly.analytics import track_visit

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Page d'accueil"""
    return render_template('base.html')

@main_bp.route('/health')
def health():
    """Endpoint de santé"""
    return jsonify(status="ok")

@main_bp.route('/sites/<site_name>')
@main_bp.route('/sites/<site_name>/')
@main_bp.route('/sites/<site_name>/<path:subpath>')
def serve_site(site_name, subpath=None):
    """Servir les fichiers d'un site depuis son dossier dédié"""
    # Recharger les sites depuis la DB pour avoir les données à jour
    sites = load_sites()
    
    # Vérifier si le site existe dans la DB
    if site_name not in sites:
        abort(404, description=f"Le site '{site_name}' n'existe pas")

    site_data = sites[site_name]
    
    # Nouveau format: dossier dédié
    if isinstance(site_data, dict) and "folder" in site_data:
        folder = site_data["folder"]
        site_folder = os.path.abspath(os.path.join(SITES_FOLDER, folder))
        is_spa = site_data.get("is_spa", False)
        
        # Si pas de sous-chemin, rediriger vers la version avec slash si nécessaire
        if not subpath:
            # Vérifier si l'URL se termine par un slash
            if not request.path.endswith('/'):
                from flask import redirect
                return redirect(request.path + '/', code=301)
            
            index_path = os.path.join(site_folder, "index.html")
            if os.path.exists(index_path):
                # Tracker la visite (uniquement pour index.html)
                track_visit(site_name)
                return send_from_directory(site_folder, "index.html")
            else:
                abort(404, description=f"index.html introuvable pour le site '{site_name}'")
        
        # Servir le fichier demandé
        file_path = os.path.join(site_folder, subpath)
        
        # Sécurité: vérifier qu'on ne sort pas du dossier du site
        real_site_folder = os.path.realpath(site_folder)
        real_file_path = os.path.realpath(file_path)
        
        if not real_file_path.startswith(real_site_folder):
            abort(403, description="Accès refusé")
        
        # Pour les SPAs : si le fichier n'existe pas, servir index.html
        if is_spa:
            if os.path.exists(file_path) and os.path.isfile(file_path):
                return send_from_directory(site_folder, subpath)
            else:
                # Servir index.html pour que Angular Router prenne le relais
                index_path = os.path.join(site_folder, "index.html")
                if os.path.exists(index_path):
                    return send_from_directory(site_folder, "index.html")
                abort(404, description=f"index.html introuvable pour la SPA '{site_name}'")
        else:
            # Pour les sites statiques classiques : erreur 404 si fichier absent
            if os.path.exists(file_path) and os.path.isfile(file_path):
                return send_from_directory(site_folder, subpath)
            else:
                abort(404, description=f"Fichier '{subpath}' introuvable")
    
    # Support ancien format (fichier unique) pour compatibilité
    elif isinstance(site_data, dict) and "filename" in site_data:
        filename = site_data.get("filename")
        filepath = os.path.join(SITES_FOLDER, filename)
        if os.path.exists(filepath):
            return send_from_directory(SITES_FOLDER, filename)
        abort(404, description=f"Le fichier '{filename}' n'existe pas")
    
    abort(404, description=f"Configuration invalide pour le site '{site_name}'")

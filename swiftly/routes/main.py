"""Routes principales"""

from flask import Blueprint, render_template, jsonify, request, send_from_directory, abort, session, redirect
import os
from swiftly.config import SITES_FOLDER
from swiftly.database import get_site_by_name, verify_site_password
from swiftly.analytics import track_visit

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Page d'accueil ou site sur sous-domaine"""
    from swiftly.config import SUBDOMAIN_BASE
    
    # Détecter si on est sur un sous-domaine
    host = request.host.split(':')[0]  # Enlever le port
    
    if SUBDOMAIN_BASE and host.endswith(f'.{SUBDOMAIN_BASE}'):
        # Extraire le nom du site depuis le sous-domaine
        site_name = host.replace(f'.{SUBDOMAIN_BASE}', '')
        
        # Servir le site depuis le sous-domaine
        return serve_site(site_name, subpath=None)
    
    # Sinon, page d'accueil normale
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
    # Récupérer les informations du site
    site = get_site_by_name(site_name)
    
    # Vérifier si le site existe
    if not site:
        abort(404, description=f"Le site '{site_name}' n'existe pas")
    
    folder = site['folder']
    site_folder = os.path.abspath(os.path.join(SITES_FOLDER, folder))
    
    # Si pas de sous-chemin, servir index.html
    if not subpath:
        # Vérifier si l'URL se termine par un slash
        if not request.path.endswith('/'):
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
    if os.path.exists(file_path) and os.path.isfile(file_path):
        # Sécurité: vérifier qu'on ne sort pas du dossier du site
        real_site_folder = os.path.realpath(site_folder)
        real_file_path = os.path.realpath(file_path)
        if real_file_path.startswith(real_site_folder):
            return send_from_directory(site_folder, subpath)
    
    abort(404, description=f"Fichier '{subpath}' introuvable")

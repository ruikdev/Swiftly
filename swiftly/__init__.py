"""Factory Flask et initialisation de l'application"""

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from swiftly.config import DEBUG, HOST, PORT, SITES_FOLDER, SECRET_KEY
from swiftly.database import init_db
import os

# Chemin racine du projet (parent du package swiftly)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def create_app():
    """Factory pour créer et configurer l'application Flask"""
    app = Flask(
        __name__,
        template_folder=os.path.join(ROOT_DIR, 'templates'),
        static_folder=os.path.join(ROOT_DIR, 'static')
    )
    
    # Configuration des sessions
    app.secret_key = os.environ.get('SECRET_KEY', SECRET_KEY)
    # Secure cookies en production (HTTPS), False en dev
    app.config['SESSION_COOKIE_SECURE'] = not DEBUG
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    # SameSite=None requis pour cookies cross-site/sous-domaines avec Secure
    app.config['SESSION_COOKIE_SAMESITE'] = 'None' if not DEBUG else 'Lax'
    
    # Partager les cookies entre le domaine principal et les sous-domaines
    from swiftly.config import SUBDOMAIN_BASE
    if SUBDOMAIN_BASE and '.' in SUBDOMAIN_BASE:
        # Utiliser .swiftly.ruikdev.me pour partager avec tous les sous-domaines
        app.config['SESSION_COOKIE_DOMAIN'] = f'.{SUBDOMAIN_BASE}'
    
    # ProxyFix pour faire confiance aux en-têtes X-Forwarded-* du reverse proxy
    # x_for=1, x_proto=1, x_host=1 si 1 seul proxy (Nginx)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    
    # Initialiser les bases de données
    init_db()
    
    # Créer les dossiers nécessaires
    os.makedirs(os.path.join(ROOT_DIR, "db"), exist_ok=True)
    os.makedirs(os.path.join(ROOT_DIR, SITES_FOLDER), exist_ok=True)
    
    # Enregistrer les blueprints API
    from swiftly.routes.main import main_bp
    from swiftly.routes.auth import auth_bp, auth_web_bp
    from swiftly.routes.user import user_bp
    from swiftly.routes.sites import sites_bp
    from swiftly.routes.dashboard import dashboard_bp
    from swiftly.routes.admin import admin_bp, admin_api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)  # API
    app.register_blueprint(auth_web_bp)  # Web
    app.register_blueprint(user_bp)
    app.register_blueprint(sites_bp)
    app.register_blueprint(dashboard_bp)  # Dashboard
    app.register_blueprint(admin_bp)  # Admin Web
    app.register_blueprint(admin_api_bp)  # Admin API
    
    return app

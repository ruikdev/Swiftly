"""Factory Flask et initialisation de l'application"""

from flask import Flask
from swiftly.config import DEBUG, HOST, PORT, SITES_FOLDER
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
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SESSION_COOKIE_SECURE'] = False  # True en production avec HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
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
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)  # API
    app.register_blueprint(auth_web_bp)  # Web
    app.register_blueprint(user_bp)
    app.register_blueprint(sites_bp)
    app.register_blueprint(dashboard_bp)  # Dashboard
    
    return app

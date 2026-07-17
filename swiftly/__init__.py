"""Factory Flask et initialisation de l'application"""

from flask import Flask, render_template
from swiftly.config import DEBUG, HOST, PORT, SITES_FOLDER
from swiftly.database import init_db
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Chemin racine du projet (parent du package swiftly)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Stockage de sessions en mémoire
user_sessions = {}

def create_app():
    """Factory pour créer et configurer l'application Flask"""
    app = Flask(
        __name__,
        template_folder=os.path.join(ROOT_DIR, 'templates'),
        static_folder=os.path.join(ROOT_DIR, 'static')
    )
    
    # Configuration simple des sessions
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
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

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404
    
    return app

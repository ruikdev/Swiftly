"""Factory Flask et initialisation de l'application"""

from flask import Flask
from swiftly.config import DEBUG, HOST, PORT, SITES_FOLDER
from swiftly.database import init_db
import os

def create_app():
    """Factory pour créer et configurer l'application Flask"""
    app = Flask(__name__)
    
    # Initialiser les bases de données
    init_db()
    
    # Créer les dossiers nécessaires
    os.makedirs("db", exist_ok=True)
    os.makedirs(SITES_FOLDER, exist_ok=True)
    
    # Enregistrer les blueprints
    from swiftly.routes.main import main_bp
    from swiftly.routes.auth import auth_bp
    from swiftly.routes.user import user_bp
    from swiftly.routes.sites import sites_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(sites_bp)
    
    return app

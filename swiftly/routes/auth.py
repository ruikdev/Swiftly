"""Routes d'authentification"""

from flask import Blueprint, jsonify, request
from swiftly.database import (
    create_user, verify_user, update_user_email, 
    update_user_password, users
)
from swiftly.utils.decorators import require_auth

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Créer un nouveau compte utilisateur"""
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify(error="Email et mot de passe requis"), 400
    
    email = data['email']
    password = data['password']
    
    if len(password) < 6:
        return jsonify(error="Le mot de passe doit contenir au moins 6 caractères"), 400
    
    if create_user(email, password):
        return jsonify(message=f"Compte créé avec succès pour {email}"), 201
    else:
        return jsonify(error=f"Un compte avec l'email {email} existe déjà"), 409

@auth_bp.route('/login', methods=['POST'])
def login():
    """Vérifier les identifiants de connexion"""
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify(error="Email et mot de passe requis"), 400
    
    email = data['email']
    password = data['password']
    
    if verify_user(email, password):
        return jsonify(message="Connexion réussie", email=email), 200
    else:
        return jsonify(error="Email ou mot de passe incorrect"), 401

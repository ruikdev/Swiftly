"""Routes utilisateur"""

from flask import Blueprint, jsonify, request
from swiftly.database import users, update_user_email, update_user_password, get_user_sites
from swiftly.utils.decorators import require_auth

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile(auth_email):
    """Obtenir le profil de l'utilisateur connecté"""
    user_data = users.get(auth_email, {})
    return jsonify(
        email=auth_email,
        sites=user_data.get("sites", []),
        total_sites=len(user_data.get("sites", []))
    ), 200

@user_bp.route('/update-email', methods=['PUT'])
@require_auth
def update_email_route(auth_email):
    """Mettre à jour l'email de l'utilisateur"""
    data = request.get_json()
    
    if not data or 'new_email' not in data or 'password' not in data:
        return jsonify(error="Nouvel email et mot de passe requis"), 400
    
    new_email = data['new_email']
    password = data['password']
    
    if update_user_email(auth_email, new_email, password):
        return jsonify(message=f"Email mis à jour avec succès. Nouvel email: {new_email}"), 200
    else:
        return jsonify(error="Impossible de mettre à jour l'email. Vérifiez que le mot de passe est correct et que le nouvel email n'est pas déjà utilisé"), 400

@user_bp.route('/update-password', methods=['PUT'])
@require_auth
def update_password_route(auth_email):
    """Mettre à jour le mot de passe de l'utilisateur"""
    data = request.get_json()
    
    if not data or 'old_password' not in data or 'new_password' not in data:
        return jsonify(error="Ancien et nouveau mot de passe requis"), 400
    
    old_password = data['old_password']
    new_password = data['new_password']
    
    if len(new_password) < 6:
        return jsonify(error="Le nouveau mot de passe doit contenir au moins 6 caractères"), 400
    
    if update_user_password(auth_email, old_password, new_password):
        return jsonify(message="Mot de passe mis à jour avec succès"), 200
    else:
        return jsonify(error="Ancien mot de passe incorrect"), 400

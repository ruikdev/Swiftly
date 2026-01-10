"""Décorateurs personnalisés"""

from flask import request, jsonify
from functools import wraps
from swiftly.database import verify_user

def require_auth(f):
    """Décorateur pour protéger les routes nécessitant une authentification"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_email = request.headers.get('X-User-Email')
        auth_password = request.headers.get('X-User-Password')
        
        if not auth_email or not auth_password:
            return jsonify(error="Authentification requise. Utilisez les headers 'X-User-Email' et 'X-User-Password'"), 401
        
        if not verify_user(auth_email, auth_password):
            return jsonify(error="Email ou mot de passe incorrect"), 401
        
        # Passer l'email à la fonction
        return f(auth_email, *args, **kwargs)
    return decorated_function

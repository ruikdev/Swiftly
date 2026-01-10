"""Modèle utilisateur"""

import hashlib

class User:
    """Classe représentant un utilisateur"""
    
    @staticmethod
    def hash_password(password):
        """Hasher un mot de passe avec SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def create_user_dict(email, password):
        """Créer un dictionnaire utilisateur"""
        return {
            "password": User.hash_password(password),
            "sites": []
        }
    
    @staticmethod
    def verify_password(stored_hash, password):
        """Vérifier un mot de passe"""
        return stored_hash == User.hash_password(password)

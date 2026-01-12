"""Modèle utilisateur"""

import bcrypt

class User:
    """Classe représentant un utilisateur"""
    
    @staticmethod
    def hash_password(password):
        """Hasher un mot de passe avec bcrypt"""
        # Convertir la chaîne en bytes et générer le hash
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
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
        # bcrypt compare automatiquement le hash stocké avec le mot de passe fourni
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))

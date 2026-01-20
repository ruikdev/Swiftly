"""Gestion de la base de données"""

import json
import os
from swiftly.config import DB_SITES, DB_USERS
from swiftly.models.user import User
from swiftly.models.site import Site

# Données en mémoire
users = {}
sites = {}

def init_db():
    """Initialiser les bases de données"""
    global users, sites
    users = load_users()
    sites = load_sites()

def load_users():
    """Charger les utilisateurs depuis le fichier JSON"""
    if os.path.exists(DB_USERS):
        try:
            with open(DB_USERS, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_users():
    """Sauvegarder les utilisateurs"""
    try:
        os.makedirs("db", exist_ok=True)
        with open(DB_USERS, 'w') as f:
            json.dump(users, f, indent=4)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des utilisateurs : {e}")

def load_sites():
    """Charger les sites depuis le fichier JSON"""
    if os.path.exists(DB_SITES):
        try:
            with open(DB_SITES, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_sites():
    """Sauvegarder les sites"""
    try:
        os.makedirs("db", exist_ok=True)
        with open(DB_SITES, 'w') as f:
            json.dump(sites, f, indent=4)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des sites : {e}")

# ========== Gestion des utilisateurs ==========

def create_user(email, password):
    """Créer un nouvel utilisateur"""
    if email in users:
        return False
    users[email] = User.create_user_dict(email, password)
    save_users()
    return True

def verify_user(email, password):
    """Vérifier les identifiants d'un utilisateur"""
    if email not in users:
        return False
    return User.verify_password(users[email]["password"], password)

def update_user_email(old_email, new_email, password):
    """Mettre à jour l'email d'un utilisateur"""
    if old_email not in users or new_email in users:
        return False
    if not verify_user(old_email, password):
        return False
    users[new_email] = users.pop(old_email)
    # Mettre à jour les sites liés à cet utilisateur
    for site_name, site_data in sites.items():
        if site_data.get("owner") == old_email:
            site_data["owner"] = new_email
    save_users()
    save_sites()
    return True

def update_user_password(email, old_password, new_password):
    """Mettre à jour le mot de passe d'un utilisateur"""
    if not verify_user(email, old_password):
        return False
    users[email]["password"] = User.hash_password(new_password)
    save_users()
    return True

# ========== Gestion des sites ==========

def add_site_to_db(name, folder, owner):
    """Ajouter un site à la base de données"""
    sites[name] = Site.create_site_dict(folder, owner)
    if owner in users:
        if name not in users[owner]["sites"]:
            users[owner]["sites"].append(name)
        save_users()
    save_sites()
    return True

def get_user_sites(email):
    """Retourner uniquement les sites d'un utilisateur"""
    user_sites = {}
    for name, data in sites.items():
        if isinstance(data, dict) and data.get("owner") == email:
            user_sites[name] = data
    return user_sites

def delete_site_from_db(name, owner=None):
    """Supprimer un site de la base de données"""
    if name in sites:
        # Vérifier si l'utilisateur est le propriétaire
        if owner and sites[name].get("owner") != owner:
            return False
        
        # Retirer le site de la liste de l'utilisateur
        site_owner = sites[name].get("owner")
        if site_owner and site_owner in users:
            if name in users[site_owner]["sites"]:
                users[site_owner]["sites"].remove(name)
            save_users()
        
        del sites[name]
        save_sites()
        return True
    return False

def hash_password(password):
    """Hasher un mot de passe (fonction utilitaire)"""
    return User.hash_password(password)

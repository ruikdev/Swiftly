"""Gestion de la base de données SQLite"""

import sqlite3
import os
from contextlib import contextmanager
from swiftly.config import DATABASE_PATH
from swiftly.models.user import User

@contextmanager
def get_db_connection():
    """Context manager pour les connexions à la base de données"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Initialiser la base de données et créer les tables"""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Table des utilisateurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des sites
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                folder TEXT NOT NULL,
                owner_id INTEGER NOT NULL,
                auto_subdomain TEXT,
                custom_domain TEXT,
                has_password_protection BOOLEAN DEFAULT 0,
                protection_password TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Table des données analytics pour les sites
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS site_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_id INTEGER NOT NULL,
                visit_date DATE NOT NULL,
                visits INTEGER DEFAULT 0,
                FOREIGN KEY (site_id) REFERENCES sites (id) ON DELETE CASCADE,
                UNIQUE(site_id, visit_date)
            )
        ''')
        
        # Créer un utilisateur admin par défaut seulement si aucun admin n'existe
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1')
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            # Aucun admin n'existe, créer le compte par défaut
            hashed_password = User.hash_password('admin')
            cursor.execute(
                'INSERT INTO users (email, password, is_admin) VALUES (?, ?, ?)',
                ('admin@admin', hashed_password, 1)
            )
            print("✓ Utilisateur admin créé (admin@admin / admin)")

# ========== Gestion des utilisateurs ==========

def create_user(email, password, is_admin=False):
    """Créer un nouvel utilisateur"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            hashed_password = User.hash_password(password)
            cursor.execute(
                'INSERT INTO users (email, password, is_admin) VALUES (?, ?, ?)',
                (email, hashed_password, is_admin)
            )
            return True
    except sqlite3.IntegrityError:
        return False

def get_user_by_email(email):
    """Récupérer un utilisateur par son email"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def verify_user(email, password):
    """Vérifier les identifiants d'un utilisateur"""
    user = get_user_by_email(email)
    if not user:
        return False
    return User.verify_password(user['password'], password)

def update_user_email(old_email, new_email, password):
    """Mettre à jour l'email d'un utilisateur"""
    if not verify_user(old_email, password):
        return False
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET email = ? WHERE email = ?',
                (new_email, old_email)
            )
            return cursor.rowcount > 0
    except sqlite3.IntegrityError:
        return False

def update_user_password(email, old_password, new_password):
    """Mettre à jour le mot de passe d'un utilisateur"""
    if not verify_user(email, old_password):
        return False
    
    hashed_password = User.hash_password(new_password)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET password = ? WHERE email = ?',
            (hashed_password, email)
        )
        return cursor.rowcount > 0

def delete_user(email):
    """Supprimer un utilisateur (et ses sites grâce au CASCADE)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE email = ?', (email,))
        return cursor.rowcount > 0

def get_all_users():
    """Récupérer tous les utilisateurs"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, email, is_admin, created_at FROM users')
        return [dict(row) for row in cursor.fetchall()]

def set_user_admin_status(email, is_admin):
    """Changer le statut admin d'un utilisateur"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET is_admin = ? WHERE email = ?',
            (1 if is_admin else 0, email)
        )
        return cursor.rowcount > 0

def admin_update_password(email, new_password):
    """Admin : modifier le mot de passe d'un utilisateur"""
    hashed_password = User.hash_password(new_password)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET password = ? WHERE email = ?',
            (hashed_password, email)
        )
        return cursor.rowcount > 0

# ========== Gestion des sites ==========

def add_site_to_db(name, folder, owner_email, auto_subdomain=None, custom_domain=None, has_password_protection=False, protection_password=None):
    """Ajouter un site à la base de données"""
    user = get_user_by_email(owner_email)
    if not user:
        return False
    
    # Hasher le mot de passe de protection si fourni
    hashed_protection = None
    if has_password_protection and protection_password:
        hashed_protection = User.hash_password(protection_password)
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO sites (name, folder, owner_id, auto_subdomain, custom_domain, has_password_protection, protection_password) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (name, folder, user['id'], auto_subdomain, custom_domain, 1 if has_password_protection else 0, hashed_protection)
            )
            return True
    except sqlite3.IntegrityError:
        return False

def get_site_by_name(name):
    """Récupérer un site par son nom"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.*, u.email as owner_email 
            FROM sites s 
            JOIN users u ON s.owner_id = u.id 
            WHERE s.name = ?
        ''', (name,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def get_user_sites(email):
    """Retourner uniquement les sites d'un utilisateur"""
    user = get_user_by_email(email)
    if not user:
        return {}
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM sites WHERE owner_id = ?',
            (user['id'],)
        )
        sites = {}
        for row in cursor.fetchall():
            site_dict = dict(row)
            name = site_dict['name']
            sites[name] = {
                'folder': site_dict['folder'],
                'owner': email,
                'auto_subdomain': site_dict['auto_subdomain'],
                'custom_domain': site_dict['custom_domain'],
                'has_password_protection': bool(site_dict['has_password_protection']),
                'created_at': site_dict['created_at']
            }
        return sites

def get_all_sites():
    """Récupérer tous les sites (pour admin)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.*, u.email as owner_email 
            FROM sites s 
            JOIN users u ON s.owner_id = u.id
        ''')
        return [dict(row) for row in cursor.fetchall()]

def delete_site_from_db(name, owner_email=None):
    """Supprimer un site de la base de données"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if owner_email:
            # Vérifier que l'utilisateur est le propriétaire
            user = get_user_by_email(owner_email)
            if not user:
                return False
            cursor.execute(
                'DELETE FROM sites WHERE name = ? AND owner_id = ?',
                (name, user['id'])
            )
        else:
            # Admin peut supprimer n'importe quel site
            cursor.execute('DELETE FROM sites WHERE name = ?', (name,))
        
        return cursor.rowcount > 0

def verify_site_password(site_name, password):
    """Vérifier le mot de passe de protection d'un site"""
    site = get_site_by_name(site_name)
    if not site or not site['has_password_protection']:
        return True  # Pas de protection
    
    if not site['protection_password']:
        return True
    
    return User.verify_password(site['protection_password'], password)

def hash_password(password):
    """Hasher un mot de passe (fonction utilitaire)"""
    return User.hash_password(password)

"""Routes d'authentification"""

from flask import Blueprint, jsonify, request, render_template, redirect, url_for, session, flash, make_response
from swiftly.database import (
    create_user, verify_user, update_user_email, 
    update_user_password, users
)
from swiftly.utils.decorators import require_auth
import secrets
import time

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
auth_web_bp = Blueprint('auth_web', __name__, url_prefix='/auth')

# Stockage des sessions utilisateur en mémoire
active_sessions = {}

def create_session_token(email):
    """Créer un token de session pour un utilisateur"""
    token = secrets.token_urlsafe(32)
    active_sessions[token] = {
        'email': email,
        'created_at': time.time()
    }
    return token

def get_email_from_token(token):
    """Récupérer l'email depuis un token"""
    if token in active_sessions:
        session_data = active_sessions[token]
        # Vérifier si la session n'est pas expirée (1 heure)
        if time.time() - session_data['created_at'] < 3600:
            return session_data['email']
        else:
            # Session expirée, la supprimer
            del active_sessions[token]
    return None

def delete_session_token(token):
    """Supprimer un token de session"""
    if token in active_sessions:
        del active_sessions[token]

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

# ========== Routes Web ==========

@auth_web_bp.route('/', methods=['GET', 'POST'])
@auth_web_bp.route('/login', methods=['GET', 'POST'])
def web_login():
    """Page de connexion web (seule page unifiée)"""
    if request.method == 'GET':
        # Vérifier si déjà connecté via cookie
        token = request.cookies.get('session_token')
        if token and get_email_from_token(token):
            return redirect(url_for('dashboard.home'))
        return render_template('auth.html')
    
    email = request.form.get('email')
    password = request.form.get('password')
    
    print(f"[LOGIN POST] Attempting login for: {email}")
    
    if not email or not password:
        flash('Email et mot de passe requis', 'error')
        return redirect(url_for('auth_web.web_login'))
    
    if verify_user(email, password):
        print(f"[LOGIN POST] Verification successful for: {email}")
        # Créer un token de session
        token = create_session_token(email)
        print(f"[LOGIN POST] Created session token: {token[:10]}... for {email}")
        
        flash('Connexion réussie !', 'success')
        response = make_response(redirect(url_for('dashboard.home')))
        # Définir le cookie avec le token
        response.set_cookie('session_token', token, max_age=3600, httponly=True)
        return response
    else:
        print(f"[LOGIN POST] Verification failed for: {email}")
        flash('Email ou mot de passe incorrect', 'error')
        return redirect(url_for('auth_web.web_login'))

@auth_web_bp.route('/register', methods=['POST'])
def web_register():
    """Gestion d'inscription (sur la même page)"""
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not email or not password:
        flash('Email et mot de passe requis', 'error')
        return redirect(url_for('auth_web.web_login'))
    
    if len(password) < 6:
        flash('Le mot de passe doit contenir au moins 6 caractères', 'error')
        return redirect(url_for('auth_web.web_login'))
    
    if create_user(email, password):
        # Créer un token de session
        token = create_session_token(email)
        flash('Compte créé avec succès !', 'success')
        response = make_response(redirect(url_for('dashboard.home')))
        response.set_cookie('session_token', token, max_age=3600, httponly=True)
        return response
    else:
        flash('Un compte avec cet email existe déjà', 'error')
        return redirect(url_for('auth_web.web_login'))

@auth_web_bp.route('/logout')
def logout():
    """Déconnexion"""
    token = request.cookies.get('session_token')
    if token:
        delete_session_token(token)
    flash('Déconnexion réussie', 'success')
    response = make_response(redirect(url_for('main.index')))
    response.set_cookie('session_token', '', expires=0)
    return response

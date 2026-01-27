"""Routes d'authentification"""

from flask import Blueprint, jsonify, request, render_template, redirect, url_for, session, flash, make_response
from swiftly.database import (
    create_user, verify_user, update_user_email, 
    update_user_password, users, verify_user_account,
    is_user_verified, reset_user_password
)
from swiftly.utils.decorators import require_auth
from swiftly.utils.email_service import (
    send_verification_email, verify_code,
    send_password_reset_email, verify_password_reset_code
)
import secrets
import time

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
auth_web_bp = Blueprint('auth_web', __name__, url_prefix='/auth')

# Stockage des sessions utilisateur en mémoire
active_sessions = {}
# Stockage temporaire des utilisateurs non vérifiés
pending_users = {}

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
    
    if email in users:
        return jsonify(error=f"Un compte avec l'email {email} existe déjà"), 409
    
    # Stocker temporairement les infos utilisateur
    pending_users[email] = password
    
    # Envoyer l'email de vérification
    if send_verification_email(email):
        return jsonify(message=f"Code de vérification envoyé à {email}"), 201
    else:
        return jsonify(error="Erreur lors de l'envoi de l'email"), 500

@auth_bp.route('/verify', methods=['POST'])
def verify():
    """Vérifier le code de vérification"""
    data = request.get_json()
    
    if not data or 'email' not in data or 'code' not in data:
        return jsonify(error="Email et code requis"), 400
    
    email = data['email']
    code = data['code']
    
    if email not in pending_users:
        return jsonify(error="Aucune inscription en attente pour cet email"), 400
    
    if verify_code(email, code):
        # Créer le compte utilisateur vérifié
        password = pending_users.pop(email)
        create_user(email, password, verified=True)
        return jsonify(message="Compte vérifié et créé avec succès"), 200
    else:
        return jsonify(error="Code invalide ou expiré"), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    """Vérifier les identifiants de connexion"""
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify(error="Email et mot de passe requis"), 400
    
    email = data['email']
    password = data['password']
    
    if verify_user(email, password):
        if not is_user_verified(email):
            return jsonify(error="Compte non vérifié. Vérifiez vos emails."), 403
        return jsonify(message="Connexion réussie", email=email), 200
    else:
        return jsonify(error="Email ou mot de passe incorrect"), 401

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Envoyer un code de réinitialisation de mot de passe"""
    data = request.get_json()
    
    if not data or 'email' not in data:
        return jsonify(error="Email requis"), 400
    
    email = data['email']
    
    if email not in users:
        return jsonify(error="Aucun compte trouvé avec cet email"), 404
    
    if send_password_reset_email(email):
        return jsonify(message=f"Code de réinitialisation envoyé à {email}"), 200
    else:
        return jsonify(error="Erreur lors de l'envoi de l'email"), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Réinitialiser le mot de passe avec le code"""
    data = request.get_json()
    
    if not data or 'email' not in data or 'code' not in data or 'new_password' not in data:
        return jsonify(error="Email, code et nouveau mot de passe requis"), 400
    
    email = data['email']
    code = data['code']
    new_password = data['new_password']
    
    if len(new_password) < 6:
        return jsonify(error="Le mot de passe doit contenir au moins 6 caractères"), 400
    
    if verify_password_reset_code(email, code):
        if reset_user_password(email, new_password):
            return jsonify(message="Mot de passe réinitialisé avec succès"), 200
        else:
            return jsonify(error="Erreur lors de la réinitialisation"), 500
    else:
        return jsonify(error="Code invalide ou expiré"), 400

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
        if not is_user_verified(email):
            flash('Compte non vérifié. Vérifiez vos emails.', 'error')
            return redirect(url_for('auth_web.web_login'))
        
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
    
    if email in users:
        flash('Un compte avec cet email existe déjà', 'error')
        return redirect(url_for('auth_web.web_login'))
    
    # Stocker temporairement les infos utilisateur
    pending_users[email] = password
    
    # Envoyer l'email de vérification
    if send_verification_email(email):
        flash(f'Code de vérification envoyé à {email}', 'success')
        return redirect(url_for('auth_web.verify_page', email=email))
    else:
        flash('Erreur lors de l\'envoi de l\'email', 'error')
        return redirect(url_for('auth_web.web_login'))

@auth_web_bp.route('/verify', methods=['GET', 'POST'])
def verify_page():
    """Page de vérification du code"""
    if request.method == 'GET':
        email = request.args.get('email')
        if not email:
            return redirect(url_for('auth_web.web_login'))
        return render_template('verify.html', email=email)
    
    email = request.form.get('email')
    code = request.form.get('code')
    
    if not email or not code:
        flash('Email et code requis', 'error')
        return redirect(url_for('auth_web.verify_page', email=email))
    
    if email not in pending_users:
        flash('Aucune inscription en attente pour cet email', 'error')
        return redirect(url_for('auth_web.web_login'))
    
    if verify_code(email, code):
        # Créer le compte utilisateur vérifié
        password = pending_users.pop(email)
        create_user(email, password, verified=True)
        
        # Créer une session
        token = create_session_token(email)
        flash('Compte vérifié et créé avec succès !', 'success')
        response = make_response(redirect(url_for('dashboard.home')))
        response.set_cookie('session_token', token, max_age=3600, httponly=True)
        return response
    else:
        flash('Code invalide ou expiré', 'error')
        return redirect(url_for('auth_web.verify_page', email=email))

@auth_web_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password_page():
    """Page de demande de réinitialisation de mot de passe"""
    if request.method == 'GET':
        return render_template('forgot_password.html')
    
    email = request.form.get('email')
    
    if not email:
        flash('Email requis', 'error')
        return redirect(url_for('auth_web.forgot_password_page'))
    
    if email not in users:
        flash('Aucun compte trouvé avec cet email', 'error')
        return redirect(url_for('auth_web.forgot_password_page'))
    
    if send_password_reset_email(email):
        flash(f'Code de réinitialisation envoyé à {email}', 'success')
        return redirect(url_for('auth_web.reset_password_page', email=email))
    else:
        flash('Erreur lors de l\'envoi de l\'email', 'error')
        return redirect(url_for('auth_web.forgot_password_page'))

@auth_web_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password_page():
    """Page de réinitialisation de mot de passe"""
    if request.method == 'GET':
        email = request.args.get('email')
        if not email:
            return redirect(url_for('auth_web.forgot_password_page'))
        return render_template('reset_password.html', email=email)
    
    email = request.form.get('email')
    code = request.form.get('code')
    new_password = request.form.get('new_password')
    
    if not email or not code or not new_password:
        flash('Tous les champs sont requis', 'error')
        return redirect(url_for('auth_web.reset_password_page', email=email))
    
    if len(new_password) < 6:
        flash('Le mot de passe doit contenir au moins 6 caractères', 'error')
        return redirect(url_for('auth_web.reset_password_page', email=email))
    
    if verify_password_reset_code(email, code):
        if reset_user_password(email, new_password):
            flash('Mot de passe réinitialisé avec succès !', 'success')
            return redirect(url_for('auth_web.web_login'))
        else:
            flash('Erreur lors de la réinitialisation', 'error')
            return redirect(url_for('auth_web.reset_password_page', email=email))
    else:
        flash('Code invalide ou expiré', 'error')
        return redirect(url_for('auth_web.reset_password_page', email=email))

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

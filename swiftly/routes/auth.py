"""Routes d'authentification"""

from flask import Blueprint, jsonify, request, render_template, redirect, url_for, session, flash
from swiftly.database import (
    create_user, verify_user, update_user_email, 
    update_user_password, users
)
from swiftly.utils.decorators import require_auth

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
auth_web_bp = Blueprint('auth_web', __name__, url_prefix='/auth')

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
        return render_template('auth.html')
    
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not email or not password:
        flash('Email et mot de passe requis', 'error')
        return redirect(url_for('auth_web.web_login'))
    
    if verify_user(email, password):
        session['email'] = email
        flash('Connexion réussie !', 'success')
        return redirect(url_for('dashboard.home'))
    else:
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
        session['email'] = email
        flash('Compte créé avec succès !', 'success')
        return redirect(url_for('dashboard.home'))
    else:
        flash('Un compte avec cet email existe déjà', 'error')
        return redirect(url_for('auth_web.web_login'))

@auth_web_bp.route('/logout')
def logout():
    """Déconnexion"""
    session.pop('email', None)
    flash('Déconnexion réussie', 'success')
    return redirect(url_for('main.index'))

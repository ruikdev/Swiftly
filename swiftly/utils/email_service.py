"""Service d'envoi d'emails"""

import smtplib
import secrets
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Stockage temporaire des codes de vérification
verification_codes = {}
password_reset_codes = {}

def send_email(to_email, subject, body_html):
    """Envoyer un email via SMTP"""
    smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_user = os.environ.get('SMTP_USER')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    smtp_from = os.environ.get('SMTP_FROM', smtp_user)
    
    if not smtp_user or not smtp_password:
        print("ERREUR: Configuration SMTP manquante dans .env")
        return False
    
    try:
        # Créer le message
        msg = MIMEMultipart('alternative')
        msg['From'] = smtp_from
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Attacher le corps HTML
        html_part = MIMEText(body_html, 'html')
        msg.attach(html_part)
        
        # Connexion et envoi
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        print(f"Email envoyé avec succès à {to_email}")
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {e}")
        return False

def generate_verification_code():
    """Générer un code de vérification à 6 chiffres"""
    return ''.join([str(secrets.randbelow(10)) for _ in range(6)])

def send_verification_email(email):
    """Envoyer un email de vérification"""
    code = generate_verification_code()
    
    # Stocker le code avec expiration (15 minutes)
    verification_codes[email] = {
        'code': code,
        'expires_at': time.time() + 900  # 15 minutes
    }
    
    subject = "Vérification de votre compte Swiftly"
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>Bienvenue sur Swiftly!</h2>
            <p>Votre code de vérification est:</p>
            <h1 style="color: #007bff; font-size: 32px; letter-spacing: 5px;">{code}</h1>
            <p>Ce code expire dans 15 minutes.</p>
            <p>Si vous n'avez pas créé de compte, ignorez cet email.</p>
        </body>
    </html>
    """
    
    return send_email(email, subject, body)

def verify_code(email, code):
    """Vérifier un code de vérification"""
    if email not in verification_codes:
        return False
    
    stored_data = verification_codes[email]
    
    # Vérifier l'expiration
    if time.time() > stored_data['expires_at']:
        del verification_codes[email]
        return False
    
    # Vérifier le code
    if stored_data['code'] == code:
        del verification_codes[email]
        return True
    
    return False

def send_password_reset_email(email):
    """Envoyer un email de réinitialisation de mot de passe"""
    code = generate_verification_code()
    
    # Stocker le code avec expiration (15 minutes)
    password_reset_codes[email] = {
        'code': code,
        'expires_at': time.time() + 900  # 15 minutes
    }
    
    subject = "Réinitialisation de votre mot de passe Swiftly"
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>Réinitialisation de mot de passe</h2>
            <p>Vous avez demandé à réinitialiser votre mot de passe.</p>
            <p>Votre code de vérification est:</p>
            <h1 style="color: #007bff; font-size: 32px; letter-spacing: 5px;">{code}</h1>
            <p>Ce code expire dans 15 minutes.</p>
            <p>Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.</p>
        </body>
    </html>
    """
    
    return send_email(email, subject, body)

def verify_password_reset_code(email, code):
    """Vérifier un code de réinitialisation de mot de passe"""
    if email not in password_reset_codes:
        return False
    
    stored_data = password_reset_codes[email]
    
    # Vérifier l'expiration
    if time.time() > stored_data['expires_at']:
        del password_reset_codes[email]
        return False
    
    # Vérifier le code
    if stored_data['code'] == code:
        del password_reset_codes[email]
        return True
    
    return False

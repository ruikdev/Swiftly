"""Module d'analytics pour tracking des visiteurs"""

import json
import os
from datetime import datetime
from flask import request
import hashlib
from cryptography.fernet import Fernet
from swiftly.config import SITES_FOLDER, ANALYTICS_ENCRYPTION_KEY

def get_cipher():
    """Obtenir le cipher pour crypter/décrypter"""
    return Fernet(ANALYTICS_ENCRYPTION_KEY)

def get_visitor_data():
    """Extraire toutes les données du visiteur depuis la requête Flask"""
    user_agent = request.headers.get('User-Agent', '')
    
    # Parsing OS
    os_name = 'Unknown'
    if 'Windows NT 10.0' in user_agent:
        os_name = 'Windows 10/11'
    elif 'Windows NT 6.3' in user_agent:
        os_name = 'Windows 8.1'
    elif 'Windows NT 6.2' in user_agent:
        os_name = 'Windows 8'
    elif 'Windows NT 6.1' in user_agent:
        os_name = 'Windows 7'
    elif 'Mac OS X' in user_agent:
        os_name = 'macOS'
    elif 'Linux' in user_agent and 'Android' not in user_agent:
        os_name = 'Linux'
    elif 'Android' in user_agent:
        os_name = 'Android'
    elif 'iPhone' in user_agent or 'iPad' in user_agent:
        os_name = 'iOS'
    
    # Parsing Browser
    browser = 'Unknown'
    if 'Edg/' in user_agent:
        browser = 'Edge'
    elif 'Chrome/' in user_agent and 'Edg/' not in user_agent:
        browser = 'Chrome'
    elif 'Firefox/' in user_agent:
        browser = 'Firefox'
    elif 'Safari/' in user_agent and 'Chrome' not in user_agent:
        browser = 'Safari'
    elif 'Opera/' in user_agent or 'OPR/' in user_agent:
        browser = 'Opera'
    
    # Géolocalisation approximative (pays) via IP
    # Note: En production, utiliser un service comme ipapi.co ou GeoIP2
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip:
        ip = ip.split(',')[0].strip()
    
    country = get_country_from_ip(ip)
    
    data = {
        'timestamp': datetime.utcnow().isoformat(),
        'ip': ip,
        'country': country,
        'os': os_name,
        'browser': browser,
        'user_agent': user_agent,
        'referrer': request.headers.get('Referer', 'Direct'),
        'path': request.path,
        'method': request.method,
        'language': request.headers.get('Accept-Language', 'Unknown'),
    }
    
    return data

def get_country_from_ip(ip):
    """Obtenir le pays depuis l'IP (version basique)"""
    # Version simplifiée - en production, utiliser un service externe
    # Exemples: ipapi.co, ip-api.com, ou GeoIP2
    if not ip or ip == '127.0.0.1' or ip.startswith('192.168.') or ip.startswith('10.'):
        return 'Local'
    
    # Pour l'instant, retourner "Unknown" - à implémenter avec un vrai service
    return 'Unknown'

def encrypt_data(data):
    """Crypter les données sensibles"""
    cipher = get_cipher()
    json_data = json.dumps(data)
    encrypted = cipher.encrypt(json_data.encode())
    return encrypted.hex()

def decrypt_data(encrypted_hex):
    """Décrypter les données"""
    try:
        cipher = get_cipher()
        encrypted = bytes.fromhex(encrypted_hex)
        decrypted = cipher.decrypt(encrypted)
        return json.loads(decrypted.decode())
    except Exception as e:
        print(f"Erreur de décryptage: {e}")
        return None

def get_analytics_db_path(site_name):
    """Obtenir le chemin de la DB analytics pour un site"""
    from swiftly.database import load_sites
    sites = load_sites()
    
    if site_name not in sites:
        return None
    
    site_data = sites[site_name]
    if isinstance(site_data, dict) and "folder" in site_data:
        folder = site_data["folder"]
        site_folder = os.path.abspath(os.path.join(SITES_FOLDER, folder))
        db_path = os.path.join(site_folder, '.analytics.json')
        return db_path
    
    return None

def init_analytics_db(site_name):
    """Initialiser la DB analytics pour un site"""
    db_path = get_analytics_db_path(site_name)
    if not db_path:
        return False
    
    if not os.path.exists(db_path):
        initial_data = {
            'visits': [],
            'created_at': datetime.utcnow().isoformat()
        }
        with open(db_path, 'w') as f:
            json.dump(initial_data, f, indent=2)
    
    return True

def track_visit(site_name):
    """Enregistrer une visite sur un site"""
    db_path = get_analytics_db_path(site_name)
    if not db_path:
        return False
    
    # Initialiser si nécessaire
    if not os.path.exists(db_path):
        init_analytics_db(site_name)
    
    # Capturer les données
    visitor_data = get_visitor_data()
    
    # Crypter les données
    encrypted_data = encrypt_data(visitor_data)
    
    # Charger la DB avec récupération automatique
    try:
        with open(db_path, 'r') as f:
            analytics = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        analytics = {'visits': [], 'created_at': datetime.utcnow().isoformat()}
    
    # Vérifier que la clé 'visits' existe, sinon réinitialiser
    if 'visits' not in analytics or not isinstance(analytics['visits'], list):
        print(f"⚠️ DB analytics corrompue pour {site_name}, réinitialisation...")
        analytics = {'visits': [], 'created_at': datetime.utcnow().isoformat()}
    
    # Ajouter la visite cryptée
    analytics['visits'].append({
        'id': len(analytics['visits']) + 1,
        'data': encrypted_data,
        'timestamp': visitor_data['timestamp']  # Non crypté pour tri/filtrage
    })
    
    # Sauvegarder
    with open(db_path, 'w') as f:
        json.dump(analytics, f, indent=2)
    
    return True

def get_analytics(site_name, decrypt=True):
    """Récupérer les analytics d'un site"""
    db_path = get_analytics_db_path(site_name)
    if not db_path or not os.path.exists(db_path):
        return None
    
    try:
        with open(db_path, 'r') as f:
            analytics = json.load(f)
        
        # Vérifier intégrité de la structure
        if 'visits' not in analytics or not isinstance(analytics['visits'], list):
            print(f"⚠️ DB analytics corrompue pour {site_name}, réinitialisation...")
            analytics = {'visits': [], 'created_at': datetime.utcnow().isoformat()}
            with open(db_path, 'w') as f:
                json.dump(analytics, f, indent=2)
        
        if decrypt:
            # Décrypter toutes les visites
            decrypted_visits = []
            for visit in analytics.get('visits', []):
                decrypted = decrypt_data(visit['data'])
                if decrypted:
                    decrypted['visit_id'] = visit['id']
                    decrypted_visits.append(decrypted)
            
            analytics['visits'] = decrypted_visits
        
        return analytics
    except Exception as e:
        print(f"Erreur lecture analytics: {e}")
        return None

def get_analytics_stats(site_name):
    """Calculer les statistiques à partir des analytics"""
    analytics = get_analytics(site_name, decrypt=True)
    if not analytics:
        return None
    
    visits = analytics.get('visits', [])
    
    if not visits:
        return {
            'total_visits': 0,
            'unique_ips': 0,
            'countries': {},
            'browsers': {},
            'os': {},
            'referrers': {},
            'hourly': {},
            'daily': {}
        }
    
    # Calculs
    ips = set()
    countries = {}
    browsers = {}
    os_stats = {}
    referrers = {}
    hourly = {}
    daily = {}
    
    for visit in visits:
        # IPs uniques
        ip = visit.get('ip', 'Unknown')
        ips.add(ip)
        
        # Pays
        country = visit.get('country', 'Unknown')
        countries[country] = countries.get(country, 0) + 1
        
        # Navigateurs
        browser = visit.get('browser', 'Unknown')
        browsers[browser] = browsers.get(browser, 0) + 1
        
        # OS
        os_name = visit.get('os', 'Unknown')
        os_stats[os_name] = os_stats.get(os_name, 0) + 1
        
        # Referrers
        referrer = visit.get('referrer', 'Direct')
        if referrer.startswith('http'):
            # Extraire le domaine
            from urllib.parse import urlparse
            domain = urlparse(referrer).netloc
            referrers[domain] = referrers.get(domain, 0) + 1
        else:
            referrers[referrer] = referrers.get(referrer, 0) + 1
        
        # Temporel
        timestamp = visit.get('timestamp', '')
        if timestamp:
            dt = datetime.fromisoformat(timestamp)
            hour_key = dt.strftime('%Y-%m-%d %H:00')
            day_key = dt.strftime('%Y-%m-%d')
            
            hourly[hour_key] = hourly.get(hour_key, 0) + 1
            daily[day_key] = daily.get(day_key, 0) + 1
    
    return {
        'total_visits': len(visits),
        'unique_ips': len(ips),
        'countries': dict(sorted(countries.items(), key=lambda x: x[1], reverse=True)),
        'browsers': dict(sorted(browsers.items(), key=lambda x: x[1], reverse=True)),
        'os': dict(sorted(os_stats.items(), key=lambda x: x[1], reverse=True)),
        'referrers': dict(sorted(referrers.items(), key=lambda x: x[1], reverse=True)),
        'hourly': dict(sorted(hourly.items())),
        'daily': dict(sorted(daily.items()))
    }

"""Configuration de l'application Swiftly"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Configuration Flask
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))

# Configuration du domaine
DOMAIN = os.getenv('DOMAIN', 'localhost:5000')
BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
SUBDOMAIN_BASE = os.getenv('SUBDOMAIN_BASE', 'swiftly.localhost')

# Configuration SSH pour gestion automatique des sous-domaines
ENABLE_SSH_MANAGEMENT = os.getenv('ENABLE_SSH_MANAGEMENT', 'False').lower() == 'true'
SSH_HOST = os.getenv('SSH_HOST', '')
SSH_PORT = int(os.getenv('SSH_PORT', 22))
SSH_USER = os.getenv('SSH_USER', 'root')
SSH_PASSWORD = os.getenv('SSH_PASSWORD', '')
SSH_KEY_PATH = os.getenv('SSH_KEY_PATH', '')

# Configuration Nginx
NGINX_SITES_AVAILABLE = os.getenv('NGINX_SITES_AVAILABLE', '/etc/nginx/sites-available')
NGINX_SITES_ENABLED = os.getenv('NGINX_SITES_ENABLED', '/etc/nginx/sites-enabled')
DOCKER_CONTAINER_IP = os.getenv('DOCKER_CONTAINER_IP', '172.17.0.1')
DOCKER_CONTAINER_PORT = int(os.getenv('DOCKER_CONTAINER_PORT', 5000))

# Base de données SQLite centralisée
DATABASE_PATH = os.getenv('DATABASE_PATH', 'db/swiftly.db')

# Dossier de stockage des sites
SITES_FOLDER = "sites"

# Clé de cryptage pour les analytics
ANALYTICS_ENCRYPTION_KEY = os.getenv('ANALYTICS_ENCRYPTION_KEY', 'ZliOEOl1awGF9J3OCZPhTvXVMvVc7_0qgtBh1OMXDqo=').encode()

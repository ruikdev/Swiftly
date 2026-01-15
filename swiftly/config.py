"""Configuration de l'application Swiftly"""

import os

# Chemins des bases de données
DB_USERS = "db/users.json"
DB_SITES = "db/sites.json"

# Dossier de stockage des sites
SITES_FOLDER = "sites"

# Clé de cryptage pour les analytics (généré avec Fernet.generate_key())
ANALYTICS_ENCRYPTION_KEY = b'8xK9mN2pQsdf453167L8nM2pR5sT7uX0='

# Configuration Flask
DEBUG = True
HOST = "0.0.0.0"
PORT = 5000

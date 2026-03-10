"""Configuration de l'application Swiftly"""

import os
from dotenv import load_dotenv

load_dotenv()

# Chemins des bases de données
DB_USERS = "db/users.json"
DB_SITES = "db/sites.json"

# Dossier de stockage des sites
SITES_FOLDER = "sites"

# Clé de cryptage pour les analytics (généré avec Fernet.generate_key())
ANALYTICS_ENCRYPTION_KEY = os.getenv("ANALYTICS_ENCRYPTION_KEY")

# Configuration Flask
DEBUG = True
HOST = "0.0.0.0"
PORT = 2019

#!/bin/bash

# Script d'installation et configuration rapide de Swiftly
# Usage: ./setup.sh

set -e

echo "🚀 Installation de Swiftly"
echo "=========================="
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    echo "Installation : sudo apt install python3 python3-pip"
    exit 1
fi

echo "✅ Python $(python3 --version) trouvé"

# Installer les dépendances
echo ""
echo "📦 Installation des dépendances..."
pip3 install -r requirements.txt

# Créer le fichier .env si nécessaire
if [ ! -f .env ]; then
    echo ""
    echo "⚙️  Configuration de l'environnement..."
    cp .env.example .env
    
    # Générer une clé secrète
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    # Demander le domaine de base
    echo ""
    echo "Configuration du domaine :"
    read -p "Domaine de base pour les sous-domaines (ex: swiftly.example.com) : " SUBDOMAIN_BASE
    
    # Demander si SSH doit être activé
    echo ""
    read -p "Activer la gestion SSH automatique ? (y/N) : " ENABLE_SSH
    
    if [[ $ENABLE_SSH =~ ^[Yy]$ ]]; then
        read -p "Hôte SSH (IP ou domaine du VPS) : " SSH_HOST
        read -p "Utilisateur SSH (défaut: root) : " SSH_USER
        SSH_USER=${SSH_USER:-root}
        read -p "Port SSH (défaut: 22) : " SSH_PORT
        SSH_PORT=${SSH_PORT:-22}
        
        # Mettre à jour le .env
        sed -i "s|ENABLE_SSH_MANAGEMENT=False|ENABLE_SSH_MANAGEMENT=True|g" .env
        sed -i "s|SSH_HOST=|SSH_HOST=$SSH_HOST|g" .env
        sed -i "s|SSH_USER=root|SSH_USER=$SSH_USER|g" .env
        sed -i "s|SSH_PORT=22|SSH_PORT=$SSH_PORT|g" .env
    fi
    
    # Mettre à jour les valeurs dans .env
    sed -i "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|g" .env
    sed -i "s|SUBDOMAIN_BASE=.*|SUBDOMAIN_BASE=$SUBDOMAIN_BASE|g" .env
    
    echo "✅ Fichier .env créé et configuré"
else
    echo "ℹ️  Fichier .env existant trouvé, conservation"
fi

# Créer les dossiers nécessaires
echo ""
echo "📁 Création des dossiers..."
mkdir -p db sites

# Initialiser la base de données
echo ""
echo "💾 Initialisation de la base de données..."
python3 -c "from swiftly.database import init_db; init_db()"

echo ""
echo "✨ Installation terminée !"
echo ""
echo "📝 Prochaines étapes :"
echo ""
echo "1. 🔐 Compte admin par défaut créé :"
echo "   Email : admin@admin"
echo "   Mot de passe : admin"
echo "   ⚠️  Changez ce mot de passe immédiatement !"
echo ""
echo "2. 🌐 Configuration DNS (si sous-domaines auto) :"
echo "   - Configurez un wildcard DNS : *.$SUBDOMAIN_BASE"
echo "   - Pointant vers votre serveur"
echo ""
echo "3. 🚀 Démarrer l'application :"
echo "   python3 app.py"
echo ""
echo "   Ou avec Docker :"
echo "   docker-compose up -d --build"
echo ""
echo "4. 📖 Documentation :"
echo "   - README : README_NEW.md"
echo "   - Déploiement : DEPLOYMENT.md"
echo "   - API : API.md"
echo ""
echo "🎉 Swiftly est prêt !"

#!/bin/bash

# 🚀 Swiftly CLI - Installer & Launcher (Linux/macOS)

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON_CMD="python3"

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          🚀 SWIFTLY CLI - Initialisation                     ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"

# Vérifier Python
echo -e "\n${BLUE}[1/4]${NC} Vérification de Python..."
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo -e "${RED}❌ Python 3 n'est pas installé!${NC}"
    echo "Installe Python 3 depuis https://www.python.org"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python ${PYTHON_VERSION} trouvé${NC}"

# Créer ou utiliser le venv
echo -e "\n${BLUE}[2/4]${NC} Configuration de l'environnement virtuel..."
if [ -d "$VENV_DIR" ]; then
    echo -e "${GREEN}✅ Environnement virtuel trouvé${NC}"
else
    echo -e "${BLUE}📦 Création de l'environnement virtuel...${NC}"
    $PYTHON_CMD -m venv "$VENV_DIR"
    echo -e "${GREEN}✅ Environnement virtuel créé${NC}"
fi

# Activer le venv
source "$VENV_DIR/bin/activate"
echo -e "${GREEN}✅ Environnement virtuel activé${NC}"

# Vérifier et installer requests
echo -e "\n${BLUE}[3/4]${NC} Installation des dépendances..."
if ! python -c "import requests" 2>/dev/null; then
    echo -e "${BLUE}📦 Installation de requests...${NC}"
    pip install requests -q
    echo -e "${GREEN}✅ requests installé${NC}"
else
    echo -e "${GREEN}✅ requests déjà installé${NC}"
fi

# Vérifier que swiftly_cli.py existe
echo -e "\n${BLUE}[4/4]${NC} Vérification des fichiers..."
if [ ! -f "$SCRIPT_DIR/swiftly_cli.py" ]; then
    echo -e "${RED}❌ swiftly_cli.py non trouvé dans $SCRIPT_DIR${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Tous les fichiers présents${NC}"

# Lancer le CLI
echo -e "\n${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Initialisation terminée! Lancement du CLI...${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}\n"

cd "$SCRIPT_DIR"
python swiftly_cli.py

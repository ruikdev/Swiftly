#!/bin/bash

# 🚀 Swiftly CLI - Installer & Launcher (Linux/macOS)

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
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
echo -e "\n${BLUE}[1/3]${NC} Vérification de Python..."
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo -e "${RED}❌ Python 3 n'est pas installé!${NC}"
    echo "Installe Python 3 depuis https://www.python.org"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python ${PYTHON_VERSION} trouvé${NC}"

# Vérifier et installer requests
echo -e "\n${BLUE}[2/3]${NC} Installation des dépendances..."
if ! $PYTHON_CMD -c "import requests" 2>/dev/null; then
    echo -e "${BLUE}📦 Installation de requests...${NC}"
    $PYTHON_CMD -m pip install requests -q
    echo -e "${GREEN}✅ requests installé${NC}"
else
    echo -e "${GREEN}✅ requests déjà installé${NC}"
fi

# Vérifier que swiftly_cli.py existe
echo -e "\n${BLUE}[3/3]${NC} Vérification des fichiers..."
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
exec $PYTHON_CMD swiftly_cli.py

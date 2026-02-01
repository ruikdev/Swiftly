#!/bin/bash

# 🚀 Swiftly CLI - Installer & Launcher (Linux/macOS)

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON_CMD="python3"
CLI_FILE="$SCRIPT_DIR/swiftly_cli.py"
CLI_URL="https://raw.githubusercontent.com/ruikdev/Swiftly/main/swiftly_cli.py"

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          🚀 SWIFTLY CLI - Initialisation                     ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"

# Vérifier Python
echo -e "\n${BLUE}[1/5]${NC} Vérification de Python..."
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo -e "${RED}❌ Python 3 n'est pas installé!${NC}"
    echo "Installe Python 3 depuis https://www.python.org"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python ${PYTHON_VERSION} trouvé${NC}"

# Mettre à jour swiftly_cli.py depuis GitHub
echo -e "\n${BLUE}[2/5]${NC} Mise à jour du CLI..."

# Sauvegarder l'ancienne version si elle existe
if [ -f "$CLI_FILE" ]; then
    cp "$CLI_FILE" "${CLI_FILE}.bak" 2>/dev/null || true
fi

echo -e "${YELLOW}📥 Téléchargement de la dernière version...${NC}"

# Essayer avec curl
if command -v curl &> /dev/null; then
    curl -fsSL "$CLI_URL" -o "$CLI_FILE" 2>/dev/null
# Sinon essayer avec wget
elif command -v wget &> /dev/null; then
    wget -q "$CLI_URL" -O "$CLI_FILE" 2>/dev/null
else
    echo -e "${YELLOW}⚠️  curl ou wget non trouvé, utilisation de la version locale${NC}"
    if [ -f "${CLI_FILE}.bak" ]; then
        mv "${CLI_FILE}.bak" "$CLI_FILE"
    fi
fi

if [ -f "$CLI_FILE" ] && [ -s "$CLI_FILE" ]; then
    echo -e "${GREEN}✅ CLI à jour${NC}"
    rm -f "${CLI_FILE}.bak" 2>/dev/null || true
else
    echo -e "${YELLOW}⚠️  Échec du téléchargement, restauration de l'ancienne version${NC}"
    if [ -f "${CLI_FILE}.bak" ]; then
        mv "${CLI_FILE}.bak" "$CLI_FILE"
        echo -e "${GREEN}✅ Version locale restaurée${NC}"
    else
        echo -e "${RED}❌ Aucune version du CLI trouvée${NC}"
        exit 1
    fi
fi

# Créer ou utiliser le venv
echo -e "\n${BLUE}[3/5]${NC} Configuration de l'environnement virtuel..."
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
echo -e "\n${BLUE}[4/5]${NC} Installation des dépendances..."
if ! python -c "import requests" 2>/dev/null; then
    echo -e "${BLUE}📦 Installation de requests...${NC}"
    pip install requests -q
    pip install rich -q
    echo -e "${GREEN}✅ requests installé${NC}"
else
    echo -e "${GREEN}✅ requests déjà installé${NC}"
fi

# Vérifier que swiftly_cli.py existe
echo -e "\n${BLUE}[5/5]${NC} Vérification finale..."
if [ ! -f "$SCRIPT_DIR/swiftly_cli.py" ]; then
    echo -e "${RED}❌ swiftly_cli.py non trouvé${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Tous les fichiers présents${NC}"

# Lancer le CLI
echo -e "\n${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Initialisation terminée! Lancement du CLI...${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}\n"

cd "$SCRIPT_DIR"
python swiftly_cli.py

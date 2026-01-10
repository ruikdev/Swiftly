@echo off
REM 🚀 Swiftly CLI - Installer & Launcher (Windows)

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%.venv"
set "PYTHON_CMD=python"
set "CLI_FILE=%SCRIPT_DIR%swiftly_cli.py"
set "CLI_URL=https://raw.githubusercontent.com/ruikdev/Swiftly/main/swiftly_cli.py"

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║          🚀 SWIFTLY CLI - Initialisation                     ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Vérifier Python
echo [1/5] Vérification de Python...
where %PYTHON_CMD% >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou n'est pas dans PATH!
    echo.
    echo Actions à faire:
    echo 1. Installe Python depuis https://www.python.org
    echo 2. Assure-toi que Python est ajouté à PATH
    echo 3. Réessaye ce script
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('%PYTHON_CMD% --version') do set PYTHON_VERSION=%%i
echo ✅ %PYTHON_VERSION% trouvé
echo.

REM Vérifier ou télécharger swiftly_cli.py
echo [2/5] Vérification du CLI...
if exist "%CLI_FILE%" (
    echo ✅ CLI trouvé localement
) else (
    echo 📥 Téléchargement du CLI depuis GitHub...
    
    REM Utiliser PowerShell pour télécharger
    powershell -NoProfile -Command "try { (New-Object Net.WebClient).DownloadFile('%CLI_URL%', '%CLI_FILE%'); exit 0 } catch { exit 1 }"
    
    if errorlevel 1 (
        echo ❌ Erreur lors du téléchargement du CLI
        echo.
        echo Assure-toi que tu as une connexion Internet
        echo.
        pause
        exit /b 1
    )
    
    echo ✅ CLI téléchargé avec succès
)
echo.

REM Créer ou utiliser le venv
echo [3/5] Configuration de l'environnement virtuel...
if exist "%VENV_DIR%" (
    echo ✅ Environnement virtuel trouvé
) else (
    echo 📦 Création de l'environnement virtuel...
    %PYTHON_CMD% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo ❌ Erreur lors de la création du venv
        echo.
        pause
        exit /b 1
    )
    echo ✅ Environnement virtuel créé
)
echo.

REM Activer le venv
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo ❌ Erreur lors de l'activation du venv
    echo.
    pause
    exit /b 1
)
echo ✅ Environnement virtuel activé
echo.

REM Vérifier et installer requests
echo [4/5] Installation des dépendances...
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installation de requests...
    python -m pip install requests -q
    if errorlevel 1 (
        echo ❌ Erreur lors de l'installation de requests
        echo.
        echo Essaye d'installer manuellement:
        echo python -m pip install requests
        echo.
        pause
        exit /b 1
    )
    echo ✅ requests installé
) else (
    echo ✅ requests déjà installé
)
echo.

REM Vérifier que swiftly_cli.py existe
echo [5/5] Vérification finale...
if not exist "%CLI_FILE%" (
    echo ❌ swiftly_cli.py non trouvé
    echo.
    pause
    exit /b 1
)
echo ✅ Tous les fichiers présents
echo.

REM Lancer le CLI
echo ════════════════════════════════════════════════════════════════
echo ✅ Initialisation terminée! Lancement du CLI...
echo ════════════════════════════════════════════════════════════════
echo.

cd /d "%SCRIPT_DIR%"
python swiftly_cli.py
pause

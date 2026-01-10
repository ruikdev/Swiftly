@echo off
REM 🚀 Swiftly CLI - Installer & Launcher (Windows)

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%.venv"
set "PYTHON_CMD=python"

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║          🚀 SWIFTLY CLI - Initialisation                     ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Vérifier Python
echo [1/4] Vérification de Python...
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

REM Créer ou utiliser le venv
echo [2/4] Configuration de l'environnement virtuel...
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
echo [3/4] Installation des dépendances...
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
echo [4/4] Vérification des fichiers...
if not exist "%SCRIPT_DIR%swiftly_cli.py" (
    echo ❌ swiftly_cli.py non trouvé dans %SCRIPT_DIR%
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

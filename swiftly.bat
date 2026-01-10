@echo off
REM 🚀 Swiftly CLI - Installer & Launcher (Windows)

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PYTHON_CMD=python"

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║          🚀 SWIFTLY CLI - Initialisation                     ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Vérifier Python
echo [1/3] Vérification de Python...
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

REM Vérifier et installer requests
echo [2/3] Installation des dépendances...
%PYTHON_CMD% -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installation de requests...
    %PYTHON_CMD% -m pip install requests -q
    if errorlevel 1 (
        echo ❌ Erreur lors de l'installation de requests
        echo.
        echo Essaye d'installer manuellement:
        echo %PYTHON_CMD% -m pip install requests
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
echo [3/3] Vérification des fichiers...
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
%PYTHON_CMD% swiftly_cli.py
pause

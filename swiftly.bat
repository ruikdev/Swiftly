@echo off
REM 🚀 Swiftly CLI - Installer & Launcher (Windows)

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%.venv"
set "PYTHON_CMD="
set "CLI_FILE=%SCRIPT_DIR%swiftly_cli.py"
set "CLI_URL=https://raw.githubusercontent.com/ruikdev/Swiftly/main/swiftly_cli.py"

echo.
echo ================================================================
echo           SWIFTLY CLI - Initialisation
echo ================================================================
echo.

REM Vérifier Python - Éviter WAPT et trouver le vrai Python
echo [1/5] Verification de Python...

REM Essayer d'abord py launcher (recommandé sur Windows)
where py >nul 2>&1
if not errorlevel 1 (
    py --version >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_CMD=py"
        goto :python_found
    )
)

REM Essayer python3
where python3 >nul 2>&1
if not errorlevel 1 (
    python3 --version >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_CMD=python3"
        goto :python_found
    )
)

REM Essayer python (en évitant WAPT)
for /f "tokens=*" %%i in ('where python 2^>nul') do (
    echo %%i | findstr /i /v "wapt" >nul
    if not errorlevel 1 (
        %%i --version >nul 2>&1
        if not errorlevel 1 (
            set "PYTHON_CMD=%%i"
            goto :python_found
        )
    )
)

echo [ERREUR] Python n'est pas installe ou n'est pas dans PATH!
echo.
echo Actions a faire:
echo 1. Installe Python depuis https://www.python.org
echo 2. Assure-toi que Python est ajoute a PATH
echo 3. Reessaye ce script
echo.
pause
exit /b 1

:python_found
for /f "tokens=*" %%i in ('%PYTHON_CMD% --version') do set PYTHON_VERSION=%%i
echo [OK] %PYTHON_VERSION% trouve
echo     Chemin: %PYTHON_CMD%
echo.

REM Mettre a jour swiftly_cli.py depuis GitHub
echo [2/5] Mise a jour du CLI...

REM Sauvegarder l'ancienne version si elle existe
if exist "%CLI_FILE%" (
    copy /Y "%CLI_FILE%" "%CLI_FILE%.bak" >nul 2>&1
)

echo     Telechargement de la derniere version...

REM Utiliser PowerShell pour télécharger
powershell -NoProfile -Command "try { (New-Object Net.WebClient).DownloadFile('%CLI_URL%', '%CLI_FILE%'); exit 0 } catch { exit 1 }" >nul 2>&1

if errorlevel 1 (
    echo [AVERT] Echec du telechargement, utilisation de la version locale
    if exist "%CLI_FILE%.bak" (
        move /Y "%CLI_FILE%.bak" "%CLI_FILE%" >nul 2>&1
    )
) else (
    echo [OK] CLI a jour
    if exist "%CLI_FILE%.bak" (
        del /Q "%CLI_FILE%.bak" >nul 2>&1
    )
)

if not exist "%CLI_FILE%" (
    echo [ERREUR] Aucune version du CLI trouvee
    echo.
    pause
    exit /b 1
)
echo.

REM Créer ou utiliser le venv
echo [3/5] Configuration de l'environnement virtuel...
if exist "%VENV_DIR%" (
    echo [OK] Environnement virtuel trouve
) else (
    echo     Creation de l'environnement virtuel...
    %PYTHON_CMD% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [ERREUR] Erreur lors de la creation du venv
        echo.
        echo Il se peut que le module venv ne soit pas installe.
        echo Essaye d'executer le CLI sans venv...
        echo.
        goto :skip_venv
    )
    echo [OK] Environnement virtuel cree
)
echo.

REM Activer le venv
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo [AVERT] Erreur lors de l'activation du venv
    echo         Utilisation de Python global...
    echo.
    goto :skip_venv
)
echo [OK] Environnement virtuel active
echo.

:skip_venv
REM Vérifier et installer requests
echo [4/5] Installation des dependances...
%PYTHON_CMD% -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo     Installation de requests...
    %PYTHON_CMD% -m pip install requests -q
    if errorlevel 1 (
        echo [ERREUR] Erreur lors de l'installation de requests
        echo.
        echo Essaye d'installer manuellement:
        echo %PYTHON_CMD% -m pip install requests
        echo.
        pause
        exit /b 1
    )
    echo [OK] requests installe
) else (
    echo [OK] requests deja installe
)
echo.

REM Vérifier que swiftly_cli.py existe
echo [5/5] Verification finale...
if not exist "%CLI_FILE%" (
    echo [ERREUR] swiftly_cli.py non trouve
    echo.
    pause
    exit /b 1
)
echo [OK] Tous les fichiers presents
echo.

REM Lancer le CLI
echo ================================================================
echo  Initialisation terminee! Lancement du CLI...
echo ================================================================
echo.

cd /d "%SCRIPT_DIR%"
%PYTHON_CMD% swiftly_cli.py
pause

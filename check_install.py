#!/usr/bin/env python3
"""Script de vérification de l'installation Swiftly"""

import os
import sys

def check_file(path, description):
    """Vérifier l'existence d'un fichier"""
    if os.path.exists(path):
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - Manquant: {path}")
        return False

def check_directory(path, description):
    """Vérifier l'existence d'un dossier"""
    if os.path.isdir(path):
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - Manquant: {path}")
        return False

def check_import(module, description):
    """Vérifier qu'un module peut être importé"""
    try:
        __import__(module)
        print(f"✅ {description}")
        return True
    except ImportError:
        print(f"❌ {description} - Module non installé: {module}")
        return False

def main():
    print("🔍 Vérification de l'installation Swiftly")
    print("=" * 50)
    print()
    
    checks_passed = 0
    checks_total = 0
    
    # Fichiers de configuration
    print("📁 Fichiers de configuration:")
    checks_total += 4
    checks_passed += check_file(".env", "Fichier .env")
    checks_passed += check_file(".env.example", "Fichier .env.example")
    checks_passed += check_file("requirements.txt", "requirements.txt")
    checks_passed += check_file("app.py", "Point d'entrée app.py")
    print()
    
    # Scripts
    print("🔧 Scripts:")
    checks_total += 3
    checks_passed += check_file("setup.sh", "Script d'installation")
    checks_passed += check_file("migrate_to_sqlite.py", "Script de migration")
    checks_passed += check_file("docker-compose.yml", "Docker Compose")
    print()
    
    # Documentation
    print("📚 Documentation:")
    checks_total += 5
    checks_passed += check_file("README_NEW.md", "README principal")
    checks_passed += check_file("DEPLOYMENT.md", "Guide de déploiement")
    checks_passed += check_file("API.md", "Documentation API")
    checks_passed += check_file("CHANGELOG.md", "Changelog")
    checks_passed += check_file("SUMMARY.md", "Résumé")
    print()
    
    # Dossiers
    print("📂 Dossiers:")
    checks_total += 4
    checks_passed += check_directory("swiftly", "Package swiftly")
    checks_passed += check_directory("templates", "Templates HTML")
    checks_passed += check_directory("db", "Dossier base de données")
    checks_passed += check_directory("sites", "Dossier sites")
    print()
    
    # Modules Python
    print("🐍 Modules swiftly:")
    checks_total += 6
    checks_passed += check_file("swiftly/__init__.py", "swiftly.__init__")
    checks_passed += check_file("swiftly/config.py", "swiftly.config")
    checks_passed += check_file("swiftly/database.py", "swiftly.database (SQLite)")
    checks_passed += check_file("swiftly/routes/admin.py", "swiftly.routes.admin")
    checks_passed += check_file("swiftly/utils/ssh_manager.py", "swiftly.utils.ssh_manager")
    checks_passed += check_file("swiftly/analytics.py", "swiftly.analytics")
    print()
    
    # Templates
    print("🎨 Templates:")
    checks_total += 2
    checks_passed += check_file("templates/admin_panel.html", "Panel admin")
    checks_passed += check_file("templates/site_auth.html", "Page auth site")
    print()
    
    # Dépendances Python
    print("📦 Dépendances Python:")
    checks_total += 5
    checks_passed += check_import("flask", "Flask")
    checks_passed += check_import("bcrypt", "bcrypt")
    checks_passed += check_import("dotenv", "python-dotenv")
    checks_passed += check_import("paramiko", "paramiko")
    checks_passed += check_import("cryptography", "cryptography")
    print()
    
    # Vérifications de configuration
    print("⚙️  Configuration:")
    checks_total += 2
    
    if os.path.exists(".env"):
        with open(".env", 'r') as f:
            content = f.read()
            if "SECRET_KEY" in content and "SUBDOMAIN_BASE" in content:
                print("✅ Fichier .env configuré")
                checks_passed += 1
            else:
                print("⚠️  Fichier .env incomplet")
    
    if os.path.exists("db/swiftly.db"):
        print("✅ Base de données SQLite initialisée")
        checks_passed += 1
    else:
        print("⚠️  Base de données non initialisée (exécutez setup.sh)")
    print()
    
    # Résumé
    print("=" * 50)
    print(f"📊 Résultat: {checks_passed}/{checks_total} vérifications réussies")
    print()
    
    if checks_passed == checks_total:
        print("🎉 Installation complète ! Swiftly est prêt.")
        print()
        print("Prochaines étapes:")
        print("1. python3 app.py")
        print("2. Ouvrir http://localhost:5000")
        print("3. Se connecter avec admin@admin / admin")
        return 0
    else:
        print("⚠️  Installation incomplète.")
        print()
        print("Actions recommandées:")
        if not os.path.exists(".env"):
            print("- Exécuter: cp .env.example .env")
        if not os.path.exists("db/swiftly.db"):
            print("- Exécuter: python3 -c 'from swiftly.database import init_db; init_db()'")
        print("- Installer dépendances: pip3 install -r requirements.txt")
        print("- Ou exécuter: ./setup.sh")
        return 1

if __name__ == "__main__":
    sys.exit(main())

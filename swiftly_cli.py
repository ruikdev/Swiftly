#!/usr/bin/env python3
"""
Swiftly CLI - Outil de gestion de sites statiques (Mode Interactif) - Multilingue
"""

import sys
import os
import json
import requests
import getpass

CONFIG_FILE = os.path.expanduser("~/.swiftly_config.json")
DEFAULT_API_URL = "https://swiftly.ruikdev.me"

TRANSLATIONS = {
    "fr": {
        "title": "🚀 SWIFTLY CLI",
        "logged_in": "👤 Connecté en tant que:",
        "not_logged_in": "👤 Non connecté",
        "main_menu": "📋 MENU PRINCIPAL:",
        "register": "1. Créer un compte",
        "login": "2. Se connecter",
        "check_api": "3. Vérifier l'API (health)",
        "quit": "0. Quitter",
        "profile": "1. Voir mon profil",
        "list_sites": "2. Lister mes sites",
        "deploy": "3. Déployer un nouveau site",
        "delete": "4. Supprimer un site",
        "update_email": "5. Modifier mon email",
        "update_password": "6. Modifier mon mot de passe",
        "logout": "7. Se déconnecter",
        "choice": "Votre choix: ",
        "create_account": "📝 CRÉATION DE COMPTE",
        "email": "Email: ",
        "password": "Mot de passe (min 6 caractères): ",
        "old_password": "Ancien mot de passe: ",
        "new_password": "Nouveau mot de passe (min 6 caractères): ",
        "login_title": "🔐 CONNEXION",
        "current_password": "Mot de passe actuel: ",
        "logout_success": "✅ Déconnexion réussie",
        "user_profile": "📋 PROFIL UTILISATEUR",
        "sites_count": "🌐 Nombre de sites:",
        "sites_list": "📦 Sites:",
        "no_sites": "📭 Vous n'avez aucun site déployé",
        "your_sites": "🌐 VOS SITES",
        "deploy_title": "🚀 DÉPLOYER UN SITE",
        "site_name": "Nom du site: ",
        "folder_path": "Chemin du dossier du projet: ",
        "file_path": "Chemin du fichier HTML: ",
        "folder_not_found": "Le dossier",
        "folder_not_exists": "n'existe pas",
        "folder_not_dir": "Le chemin ne pointe pas vers un dossier",
        "index_missing": "❌ Le dossier doit contenir un fichier 'index.html' à la racine",
        "scanning_folder": "📂 Analyse du dossier...",
        "files_found": "fichiers trouvés",
        "uploading": "📤 Upload en cours...",
        "file_not_found": "Le fichier",
        "file_not_exists": "n'existe pas",
        "file_not_html": "Le fichier doit être un fichier HTML (.html)",
        "delete_title": "🗑️  SUPPRIMER UN SITE",
        "site_to_delete": "Nom du site à supprimer: ",
        "confirm_delete": "Êtes-vous sûr de vouloir supprimer",
        "confirm_yes": "(oui/non): ",
        "delete_cancelled": "❌ Suppression annulée",
        "file_label": "└─ Fichier:",
        "url_label": "└─ URL:",
        "api_ok": "✅ API opérationnelle",
        "api_error": "❌ API non accessible",
        "error": "❌ Erreur:",
        "connection_error": "❌ Erreur de connexion à l'API:",
        "invalid_choice": "❌ Choix invalide",
        "continue": "Appuyez sur Entrée pour continuer...",
        "goodbye": "👋 Au revoir !",
        "language_selection": "Sélectionnez votre langue / Select your language:",
        "french": "1. Français (FR)",
        "english": "2. English (EN)",
        "change_lang": "💬 CHANGER DE LANGUE",
    },
    "en": {
        "title": "🚀 SWIFTLY CLI",
        "logged_in": "👤 Logged in as:",
        "not_logged_in": "👤 Not logged in",
        "main_menu": "📋 MAIN MENU:",
        "register": "1. Create an account",
        "login": "2. Login",
        "check_api": "3. Check API (health)",
        "quit": "0. Quit",
        "profile": "1. View my profile",
        "list_sites": "2. List my sites",
        "deploy": "3. Deploy a new site",
        "delete": "4. Delete a site",
        "update_email": "5. Change my email",
        "update_password": "6. Change my password",
        "logout": "7. Logout",
        "choice": "Your choice: ",
        "create_account": "📝 CREATE ACCOUNT",
        "email": "Email: ",
        "password": "Password (min 6 characters): ",
        "old_password": "Old password: ",
        "new_password": "New password (min 6 characters): ",
        "login_title": "🔐 LOGIN",
        "current_password": "Current password: ",
        "logout_success": "✅ Logout successful",
        "user_profile": "📋 USER PROFILE",
        "sites_count": "🌐 Number of sites:",
        "sites_list": "📦 Sites:",
        "no_sites": "📭 You have no deployed sites",
        "your_sites": "🌐 YOUR SITES",
        "deploy_title": "🚀 DEPLOY A SITE",
        "site_name": "Site name: ",
        "folder_path": "Project folder path: ",
        "file_path": "HTML file path: ",
        "folder_not_found": "The folder",
        "folder_not_exists": "does not exist",
        "folder_not_dir": "The path does not point to a folder",
        "index_missing": "❌ The folder must contain an 'index.html' file at the root",
        "scanning_folder": "📂 Scanning folder...",
        "files_found": "files found",
        "uploading": "📤 Uploading...",
        "file_not_found": "The file",
        "file_not_exists": "does not exist",
        "file_not_html": "The file must be an HTML file (.html)",
        "delete_title": "🗑️  DELETE A SITE",
        "site_to_delete": "Site name to delete: ",
        "confirm_delete": "Are you sure you want to delete",
        "confirm_yes": "(yes/no): ",
        "delete_cancelled": "❌ Deletion cancelled",
        "file_label": "└─ File:",
        "url_label": "└─ URL:",
        "api_ok": "✅ API is operational",
        "api_error": "❌ API is not accessible",
        "error": "❌ Error:",
        "connection_error": "❌ Connection error with API:",
        "invalid_choice": "❌ Invalid choice",
        "continue": "Press Enter to continue...",
        "goodbye": "👋 Goodbye!",
        "language_selection": "Select your language / Sélectionnez votre langue:",
        "french": "1. Français (FR)",
        "english": "2. English (EN)",
        "change_lang": "💬 CHANGE LANGUAGE",
    }
}

class SwiftlyCLI:
    def __init__(self):
        self.config = self.load_config()
        self.api_url = self.config.get("api_url", DEFAULT_API_URL)
        self.email = self.config.get("email")
        self.password = self.config.get("password")
        self.language = self.config.get("language", "fr")
        self.running = True
    
    def t(self, key):
        """Obtenir une traduction"""
        return TRANSLATIONS.get(self.language, TRANSLATIONS["fr"]).get(key, key)
    
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_config(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
            os.chmod(CONFIG_FILE, 0o600)
            return True
        except Exception as e:
            print(f"❌ Error saving config: {e}")
            return False
    
    def get_headers(self):
        if not self.email or not self.password:
            return None
        return {
            "X-User-Email": self.email,
            "X-User-Password": self.password
        }
    
    def is_logged_in(self):
        return self.email is not None and self.password is not None
    
    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def select_language(self):
        self.clear_screen()
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                     🚀 SWIFTLY CLI                          ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()
        print("Select your language / Sélectionnez votre langue:")
        print("1. Français (FR)")
        print("2. English (EN)")
        print()
        choice = input("Votre choix / Your choice: ").strip()
        
        if choice == "2":
            self.language = "en"
        else:
            self.language = "fr"
        
        self.config["language"] = self.language
        self.save_config()
    
    def print_header(self):
        self.clear_screen()
        print("╔══════════════════════════════════════════════════════════════╗")
        print(f"║                     {self.t('title')}                     ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        if self.is_logged_in():
            print(f"{self.t('logged_in')} {self.email}")
        else:
            print(self.t("not_logged_in"))
        print()
    
    def show_main_menu(self):
        self.print_header()
        
        print(self.t("main_menu"))
        if not self.is_logged_in():
            print("  " + self.t("register"))
            print("  " + self.t("login"))
            print("  " + self.t("check_api"))
            print("  9. " + self.t("change_lang"))
            print("  " + self.t("quit"))
        else:
            print("  " + self.t("profile"))
            print("  " + self.t("list_sites"))
            print("  " + self.t("deploy"))
            print("  " + self.t("delete"))
            print("  " + self.t("update_email"))
            print("  " + self.t("update_password"))
            print("  " + self.t("logout"))
            print("  " + self.t("check_api"))
            print("  9. " + self.t("change_lang"))
            print("  " + self.t("quit"))
        
        print()
        choice = input(self.t("choice")).strip()
        return choice
    
    def register_interactive(self):
        self.print_header()
        print(self.t("create_account") + "\n")
        
        email = input(self.t("email")).strip()
        password = getpass.getpass(self.t("password"))
        
        try:
            response = requests.post(
                f"{self.api_url}/api/auth/register",
                json={"email": email, "password": password}
            )
            
            if response.status_code == 201:
                print(f"\n✅ {response.json()['message']}")
                self.config["email"] = email
                self.config["password"] = password
                self.email = email
                self.password = password
                self.save_config()
                input(f"\n{self.t('continue')}")
                return True
            else:
                print(f"\n{self.t('error')} {response.json().get('error', 'Unknown error')}")
                input(f"\n{self.t('continue')}")
                return False
        except Exception as e:
            print(f"\n{self.t('connection_error')} {e}")
            input(f"\n{self.t('continue')}")
            return False
    
    def login_interactive(self):
        self.print_header()
        print(self.t("login_title") + "\n")
        
        email = input(self.t("email")).strip()
        password = getpass.getpass(self.t("password"))
        
        try:
            response = requests.post(
                f"{self.api_url}/api/auth/login",
                json={"email": email, "password": password}
            )
            
            if response.status_code == 200:
                print(f"\n✅ {response.json()['message']}")
                self.config["email"] = email
                self.config["password"] = password
                self.email = email
                self.password = password
                self.save_config()
                input(f"\n{self.t('continue')}")
                return True
            else:
                print(f"\n{self.t('error')} {response.json().get('error', 'Unknown error')}")
                input(f"\n{self.t('continue')}")
                return False
        except Exception as e:
            print(f"\n{self.t('connection_error')} {e}")
            input(f"\n{self.t('continue')}")
            return False
    
    def logout_interactive(self):
        self.config.pop("email", None)
        self.config.pop("password", None)
        self.email = None
        self.password = None
        self.save_config()
        self.print_header()
        print(self.t("logout_success"))
        input(f"\n{self.t('continue')}")
    
    def profile_interactive(self):
        self.print_header()
        try:
            response = requests.get(
                f"{self.api_url}/api/user/profile",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                print(self.t("user_profile") + "\n")
                print(f"📧 Email: {data['email']}")
                print(f"🌐 {self.t('sites_count')} {data['total_sites']}")
                if data['sites']:
                    print(f"\n{self.t('sites_list')}")
                    for site in data['sites']:
                        print(f"   • {site}")
            else:
                print(f"{self.t('error')} {response.json().get('error', 'Unknown error')}")
        except Exception as e:
            print(f"{self.t('connection_error')} {e}")
        
        input(f"\n{self.t('continue')}")
    
    def list_sites_interactive(self):
        self.print_header()
        try:
            response = requests.get(
                f"{self.api_url}/api/sites",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                sites = response.json()["sites"]
                if not sites:
                    print(self.t("no_sites"))
                else:
                    print(self.t("your_sites") + "\n")
                    for name, data in sites.items():
                        # Nouveau format avec dossier
                        if isinstance(data, dict) and "folder" in data:
                            folder = data.get("folder")
                            file_count = data.get("file_count", "?")
                            print(f"📂 {name}")
                            print(f"   └─ Dossier: {folder}")
                            print(f"   └─ Fichiers: {file_count}")
                            print(f"   {self.t('url_label')} {self.api_url}/sites/{name}\n")
                        # Ancien format avec fichier unique
                        elif isinstance(data, dict) and "filename" in data:
                            filename = data.get("filename")
                            print(f"📝 {name}")
                            print(f"   {self.t('file_label')} {filename}")
                            print(f"   {self.t('url_label')} {self.api_url}/sites/{name}\n")
            else:
                try:
                    error_msg = response.json().get('error', 'Unknown error')
                except:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                print(f"{self.t('error')} {error_msg}")
        except Exception as e:
            print(f"{self.t('connection_error')} {e}")
        
        input(f"\n{self.t('continue')}")
    
    def deploy_site_interactive(self):
        self.print_header()
        print(self.t("deploy_title") + "\n")
        
        name = input(self.t("site_name")).strip()
        folder_path = input(self.t("folder_path")).strip().strip("'\"")
        
        # Vérifier que le dossier existe
        if not os.path.exists(folder_path):
            print(f"\n{self.t('error')} {self.t('folder_not_found')} {folder_path} {self.t('folder_not_exists')}")
            input(f"\n{self.t('continue')}")
            return False
        
        # Vérifier que c'est un dossier
        if not os.path.isdir(folder_path):
            print(f"\n{self.t('error')} {self.t('folder_not_dir')}")
            input(f"\n{self.t('continue')}")
            return False
        
        # Vérifier la présence d'index.html à la racine
        index_path = os.path.join(folder_path, "index.html")
        if not os.path.exists(index_path):
            print(f"\n{self.t('index_missing')}")
            input(f"\n{self.t('continue')}")
            return False
        
        # Scanner tous les fichiers du dossier
        print(f"\n{self.t('scanning_folder')}")
        files_to_upload = []
        
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                # Calculer le chemin relatif depuis le dossier du projet
                relative_path = os.path.relpath(file_path, folder_path)
                files_to_upload.append((file_path, relative_path))
        
        print(f"✅ {len(files_to_upload)} {self.t('files_found')}")
        
        # Préparer les fichiers pour l'upload
        print(f"\n{self.t('uploading')}")
        
        try:
            # Préparer la liste de fichiers pour requests
            files_data = []
            for file_path, relative_path in files_to_upload:
                with open(file_path, 'rb') as f:
                    # Lire le contenu du fichier
                    file_content = f.read()
                    # Ajouter à la liste (nom du champ, (nom du fichier, contenu, type mime))
                    files_data.append(('files', (relative_path, file_content)))
            
            # Envoyer la requête
            response = requests.post(
                f"{self.api_url}/api/sites",
                headers=self.get_headers(),
                files=files_data,
                data={'name': name}
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"\n✅ {result['message']}")
                print(f"📁 Fichiers uploadés: {result.get('files_uploaded', 0)}")
                print(f"🌐 URL: {self.api_url}{result['url']}")
            else:
                print(f"\n{self.t('error')} {response.json().get('error', 'Unknown error')}")
        except Exception as e:
            print(f"\n{self.t('connection_error')} {e}")
        
        input(f"\n{self.t('continue')}")
    
    def delete_site_interactive(self):
        self.print_header()
        print(self.t("delete_title") + "\n")
        
        name = input(self.t("site_to_delete")).strip()
        confirm = input(f"{self.t('confirm_delete')} '{name}' ? {self.t('confirm_yes')}").strip().lower()
        
        if confirm not in ['oui', 'o', 'yes', 'y', 'non', 'n', 'no']:
            print(f"\n{self.t('error')} {self.t('confirm_yes')}")
            input(f"\n{self.t('continue')}")
            return
        
        if confirm in ['non', 'n', 'no']:
            print(f"\n{self.t('delete_cancelled')}")
            input(f"\n{self.t('continue')}")
            return
        
        try:
            response = requests.delete(
                f"{self.api_url}/api/sites/{name}",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                print(f"\n✅ {response.json()['message']}")
            else:
                print(f"\n{self.t('error')} {response.json().get('error', 'Unknown error')}")
        except Exception as e:
            print(f"\n{self.t('connection_error')} {e}")
        
        input(f"\n{self.t('continue')}")
    
    def update_email_interactive(self):
        self.print_header()
        print("📧 " + self.t("update_email") + "\n")
        
        new_email = input("📧 " + self.t("email")).strip()
        password = getpass.getpass(self.t("current_password"))
        
        try:
            response = requests.put(
                f"{self.api_url}/api/user/update-email",
                headers=self.get_headers(),
                json={"new_email": new_email, "password": password}
            )
            
            if response.status_code == 200:
                print(f"\n✅ {response.json()['message']}")
                self.config["email"] = new_email
                self.email = new_email
                self.save_config()
            else:
                print(f"\n{self.t('error')} {response.json().get('error', 'Unknown error')}")
        except Exception as e:
            print(f"\n{self.t('connection_error')} {e}")
        
        input(f"\n{self.t('continue')}")
    
    def update_password_interactive(self):
        self.print_header()
        print("🔑 " + self.t("update_password") + "\n")
        
        old_password = getpass.getpass(self.t("old_password"))
        new_password = getpass.getpass(self.t("new_password"))
        
        try:
            response = requests.put(
                f"{self.api_url}/api/user/update-password",
                headers=self.get_headers(),
                json={"old_password": old_password, "new_password": new_password}
            )
            
            if response.status_code == 200:
                print(f"\n✅ {response.json()['message']}")
                self.config["password"] = new_password
                self.password = new_password
                self.save_config()
            else:
                print(f"\n{self.t('error')} {response.json().get('error', 'Unknown error')}")
        except Exception as e:
            print(f"\n{self.t('connection_error')} {e}")
        
        input(f"\n{self.t('continue')}")
    
    def health_interactive(self):
        self.print_header()
        try:
            response = requests.get(f"{self.api_url}/health")
            if response.status_code == 200:
                print(f"{self.t('api_ok')} ({self.api_url})")
            else:
                print(self.t("api_error"))
        except Exception as e:
            print(f"{self.t('connection_error')} {e}")
        
        input(f"\n{self.t('continue')}")
    
    def run(self):
        try:
            while self.running:
                choice = self.show_main_menu()
                
                if not self.is_logged_in():
                    if choice == "1":
                        self.register_interactive()
                    elif choice == "2":
                        self.login_interactive()
                    elif choice == "3":
                        self.health_interactive()
                    elif choice == "9":
                        self.select_language()
                    elif choice == "0":
                        self.running = False
                    else:
                        self.print_header()
                        print(self.t("invalid_choice"))
                        input(f"\n{self.t('continue')}")
                else:
                    if choice == "1":
                        self.profile_interactive()
                    elif choice == "2":
                        self.list_sites_interactive()
                    elif choice == "3":
                        self.deploy_site_interactive()
                    elif choice == "4":
                        self.delete_site_interactive()
                    elif choice == "5":
                        self.update_email_interactive()
                    elif choice == "6":
                        self.update_password_interactive()
                    elif choice == "7":
                        self.logout_interactive()
                    elif choice == "8":
                        self.health_interactive()
                    elif choice == "9":
                        self.select_language()
                    elif choice == "0":
                        self.running = False
                    else:
                        self.print_header()
                        print(self.t("invalid_choice"))
                        input(f"\n{self.t('continue')}")
            
            self.clear_screen()
            print(self.t("goodbye"))
        
        except KeyboardInterrupt:
            self.clear_screen()
            print(f"\n{self.t('goodbye')}")
            sys.exit(0)

def main():
    cli = SwiftlyCLI()
    cli.select_language()
    cli.run()

if __name__ == "__main__":
    main()

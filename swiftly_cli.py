#!/usr/bin/env python3
"""
Swiftly CLI - Outil de gestion de sites statiques (Mode Interactif)
"""

import sys
import os
import json
import requests
import getpass

# Configuration
CONFIG_FILE = os.path.expanduser("~/.swiftly_config.json")
DEFAULT_API_URL = "http://localhost:5000"

class SwiftlyCLI:
    def __init__(self):
        self.config = self.load_config()
        self.api_url = self.config.get("api_url", DEFAULT_API_URL)
        self.email = self.config.get("email")
        self.password = self.config.get("password")
        self.running = True
    
    def load_config(self):
        """Charger la configuration depuis le fichier"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_config(self):
        """Sauvegarder la configuration"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
            os.chmod(CONFIG_FILE, 0o600)
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde de la configuration: {e}")
            return False
    
    def get_headers(self):
        """Obtenir les headers d'authentification"""
        if not self.email or not self.password:
            return None
        return {
            "X-User-Email": self.email,
            "X-User-Password": self.password
        }
    
    def is_logged_in(self):
        """Vérifier si l'utilisateur est connecté"""
        return self.email is not None and self.password is not None
    
    def clear_screen(self):
        """Effacer l'écran"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_header(self):
        """Afficher l'en-tête"""
        self.clear_screen()
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                     🚀 SWIFTLY CLI                          ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        if self.is_logged_in():
            print(f"👤 Connecté en tant que: {self.email}")
        else:
            print("👤 Non connecté")
        print()
    
    def show_main_menu(self):
        """Afficher le menu principal"""
        self.print_header()
        
        if not self.is_logged_in():
            print("📋 MENU PRINCIPAL:")
            print("  1. Créer un compte")
            print("  2. Se connecter")
            print("  3. Vérifier l'API (health)")
            print("  0. Quitter")
        else:
            print("📋 MENU PRINCIPAL:")
            print("  1. Voir mon profil")
            print("  2. Lister mes sites")
            print("  3. Déployer un nouveau site")
            print("  4. Supprimer un site")
            print("  5. Modifier mon email")
            print("  6. Modifier mon mot de passe")
            print("  7. Se déconnecter")
            print("  8. Vérifier l'API (health)")
            print("  0. Quitter")
        
        print()
        choice = input("Votre choix: ").strip()
        return choice
    
    def register_interactive(self):
        """Créer un compte (mode interactif)"""
        self.print_header()
        print("📝 CRÉATION DE COMPTE\n")
        
        email = input("Email: ").strip()
        password = getpass.getpass("Mot de passe (min 6 caractères): ")
        
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
                print("✅ Connexion automatique effectuée")
                input("\nAppuyez sur Entrée pour continuer...")
                return True
            else:
                print(f"\n❌ Erreur: {response.json().get('error', 'Erreur inconnue')}")
                input("\nAppuyez sur Entrée pour continuer...")
                return False
        except Exception as e:
            print(f"\n❌ Erreur de connexion à l'API: {e}")
            input("\nAppuyez sur Entrée pour continuer...")
            return False
    
    def login_interactive(self):
        """Se connecter (mode interactif)"""
        self.print_header()
        print("🔐 CONNEXION\n")
        
        email = input("Email: ").strip()
        password = getpass.getpass("Mot de passe: ")
        
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
                input("\nAppuyez sur Entrée pour continuer...")
                return True
            else:
                print(f"\n❌ Erreur: {response.json().get('error', 'Erreur inconnue')}")
                input("\nAppuyez sur Entrée pour continuer...")
                return False
        except Exception as e:
            print(f"\n❌ Erreur de connexion à l'API: {e}")
            input("\nAppuyez sur Entrée pour continuer...")
            return False
    
    def logout_interactive(self):
        """Se déconnecter"""
        self.config.pop("email", None)
        self.config.pop("password", None)
        self.email = None
        self.password = None
        self.save_config()
        self.print_header()
        print("✅ Déconnexion réussie")
        input("\nAppuyez sur Entrée pour continuer...")
    
    def profile_interactive(self):
        """Afficher le profil"""
        self.print_header()
        try:
            response = requests.get(
                f"{self.api_url}/api/user/profile",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                print("📋 PROFIL UTILISATEUR\n")
                print(f"📧 Email: {data['email']}")
                print(f"🌐 Nombre de sites: {data['total_sites']}")
                if data['sites']:
                    print(f"\n📦 Sites:")
                    for site in data['sites']:
                        print(f"   • {site}")
            else:
                print(f"❌ Erreur: {response.json().get('error', 'Erreur inconnue')}")
        except Exception as e:
            print(f"❌ Erreur de connexion à l'API: {e}")
        
        input("\nAppuyez sur Entrée pour continuer...")
    
    def list_sites_interactive(self):
        """Lister tous les sites"""
        self.print_header()
        try:
            response = requests.get(
                f"{self.api_url}/api/sites",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                sites = response.json()["sites"]
                if not sites:
                    print("📭 Vous n'avez aucun site déployé")
                else:
                    print("🌐 VOS SITES\n")
                    for name, data in sites.items():
                        filename = data.get("filename") if isinstance(data, dict) else data
                        print(f"📄 {name}")
                        print(f"   └─ Fichier: {filename}")
                        print(f"   └─ URL: {self.api_url}/sites/{name}\n")
            else:
                try:
                    error_msg = response.json().get('error', 'Erreur inconnue')
                except:
                    error_msg = f"Erreur HTTP {response.status_code}: {response.text}"
                print(f"❌ Erreur: {error_msg}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur de connexion à l'API: {e}")
        except Exception as e:
            print(f"❌ Erreur: {e}")
            print(f"   Réponse brute: {response.text if 'response' in locals() else 'Aucune réponse'}")
        
        input("\nAppuyez sur Entrée pour continuer...")
    
    def deploy_site_interactive(self):
        """Déployer un nouveau site"""
        self.print_header()
        print("🚀 DÉPLOYER UN SITE\n")
        
        name = input("Nom du site: ").strip()
        filepath = input("Chemin du fichier HTML: ").strip().strip("'\"")  # Enlever les guillemets
        
        if not os.path.exists(filepath):
            print(f"\n❌ Le fichier {filepath} n'existe pas")
            input("\nAppuyez sur Entrée pour continuer...")
            return False
        
        if not filepath.endswith('.html'):
            print(f"\n❌ Le fichier doit être un fichier HTML (.html)")
            input("\nAppuyez sur Entrée pour continuer...")
            return False
        
        try:
            with open(filepath, 'rb') as f:
                files = {'file': (os.path.basename(filepath), f, 'text/html')}
                data = {'name': name}
                
                response = requests.post(
                    f"{self.api_url}/api/sites",
                    headers=self.get_headers(),
                    files=files,
                    data=data
                )
        
            if response.status_code == 201:
                result = response.json()
                print(f"\n✅ {result['message']}")
                print(f"🌐 URL: {self.api_url}{result['url']}")
            else:
                print(f"\n❌ Erreur: {response.json().get('error', 'Erreur inconnue')}")
        except Exception as e:
            print(f"\n❌ Erreur de connexion à l'API: {e}")
    
        input("\nAppuyez sur Entrée pour continuer...")
    
    def delete_site_interactive(self):
        """Supprimer un site"""
        self.print_header()
        print("🗑️  SUPPRIMER UN SITE\n")
        
        name = input("Nom du site à supprimer: ").strip()
        confirm = input(f"Êtes-vous sûr de vouloir supprimer '{name}' ? (oui/non): ").strip().lower()
        
        if confirm not in ['oui', 'o', 'yes', 'y']:
            print("\n❌ Suppression annulée")
            input("\nAppuyez sur Entrée pour continuer...")
            return
        
        try:
            response = requests.delete(
                f"{self.api_url}/api/sites/{name}",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                print(f"\n✅ {response.json()['message']}")
            else:
                print(f"\n❌ Erreur: {response.json().get('error', 'Erreur inconnue')}")
        except Exception as e:
            print(f"\n❌ Erreur de connexion à l'API: {e}")
        
        input("\nAppuyez sur Entrée pour continuer...")
    
    def update_email_interactive(self):
        """Mettre à jour l'email"""
        self.print_header()
        print("📧 MODIFIER L'EMAIL\n")
        
        new_email = input("Nouvel email: ").strip()
        password = getpass.getpass("Mot de passe actuel: ")
        
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
                print(f"\n❌ Erreur: {response.json().get('error', 'Erreur inconnue')}")
        except Exception as e:
            print(f"\n❌ Erreur de connexion à l'API: {e}")
        
        input("\nAppuyez sur Entrée pour continuer...")
    
    def update_password_interactive(self):
        """Mettre à jour le mot de passe"""
        self.print_header()
        print("🔑 MODIFIER LE MOT DE PASSE\n")
        
        old_password = getpass.getpass("Ancien mot de passe: ")
        new_password = getpass.getpass("Nouveau mot de passe (min 6 caractères): ")
        
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
                print(f"\n❌ Erreur: {response.json().get('error', 'Erreur inconnue')}")
        except Exception as e:
            print(f"\n❌ Erreur de connexion à l'API: {e}")
        
        input("\nAppuyez sur Entrée pour continuer...")
    
    def health_interactive(self):
        """Vérifier la santé de l'API"""
        self.print_header()
        try:
            response = requests.get(f"{self.api_url}/health")
            if response.status_code == 200:
                print(f"✅ API opérationnelle ({self.api_url})")
            else:
                print(f"❌ API non accessible")
        except Exception as e:
            print(f"❌ Erreur de connexion à l'API: {e}")
        
        input("\nAppuyez sur Entrée pour continuer...")
    
    def run(self):
        """Boucle principale"""
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
                    elif choice == "0":
                        self.running = False
                    else:
                        self.print_header()
                        print("❌ Choix invalide")
                        input("\nAppuyez sur Entrée pour continuer...")
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
                    elif choice == "0":
                        self.running = False
                    else:
                        self.print_header()
                        print("❌ Choix invalide")
                        input("\nAppuyez sur Entrée pour continuer...")
            
            self.clear_screen()
            print("👋 Au revoir !")
        
        except KeyboardInterrupt:
            self.clear_screen()
            print("\n👋 Au revoir !")
            sys.exit(0)

def main():
    cli = SwiftlyCLI()
    cli.run()

if __name__ == "__main__":
    main()

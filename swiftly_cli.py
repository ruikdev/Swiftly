#!/usr/bin/env python3
"""
Swiftly CLI - Outil de gestion de sites statiques (Mode Interactif) - Multilingue
"""

import sys
import os
import json
import requests
import getpass
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt, Confirm
from rich import box
from rich.markdown import Markdown
from rich.text import Text

CONFIG_FILE = os.path.expanduser("~/.swiftly_config.json")
DEFAULT_API_URL = "https://swiftly.ruikdev.me"

TRANSLATIONS = {
    "fr": {
        "title": "🚀 SWIFTLY CLI",
        "logged_in": "👤 Connecté en tant que:",
        "not_logged_in": "👤 Non connecté",
        "main_menu": "📋 MENU PRINCIPAL:",
        "login": "1. Se connecter",
        "check_api": "8. Vérifier l'API (health)",
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
        "login": "1. Login",
        "check_api": "8. Check API (health)",
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
        self.console = Console()
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
        self.console.clear()
    
    def select_language(self):
        self.clear_screen()
        
        # Titre avec style
        title = Panel.fit(
            "[bold cyan]🚀 SWIFTLY CLI[/bold cyan]",
            border_style="bright_blue",
            box=box.DOUBLE
        )
        self.console.print(title)
        self.console.print()
        
        # Options de langue dans un panel
        lang_text = Text()
        lang_text.append("Select your language / Sélectionnez votre langue:\n\n", style="bold yellow")
        lang_text.append("1. ", style="bright_white")
        lang_text.append("Français (FR)\n", style="cyan")
        lang_text.append("2. ", style="bright_white")
        lang_text.append("English (EN)", style="cyan")
        
        panel = Panel(lang_text, border_style="yellow", box=box.ROUNDED)
        self.console.print(panel)
        self.console.print()
        
        choice = Prompt.ask(
            "[bold green]Votre choix / Your choice[/bold green]",
            choices=["1", "2"],
            default="1"
        )
        
        if choice == "2":
            self.language = "en"
        else:
            self.language = "fr"
        
        self.config["language"] = self.language
        self.save_config()
    
    def print_header(self):
        self.clear_screen()
        
        # Titre principal
        title = Panel.fit(
            f"[bold cyan]{self.t('title')}[/bold cyan]",
            border_style="bright_blue",
            box=box.DOUBLE
        )
        self.console.print(title)
        
        # Statut de connexion
        if self.is_logged_in():
            status_text = f"[green]✓[/green] [bold]{self.t('logged_in')}[/bold] [cyan]{self.email}[/cyan]"
        else:
            status_text = f"[yellow]○[/yellow] [bold]{self.t('not_logged_in')}[/bold]"
        
        self.console.print(Panel(status_text, border_style="bright_black", box=box.ROUNDED))
        self.console.print()
    
    def show_main_menu(self):
        self.print_header()
        
        # Créer un tableau pour le menu
        table = Table(show_header=False, box=box.ROUNDED, border_style="cyan", padding=(0, 2))
        table.add_column("Option", style="bright_white", width=4)
        table.add_column("Description", style="cyan")
        
        if not self.is_logged_in():
            table.add_row("1", " " + self.t("login"))
            table.add_row("8", "❤️  " + self.t("check_api"))
            table.add_row("9", "💬 " + self.t("change_lang"))
            table.add_row("0", "🚪 " + self.t("quit"))
        else:
            table.add_row("1", "👤 " + self.t("profile"))
            table.add_row("2", "📋 " + self.t("list_sites"))
            table.add_row("3", "🚀 " + self.t("deploy"))
            table.add_row("4", "🗑️  " + self.t("delete"))
            table.add_row("5", "📧 " + self.t("update_email"))
            table.add_row("6", "🔑 " + self.t("update_password"))
            table.add_row("7", "🚪 " + self.t("logout"))
            table.add_row("8", "❤️  " + self.t("check_api"))
            table.add_row("9", "💬 " + self.t("change_lang"))
            table.add_row("0", "🚪 " + self.t("quit"))
        
        menu_panel = Panel(table, title=f"[bold yellow]{self.t('main_menu')}[/bold yellow]", 
                          border_style="yellow", box=box.DOUBLE)
        self.console.print(menu_panel)
        self.console.print()
        
        choice = Prompt.ask("[bold green]" + self.t("choice") + "[/bold green]")
        return choice.strip()
    
    def register_interactive(self):
        self.print_header()
        
        panel = Panel(
            "[bold cyan]" + self.t("create_account") + "[/bold cyan]",
            border_style="cyan",
            box=box.DOUBLE
        )
        self.console.print(panel)
        self.console.print()
        
        email = Prompt.ask("[cyan]" + self.t("email") + "[/cyan]").strip()
        password = Prompt.ask("[cyan]" + self.t("password") + "[/cyan]", password=True)
        
        with self.console.status("[bold green]Création du compte en cours...[/bold green]", spinner="dots"):
            try:
                response = requests.post(
                    f"{self.api_url}/api/auth/register",
                    json={"email": email, "password": password}
                )
                
                if response.status_code == 201:
                    self.console.print(f"\n[bold green]✅ {response.json()['message']}[/bold green]")
                    self.config["email"] = email
                    self.config["password"] = password
                    self.email = email
                    self.password = password
                    self.save_config()
                    Prompt.ask(f"\n[dim]{self.t('continue')}[/dim]")
                    return True
                else:
                    self.console.print(f"\n[bold red]{self.t('error')} {response.json().get('error', 'Unknown error')}[/bold red]")
                    Prompt.ask(f"\n[dim]{self.t('continue')}[/dim]")
                    return False
            except Exception as e:
                self.console.print(f"\n[bold red]{self.t('connection_error')} {e}[/bold red]")
                Prompt.ask(f"\n[dim]{self.t('continue')}[/dim]")
                return False
    
    def login_interactive(self):
        self.print_header()
        
        panel = Panel(
            "[bold cyan]" + self.t("login_title") + "[/bold cyan]",
            border_style="cyan",
            box=box.DOUBLE
        )
        self.console.print(panel)
        self.console.print()
        
        email = Prompt.ask("[cyan]" + self.t("email") + "[/cyan]").strip()
        password = Prompt.ask("[cyan]" + self.t("password") + "[/cyan]", password=True)
        
        with self.console.status("[bold green]Connexion en cours...[/bold green]", spinner="dots"):
            try:
                response = requests.post(
                    f"{self.api_url}/api/auth/login",
                    json={"email": email, "password": password}
                )
                
                if response.status_code == 200:
                    self.console.print(f"\n[bold green]✅ {response.json()['message']}[/bold green]")
                    self.config["email"] = email
                    self.config["password"] = password
                    self.email = email
                    self.password = password
                    self.save_config()
                    Prompt.ask(f"\n[dim]{self.t('continue')}[/dim]")
                    return True
                else:
                    self.console.print(f"\n[bold red]{self.t('error')} {response.json().get('error', 'Unknown error')}[/bold red]")
                    Prompt.ask(f"\n[dim]{self.t('continue')}[/dim]")
                    return False
            except Exception as e:
                self.console.print(f"\n[bold red]{self.t('connection_error')} {e}[/bold red]")
                Prompt.ask(f"\n[dim]{self.t('continue')}[/dim]")
                return False
    
    def logout_interactive(self):
        self.config.pop("email", None)
        self.config.pop("password", None)
        self.email = None
        self.password = None
        self.save_config()
        self.print_header()
        self.console.print(f"[bold green]{self.t('logout_success')}[/bold green]")
        Prompt.ask(f"\n[dim]{self.t('continue')}[/dim]")
    
    def profile_interactive(self):
        self.print_header()
        
        with self.console.status("[bold green]Chargement du profil...[/bold green]", spinner="dots"):
            try:
                response = requests.get(
                    f"{self.api_url}/api/user/profile",
                    headers=self.get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Créer un tableau pour le profil
                    table = Table(show_header=False, box=box.ROUNDED, border_style="cyan")
                    table.add_column("Propriété", style="bold cyan", width=20)
                    table.add_column("Valeur", style="white")
                    
                    table.add_row("📧 Email", data['email'])
                    table.add_row("🌐 " + self.t('sites_count'), str(data['total_sites']))
                    
                    profile_panel = Panel(
                        table,
                        title=f"[bold yellow]{self.t('user_profile')}[/bold yellow]",
                        border_style="yellow",
                        box=box.DOUBLE
                    )
                    self.console.print(profile_panel)
                    
                    if data['sites']:
                        self.console.print()
                        sites_text = Text()
                        sites_text.append(f"\n{self.t('sites_list')}\n", style="bold cyan")
                        for site in data['sites']:
                            sites_text.append(f"   • {site}\n", style="green")
                        self.console.print(sites_text)
                else:
                    self.console.print(f"[bold red]{self.t('error')} {response.json().get('error', 'Unknown error')}[/bold red]")
            except Exception as e:
                self.console.print(f"[bold red]{self.t('connection_error')} {e}[/bold red]")
        
        Prompt.ask(f"\n[dim]{self.t('continue')}[/dim]")
    
    def list_sites_interactive(self):
        self.print_header()
        
        with self.console.status("[bold green]Chargement des sites...[/bold green]", spinner="dots"):
            try:
                response = requests.get(
                    f"{self.api_url}/api/sites",
                    headers=self.get_headers()
                )
                
                if response.status_code == 200:
                    sites = response.json()["sites"]
                    if not sites:
                        panel = Panel(
                            "[yellow]" + self.t("no_sites") + "[/yellow]",
                            border_style="yellow",
                            box=box.ROUNDED
                        )
                        self.console.print(panel)
                    else:
                        # Créer un tableau pour les sites
                        table = Table(box=box.ROUNDED, border_style="cyan", show_lines=True)
                        table.add_column("🌐 Nom du site", style="bold cyan", no_wrap=True)
                        table.add_column("📁 Type", style="yellow")
                        table.add_column("📊 Détails", style="white")
                        table.add_column("🔗 URL", style="green")
                        
                        for name, data in sites.items():
                            # Nouveau format avec dossier
                            if isinstance(data, dict) and "folder" in data:
                                folder = data.get("folder")
                                file_count = data.get("file_count", "?")
                                table.add_row(
                                    name,
                                    "📂 Dossier",
                                    f"Dossier: {folder}\nFichiers: {file_count}",
                                    f"{self.api_url}/sites/{name}"
                                )
                            # Ancien format avec fichier unique
                            elif isinstance(data, dict) and "filename" in data:
                                filename = data.get("filename")
                                table.add_row(
                                    name,
                                    "📝 Fichier",
                                    f"Fichier: {filename}",
                                    f"{self.api_url}/sites/{name}"
                                )
                        
                        sites_panel = Panel(
                            table,
                            title=f"[bold yellow]{self.t('your_sites')}[/bold yellow]",
                            border_style="yellow",
                            box=box.DOUBLE
                        )
                        self.console.print(sites_panel)
                else:
                    try:
                        error_msg = response.json().get('error', 'Unknown error')
                    except:
                        error_msg = f"HTTP {response.status_code}: {response.text}"
                    self.console.print(f"[bold red]{self.t('error')} {error_msg}[/bold red]")
            except Exception as e:
                self.console.print(f"[bold red]{self.t('connection_error')} {e}[/bold red]")
        
        Prompt.ask(f"\n[dim]{self.t('continue')}[/dim]")
    
    def deploy_site_interactive(self):
        self.print_header()
        
        panel = Panel(
            "[bold cyan]" + self.t("deploy_title") + "[/bold cyan]",
            border_style="cyan",
            box=box.DOUBLE
        )
        self.console.print(panel)
        self.console.print()
        
        name = Prompt.ask("[cyan]" + self.t("site_name") + "[/cyan]").strip()
        folder_path = Prompt.ask("[cyan]" + self.t("folder_path") + "[/cyan]").strip().strip("'\"")
        
        # Vérifier que le dossier existe
        if not os.path.exists(folder_path):
            self.console.print(f"\n[bold red]{self.t('error')} {self.t('folder_not_found')} {folder_path} {self.t('folder_not_exists')}[/bold red]")
            Prompt.ask(f"\n[dim]{self.t('continue')}[/dim]")
            return False
        
        # Vérifier que c'est un dossier
        if not os.path.isdir(folder_path):
            self.console.print(f"\n[bold red]{self.t('error')} {self.t('folder_not_dir')}[/bold red]")
            Prompt.ask(f"\n[dim]{self.t('continue')}[/dim]")
            return False
        
        # Vérifier la présence d'index.html à la racine
        index_path = os.path.join(folder_path, "index.html")
        if not os.path.exists(index_path):
            self.console.print(f"\n[bold red]{self.t('index_missing')}[/bold red]")
            Prompt.ask(f"\n[dim]{self.t('continue')}[/dim]")
            return False
        
        # Vérifier la structure des dossiers requis
        required_folders = ["css", "js", "images"]
        missing_folders = []
        
        for folder in required_folders:
            folder_full_path = os.path.join(folder_path, folder)
            if not os.path.exists(folder_full_path) or not os.path.isdir(folder_full_path):
                missing_folders.append(folder)
        
        if missing_folders:
            self.console.print(f"\n[bold red]❌ Structure invalide. Dossiers manquants: {', '.join(missing_folders)}[/bold red]")
            structure_text = Text()
            structure_text.append("📁 Structure requise:\n", style="bold yellow")
            structure_text.append("   ├── index.html\n", style="white")
            structure_text.append("   ├── css/\n", style="white")
            structure_text.append("   ├── js/\n", style="white")
            structure_text.append("   └── images/", style="white")
            self.console.print(Panel(structure_text, border_style="yellow", box=box.ROUNDED))
            Prompt.ask(f"\n[dim]{self.t('continue')}[/dim]")
            return False
        
        # Scanner tous les fichiers du dossier
        self.console.print(f"\n[bold cyan]{self.t('scanning_folder')}[/bold cyan]")
        files_to_upload = []
        
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                # Calculer le chemin relatif depuis le dossier du projet
                relative_path = os.path.relpath(file_path, folder_path)
                files_to_upload.append((file_path, relative_path))
        
        self.console.print(f"[bold green]✅ {len(files_to_upload)} {self.t('files_found')}[/bold green]")
        
        # Préparer les fichiers pour l'upload avec barre de progression
        try:
            files_data = []
            total_size = 0
            
            # Barre de progression pour la préparation des fichiers
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=self.console
            ) as progress:
                prep_task = progress.add_task("[cyan]Préparation des fichiers...", total=len(files_to_upload))
                
                for file_path, relative_path in files_to_upload:
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                        total_size += len(file_content)
                        files_data.append(('files', (relative_path, file_content)))
                    progress.update(prep_task, advance=1)
            
            # Afficher la taille totale
            size_mb = total_size / (1024 * 1024)
            if size_mb > 1:
                self.console.print(f"[bold cyan]📦 Taille totale: {size_mb:.2f} MB[/bold cyan]")
            else:
                self.console.print(f"[bold cyan]📦 Taille totale: {total_size / 1024:.2f} KB[/bold cyan]")
            
            # Envoyer la requête avec spinner
            with self.console.status("[bold green]⏳ Envoi en cours...[/bold green]", spinner="dots"):
                timeout = 30 if size_mb < 5 else 60
                response = requests.post(
                    f"{self.api_url}/api/sites",
                    headers=self.get_headers(),
                    files=files_data,
                    data={'name': name},
                    timeout=timeout
                )
            
            if response.status_code == 201:
                try:
                    result = response.json()
                    # Afficher le succès dans un panel
                    success_text = Text()
                    success_text.append(f"✅ {result['message']}\n\n", style="bold green")
                    success_text.append(f"📁 Fichiers uploadés: {result.get('files_uploaded', 0)}\n", style="cyan")
                    success_text.append(f"🌐 URL: ", style="yellow")
                    success_text.append(f"{self.api_url}{result['url']}", style="bold blue underline")
                    
                    success_panel = Panel(success_text, border_style="green", box=box.DOUBLE)
                    self.console.print(success_panel)
                except Exception as json_error:
                    self.console.print(f"\n[bold green]✅ Site déployé (Status: {response.status_code})[/bold green]")
                    self.console.print(f"[bold blue]🌐 URL: {self.api_url}/sites/{name}[/bold blue]")
            else:
                try:
                    error_msg = response.json().get('error', 'Unknown error')
                    self.console.print(f"\n[bold red]{self.t('error')} {error_msg}[/bold red]")
                except:
                    self.console.print(f"\n[bold red]{self.t('error')} HTTP {response.status_code}[/bold red]")
                    self.console.print(f"[dim]Réponse du serveur: {response.text[:200]}[/dim]")
        except requests.exceptions.RequestException as e:
            self.console.print(f"\n[bold red]{self.t('connection_error')} {e}[/bold red]")
        except Exception as e:
            self.console.print(f"\n[bold red]{self.t('error')} {type(e).__name__}: {e}[/bold red]")
        
        Prompt.ask(f"\n[dim]{self.t('continue')}[/dim]")
    
    def delete_site_interactive(self):
        self.print_header()
        
        panel = Panel(
            "[bold red]" + self.t("delete_title") + "[/bold red]",
            border_style="red",
            box=box.DOUBLE
        )
        self.console.print(panel)
        self.console.print()
        
        name = Prompt.ask("[yellow]" + self.t("site_to_delete") + "[/yellow]").strip()
        
        confirm = Confirm.ask(
            f"[bold red]{self.t('confirm_delete')} '{name}' ?[/bold red]",
            default=False
        )
        
        if not confirm:
            self.console.print(f"\n[yellow]{self.t('delete_cancelled')}[/yellow]")
            Prompt.ask(f"\n[dim]{self.t('continue')}[/dim]")
            return
        
        with self.console.status("[bold red]Suppression en cours...[/bold red]", spinner="dots"):
            try:
                response = requests.delete(
                    f"{self.api_url}/api/sites/{name}",
                    headers=self.get_headers()
                )
                
                if response.status_code == 200:
                    self.console.print(f"\n[bold green]✅ {response.json()['message']}[/bold green]")
                else:
                    self.console.print(f"\n[bold red]{self.t('error')} {response.json().get('error', 'Unknown error')}[/bold red]")
            except Exception as e:
                self.console.print(f"\n[bold red]{self.t('connection_error')} {e}[/bold red]")
        
        Prompt.ask(f"\n[dim]{self.t('continue')}[/dim]")
    
    def update_email_interactive(self):
        self.print_header()
        
        panel = Panel(
            "[bold cyan]📧 " + self.t("update_email") + "[/bold cyan]",
            border_style="cyan",
            box=box.DOUBLE
        )
        self.console.print(panel)
        self.console.print()
        
        new_email = Prompt.ask("[cyan]📧 " + self.t("email") + "[/cyan]").strip()
        password = Prompt.ask("[cyan]" + self.t("current_password") + "[/cyan]", password=True)
        
        with self.console.status("[bold green]Mise à jour de l'email...[/bold green]", spinner="dots"):
            try:
                response = requests.put(
                    f"{self.api_url}/api/user/update-email",
                    headers=self.get_headers(),
                    json={"new_email": new_email, "password": password}
                )
                
                if response.status_code == 200:
                    self.console.print(f"\n[bold green]✅ {response.json()['message']}[/bold green]")
                    self.config["email"] = new_email
                    self.email = new_email
                    self.save_config()
                else:
                    self.console.print(f"\n[bold red]{self.t('error')} {response.json().get('error', 'Unknown error')}[/bold red]")
            except Exception as e:
                self.console.print(f"\n[bold red]{self.t('connection_error')} {e}[/bold red]")
        
        Prompt.ask(f"\n[dim]{self.t('continue')}[/dim]")
    
    def update_password_interactive(self):
        self.print_header()
        
        panel = Panel(
            "[bold cyan]🔑 " + self.t("update_password") + "[/bold cyan]",
            border_style="cyan",
            box=box.DOUBLE
        )
        self.console.print(panel)
        self.console.print()
        
        old_password = Prompt.ask("[cyan]" + self.t("old_password") + "[/cyan]", password=True)
        new_password = Prompt.ask("[cyan]" + self.t("new_password") + "[/cyan]", password=True)
        
        with self.console.status("[bold green]Mise à jour du mot de passe...[/bold green]", spinner="dots"):
            try:
                response = requests.put(
                    f"{self.api_url}/api/user/update-password",
                    headers=self.get_headers(),
                    json={"old_password": old_password, "new_password": new_password}
                )
                
                if response.status_code == 200:
                    self.console.print(f"\n[bold green]✅ {response.json()['message']}[/bold green]")
                    self.config["password"] = new_password
                    self.password = new_password
                    self.save_config()
                else:
                    self.console.print(f"\n[bold red]{self.t('error')} {response.json().get('error', 'Unknown error')}[/bold red]")
            except Exception as e:
                self.console.print(f"\n[bold red]{self.t('connection_error')} {e}[/bold red]")
        
        Prompt.ask(f"\n[dim]{self.t('continue')}[/dim]")
    
    def health_interactive(self):
        self.print_header()
        
        with self.console.status("[bold cyan]Vérification de l'API...[/bold cyan]", spinner="dots"):
            try:
                response = requests.get(f"{self.api_url}/health")
                if response.status_code == 200:
                    health_text = Text()
                    health_text.append("✅ ", style="bold green")
                    health_text.append(self.t('api_ok'), style="green")
                    health_text.append(f"\n\n🌐 URL: {self.api_url}", style="cyan")
                    
                    panel = Panel(health_text, border_style="green", box=box.ROUNDED)
                    self.console.print(panel)
                else:
                    self.console.print(f"[bold red]{self.t('api_error')}[/bold red]")
            except Exception as e:
                self.console.print(f"[bold red]{self.t('connection_error')} {e}[/bold red]")
        
        Prompt.ask(f"\n[dim]{self.t('continue')}[/dim]")
    
    def run(self):
        try:
            while self.running:
                choice = self.show_main_menu()
                
                if not self.is_logged_in():
                    if choice == "1":
                        self.login_interactive()
                    elif choice == "8":
                        self.health_interactive()
                    elif choice == "9":
                        self.select_language()
                    elif choice == "0":
                        self.running = False
                    else:
                        self.print_header()
                        self.console.print(f"[bold red]{self.t('invalid_choice')}[/bold red]")
                        Prompt.ask(f"\n[dim]{self.t('continue')}[/dim]")
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
                        self.console.print(f"[bold red]{self.t('invalid_choice')}[/bold red]")
                        Prompt.ask(f"\n[dim]{self.t('continue')}[/dim]")
            
            self.clear_screen()
            # Message de fin stylisé
            goodbye_text = Text()
            goodbye_text.append("👋 ", style="bold yellow")
            goodbye_text.append(self.t("goodbye"), style="bold cyan")
            
            goodbye_panel = Panel.fit(
                goodbye_text,
                border_style="cyan",
                box=box.DOUBLE
            )
            self.console.print(goodbye_panel)
        
        except KeyboardInterrupt:
            self.clear_screen()
            goodbye_text = Text()
            goodbye_text.append("\n👋 ", style="bold yellow")
            goodbye_text.append(self.t("goodbye"), style="bold cyan")
            self.console.print(goodbye_text)
            sys.exit(0)

def main():
    cli = SwiftlyCLI()
    cli.select_language()
    cli.run()

if __name__ == "__main__":
    main()

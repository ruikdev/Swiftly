#!/usr/bin/env python3
"""
CLI pour tester l'API Swiftly
Usage:
    python cli.py list                          # Lister tous les sites
    python cli.py add <name> <file.html>        # Ajouter un site
    python cli.py delete <name>                 # Supprimer un site
    python cli.py health                        # Vérifier le statut de l'API
"""

import requests
import sys
import os
from pathlib import Path

API_BASE_URL = "http://localhost:5000"

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def health_check():
    """Vérifier si l'API est en ligne"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print_success("API is running!")
            print(response.json())
        else:
            print_error(f"API returned status code {response.status_code}")
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to API. Is the server running?")
    except Exception as e:
        print_error(f"Error: {e}")

def list_sites():
    """Lister tous les sites"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/sites")
        if response.status_code == 200:
            data = response.json()
            sites = data.get('sites', {})
            if sites:
                print_success(f"Found {len(sites)} site(s):")
                for name, filename in sites.items():
                    print(f"  • {name} → {filename}")
                    print(f"    URL: {API_BASE_URL}/sites/{name}")
            else:
                print_info("No sites found")
        else:
            print_error(f"Error: {response.status_code}")
            print(response.json())
    except Exception as e:
        print_error(f"Error: {e}")

def add_site(name, filepath):
    """Ajouter un nouveau site"""
    if not os.path.exists(filepath):
        print_error(f"File not found: {filepath}")
        return
    
    if not filepath.endswith('.html'):
        print_error("File must be an HTML file (.html)")
        return
    
    try:
        with open(filepath, 'rb') as f:
            files = {'file': (os.path.basename(filepath), f, 'text/html')}
            data = {'name': name}
            
            print_info(f"Uploading {filepath} as '{name}'...")
            response = requests.post(f"{API_BASE_URL}/api/sites", files=files, data=data)
            
            if response.status_code == 201:
                result = response.json()
                print_success(result['message'])
                print_info(f"Access your site at: {API_BASE_URL}{result['url']}")
            else:
                print_error(f"Error {response.status_code}")
                print(response.json())
    except Exception as e:
        print_error(f"Error: {e}")

def delete_site(name):
    """Supprimer un site"""
    try:
        print_info(f"Deleting site '{name}'...")
        response = requests.delete(f"{API_BASE_URL}/api/sites/{name}")
        
        if response.status_code == 200:
            result = response.json()
            print_success(result['message'])
        else:
            print_error(f"Error {response.status_code}")
            print(response.json())
    except Exception as e:
        print_error(f"Error: {e}")

def show_help():
    """Afficher l'aide"""
    print("""
🚀 Swiftly CLI - Test your API

Commands:
  health                      Check if API is running
  list                        List all sites
  add <name> <file.html>      Add a new site with HTML file
  delete <name>               Delete a site
  help                        Show this help message

Examples:
  python cli.py health
  python cli.py list
  python cli.py add mon-site index.html
  python cli.py delete mon-site

Configuration:
  API URL: {API_BASE_URL}
    """)

def main():
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "health":
        health_check()
    
    elif command == "list":
        list_sites()
    
    elif command == "add":
        if len(sys.argv) < 4:
            print_error("Usage: python cli.py add <name> <file.html>")
            sys.exit(1)
        name = sys.argv[2]
        filepath = sys.argv[3]
        add_site(name, filepath)
    
    elif command == "delete":
        if len(sys.argv) < 3:
            print_error("Usage: python cli.py delete <name>")
            sys.exit(1)
        name = sys.argv[2]
        delete_site(name)
    
    elif command == "help":
        show_help()
    
    else:
        print_error(f"Unknown command: {command}")
        show_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
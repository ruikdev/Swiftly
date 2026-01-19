#!/usr/bin/env python3
"""Script de migration des données JSON vers SQLite"""

import json
import os
import sys

# Ajouter le dossier parent au path pour importer swiftly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from swiftly.database import init_db, create_user, add_site_to_db
from swiftly.config import DATABASE_PATH

def migrate_from_json():
    """Migrer les données depuis les anciens fichiers JSON"""
    
    print("🔄 Début de la migration des données JSON vers SQLite...")
    
    # Initialiser la base de données
    print("📦 Initialisation de la base de données SQLite...")
    init_db()
    print("✅ Base de données initialisée")
    
    # Chemins des anciens fichiers
    users_json = "db/users.json"
    sites_json = "db/sites.json"
    
    users_migrated = 0
    sites_migrated = 0
    errors = []
    
    # Migrer les utilisateurs
    if os.path.exists(users_json):
        print(f"\n👥 Migration des utilisateurs depuis {users_json}...")
        try:
            with open(users_json, 'r') as f:
                old_users = json.load(f)
            
            for email, user_data in old_users.items():
                # Skip admin par défaut s'il existe déjà
                if email == "admin@admin":
                    print(f"  ⏭️  {email} (admin par défaut, déjà créé)")
                    continue
                
                # Le hash est déjà présent, on l'utilise directement
                # Mais create_user va hasher à nouveau, donc on doit utiliser une autre méthode
                # On va recréer avec un mot de passe temporaire et recommander de le changer
                
                # Pour l'instant, on ne peut pas migrer les mots de passe hashés
                # Les utilisateurs devront réinitialiser
                print(f"  ⚠️  {email} - Migration impossible (mot de passe hashé)")
                print(f"      → L'utilisateur devra créer un nouveau compte")
                errors.append(f"Utilisateur {email} : mot de passe hashé non migratable")
            
            print(f"✅ {users_migrated} utilisateurs migrés")
            if errors:
                print(f"⚠️  {len(errors)} utilisateurs nécessitent une action manuelle")
        
        except Exception as e:
            print(f"❌ Erreur lors de la migration des utilisateurs : {e}")
    else:
        print(f"ℹ️  Aucun fichier {users_json} trouvé, migration utilisateurs ignorée")
    
    # Migrer les sites
    if os.path.exists(sites_json):
        print(f"\n🌐 Migration des sites depuis {sites_json}...")
        try:
            with open(sites_json, 'r') as f:
                old_sites = json.load(f)
            
            for site_name, site_data in old_sites.items():
                if isinstance(site_data, dict):
                    folder = site_data.get("folder", site_name)
                    owner = site_data.get("owner", "admin@admin")
                    
                    # Migrer avec les nouveaux champs
                    success = add_site_to_db(
                        name=site_name,
                        folder=folder,
                        owner_email=owner,
                        auto_subdomain=None,  # Sera défini plus tard si nécessaire
                        custom_domain=None,
                        has_password_protection=False,
                        protection_password=None
                    )
                    
                    if success:
                        print(f"  ✅ {site_name} (propriétaire: {owner})")
                        sites_migrated += 1
                    else:
                        print(f"  ❌ {site_name} - Échec de la migration")
                        errors.append(f"Site {site_name} : échec de la migration")
                else:
                    print(f"  ⚠️  {site_name} - Format invalide, ignoré")
                    errors.append(f"Site {site_name} : format invalide")
            
            print(f"✅ {sites_migrated} sites migrés")
        
        except Exception as e:
            print(f"❌ Erreur lors de la migration des sites : {e}")
    else:
        print(f"ℹ️  Aucun fichier {sites_json} trouvé, migration sites ignorée")
    
    # Résumé
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DE LA MIGRATION")
    print("="*60)
    print(f"Utilisateurs migrés : {users_migrated}")
    print(f"Sites migrés : {sites_migrated}")
    
    if errors:
        print(f"\n⚠️  {len(errors)} erreurs/avertissements :")
        for error in errors[:10]:  # Afficher max 10 erreurs
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... et {len(errors) - 10} autres")
    
    print("\n✨ Migration terminée !")
    print(f"📁 Base de données SQLite : {DATABASE_PATH}")
    print("\n⚠️  IMPORTANT :")
    print("  - Les mots de passe hashés n'ont pas pu être migrés")
    print("  - Les utilisateurs doivent créer de nouveaux comptes")
    print("  - Ou utilisez le panel admin pour créer les comptes manuellement")
    print("  - Le compte admin par défaut : admin@admin / admin")
    print("\n💡 Conseil : Sauvegardez les anciens fichiers JSON avant de les supprimer")

if __name__ == "__main__":
    migrate_from_json()

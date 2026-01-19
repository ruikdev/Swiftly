"""Utilitaires pour la gestion SSH et Nginx"""

import paramiko
from swiftly.config import (
    ENABLE_SSH_MANAGEMENT, SSH_HOST, SSH_PORT, SSH_USER, 
    SSH_PASSWORD, SSH_KEY_PATH, NGINX_SITES_AVAILABLE,
    NGINX_SITES_ENABLED, DOCKER_CONTAINER_IP, DOCKER_CONTAINER_PORT
)

def get_ssh_client():
    """Créer une connexion SSH au serveur"""
    if not ENABLE_SSH_MANAGEMENT:
        return None
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        if SSH_KEY_PATH:
            client.connect(
                hostname=SSH_HOST,
                port=SSH_PORT,
                username=SSH_USER,
                key_filename=SSH_KEY_PATH
            )
        else:
            client.connect(
                hostname=SSH_HOST,
                port=SSH_PORT,
                username=SSH_USER,
                password=SSH_PASSWORD
            )
        return client
    except Exception as e:
        print(f"Erreur de connexion SSH: {e}")
        return None

def execute_ssh_command(client, command):
    """Exécuter une commande SSH"""
    if not client:
        return False, "SSH désactivé"
    
    try:
        stdin, stdout, stderr = client.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        return exit_status == 0, output if exit_status == 0 else error
    except Exception as e:
        return False, str(e)

def create_nginx_config(subdomain, site_name):
    """Créer le fichier de configuration Nginx pour un sous-domaine"""
    config = f"""server {{
    listen 80;
    server_name {subdomain};

    location / {{
        proxy_pass http://{DOCKER_CONTAINER_IP}:{DOCKER_CONTAINER_PORT}/sites/{site_name}/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
    return config

def setup_subdomain(subdomain, site_name):
    """Configurer un sous-domaine avec Nginx via SSH"""
    if not ENABLE_SSH_MANAGEMENT:
        return True, "SSH désactivé - configuration manuelle requise"
    
    client = get_ssh_client()
    if not client:
        return False, "Impossible de se connecter au serveur SSH"
    
    try:
        config_content = create_nginx_config(subdomain, site_name)
        config_file = f"{NGINX_SITES_AVAILABLE}/{subdomain}"
        enabled_link = f"{NGINX_SITES_ENABLED}/{subdomain}"
        
        # Créer le fichier de configuration
        create_cmd = f"echo '{config_content}' | sudo tee {config_file}"
        success, output = execute_ssh_command(client, create_cmd)
        if not success:
            client.close()
            return False, f"Erreur lors de la création du fichier Nginx: {output}"
        
        # Créer le lien symbolique
        link_cmd = f"sudo ln -sf {config_file} {enabled_link}"
        success, output = execute_ssh_command(client, link_cmd)
        if not success:
            client.close()
            return False, f"Erreur lors de la création du lien symbolique: {output}"
        
        # Tester la configuration Nginx
        test_cmd = "sudo nginx -t"
        success, output = execute_ssh_command(client, test_cmd)
        if not success:
            # Rollback
            execute_ssh_command(client, f"sudo rm {config_file} {enabled_link}")
            client.close()
            return False, f"Configuration Nginx invalide: {output}"
        
        # Recharger Nginx
        reload_cmd = "sudo systemctl reload nginx"
        success, output = execute_ssh_command(client, reload_cmd)
        if not success:
            client.close()
            return False, f"Erreur lors du rechargement de Nginx: {output}"
        
        client.close()
        return True, "Sous-domaine configuré avec succès"
    
    except Exception as e:
        if client:
            client.close()
        return False, str(e)

def remove_subdomain(subdomain):
    """Supprimer la configuration d'un sous-domaine"""
    if not ENABLE_SSH_MANAGEMENT:
        return True, "SSH désactivé - suppression manuelle requise"
    
    client = get_ssh_client()
    if not client:
        return False, "Impossible de se connecter au serveur SSH"
    
    try:
        config_file = f"{NGINX_SITES_AVAILABLE}/{subdomain}"
        enabled_link = f"{NGINX_SITES_ENABLED}/{subdomain}"
        
        # Supprimer le lien symbolique
        execute_ssh_command(client, f"sudo rm -f {enabled_link}")
        
        # Supprimer le fichier de configuration
        execute_ssh_command(client, f"sudo rm -f {config_file}")
        
        # Recharger Nginx
        reload_cmd = "sudo systemctl reload nginx"
        success, output = execute_ssh_command(client, reload_cmd)
        
        client.close()
        return True, "Sous-domaine supprimé avec succès"
    
    except Exception as e:
        if client:
            client.close()
        return False, str(e)

def get_dns_instructions(domain, is_custom=False):
    """Obtenir les instructions DNS pour configurer le domaine"""
    if is_custom:
        # Instructions pour un domaine custom
        instructions = {
            "type": "A",
            "domain": domain,
            "value": SSH_HOST if ENABLE_SSH_MANAGEMENT else "VOTRE_IP_SERVEUR",
            "ttl": "3600",
            "instructions": [
                f"Configuration DNS requise pour votre domaine custom:",
                f"",
                f"1. Connectez-vous au panel DNS de votre registrar de domaine",
                f"2. Ajoutez un enregistrement de type A ou CNAME:",
                f"   - Type: A",
                f"   - Nom/Host: {domain.split('.')[0]} (ou @ si domaine racine)",
                f"   - Valeur/Target: {SSH_HOST if ENABLE_SSH_MANAGEMENT else 'VOTRE_IP_SERVEUR'}",
                f"   - TTL: 3600 (ou par défaut)",
                f"3. Sauvegardez et attendez la propagation DNS (quelques minutes à 48h)",
                f"",
                f"Note: La configuration Nginx a été créée automatiquement sur le serveur."
            ]
        }
    else:
        # Le sous-domaine automatique est déjà géré par le wildcard
        instructions = {
            "type": "auto",
            "domain": domain,
            "instructions": [
                f"✓ Sous-domaine automatique configuré: {domain}",
                f"",
                f"Aucune configuration DNS requise !",
                f"Le wildcard DNS est déjà configuré par l'administrateur.",
                f"",
                f"Votre site est accessible immédiatement à l'adresse:",
                f"https://{domain}"
            ]
        }
    return instructions

"""Modèle site"""

class Site:
    """Classe représentant un site"""
    
    @staticmethod
    def create_site_dict(folder, owner, is_spa=False):
        """Créer un dictionnaire site"""
        return {
            "folder": folder,
            "owner": owner,
            "is_spa": is_spa
        }
    
    @staticmethod
    def is_valid_format(site_data):
        """Vérifier si le site est au nouveau format"""
        return isinstance(site_data, dict) and "folder" in site_data

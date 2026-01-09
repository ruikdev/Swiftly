from flask import Flask, jsonify, request, send_from_directory, abort, render_template
import json
import os

app = Flask(__name__)
db_sites = "db/sites.json"
sites_folder = "sites"

# Charger la base de données dans une variable
def load_db():
    if os.path.exists(db_sites):
        with open(db_sites, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {} # Retourne un dictionnaire vide si le fichier est mal formé
    return {}

sites = load_db()

def save_db():
    try:
        with open(db_sites, 'w') as f:
            json.dump(sites, f, indent=4)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde : {e}")

def add_site_to_db(name, filename):
    sites[name] = filename
    save_db()
    return True

def get_all_sites():
    return sites

def delete_site_from_db(name):
    if name in sites:
        del sites[name]
        save_db()
        return True
    return False

@app.route("/")
def index():
    return render_template("base.html")

@app.route("/health")
def health():
    return jsonify(status="ok")

# Route pour servir les sites statiques
@app.route("/sites/<site_name>")
def serve_site(site_name):
    """Servir une page HTML depuis le dossier sites/"""
    # Vérifier si le site existe dans la DB
    if site_name not in sites:
        abort(404, description=f"Le site '{site_name}' n'existe pas")

    filename = sites[site_name]
    filepath = os.path.join(sites_folder, filename)

    # Vérifier si le fichier existe
    if not os.path.exists(filepath):
        abort(404, description=f"Le fichier '{filename}' n'existe pas")

    # Servir le fichier HTML
    return send_from_directory(sites_folder, filename)

# API : Lister tous les sites
@app.route("/api/sites", methods=["GET"])
def list_sites():
    """Retourner la liste de tous les sites"""
    return jsonify(sites=get_all_sites())

# API : Ajouter un nouveau site
@app.route("/api/sites", methods=["POST"])
def create_site():
    """Ajouter un nouveau site avec upload de fichier HTML"""
    
    # Vérifier si un fichier est présent dans la requête
    if 'file' in request.files:
        # Mode upload: on reçoit le fichier HTML
        file = request.files['file']
        name = request.form.get('name')
        
        # Validation
        if not name:
            return jsonify(error="Le champ 'name' est requis"), 400
        
        if file.filename == '':
            return jsonify(error="Aucun fichier sélectionné"), 400
        
        # Vérifier si le site existe déjà
        if name in sites:
            return jsonify(error=f"Le site '{name}' existe déjà"), 409
        
        # Vérifier l'extension du fichier
        if not file.filename.endswith('.html'):
            return jsonify(error="Le fichier doit être un fichier HTML (.html)"), 400
        
        # Générer un nom de fichier sécurisé
        from werkzeug.utils import secure_filename
        filename = secure_filename(file.filename)
        
        # Si le nom du site est différent du nom de fichier, on peut utiliser le nom du site
        # Pour éviter les conflits, on peut utiliser: name.html
        filename = f"{secure_filename(name)}.html"
        
        # Sauvegarder le fichier
        filepath = os.path.join(sites_folder, filename)
        
        # Créer le dossier sites s'il n'existe pas
        os.makedirs(sites_folder, exist_ok=True)
        
        try:
            file.save(filepath)
        except Exception as e:
            return jsonify(error=f"Erreur lors de la sauvegarde du fichier: {str(e)}"), 500
        
        # Ajouter le site à la DB
        add_site_to_db(name, filename)
        return jsonify(
            message=f"Site '{name}' ajouté avec succès",
            site={name: filename},
            url=f"/sites/{name}"
        ), 201
    
    else:
        return jsonify(error=f"Votre requete ne contient pas de fichier html"), 404

# API : Supprimer un site
@app.route("/api/sites/<site_name>", methods=["DELETE"])
def remove_site(site_name):
    """Supprimer un site"""
    if delete_site_from_db(site_name):
        return jsonify(message=f"Site '{site_name}' supprimé avec succès")
    return jsonify(error=f"Le site '{site_name}' n'existe pas"), 404



if __name__ == "__main__":
    # Test rapide : ajout du site exemple au démarrage
    add_site_to_db("exemple", "exemple.html")
    save_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
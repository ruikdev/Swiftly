from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)
db_sites = "db/sites.json"

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
    return "Bonjour depuis Flask !"

@app.route("/health")
def health():
    return jsonify(status="ok")



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
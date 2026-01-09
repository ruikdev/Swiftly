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

@app.route("/")
def index():
    return "Bonjour depuis Flask !"

@app.route("/health")
def health():
    return jsonify(status="ok")



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
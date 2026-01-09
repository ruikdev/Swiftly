from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/")
def index():
    return "Bonjour depuis Flask !"

@app.route("/health")
def health():
    return jsonify(status="ok")

@app.route("/echo", methods=["POST"])
def echo():
    data = request.get_json(silent=True)
    return jsonify(received=data if data is not None else {})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
#!/usr/bin/env python3
"""Point d'entrée de l'application Swiftly"""

from swiftly import create_app
from swiftly.config import DEBUG, HOST, PORT

app = create_app()

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)
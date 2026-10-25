"""Arranca el panel administrativo:  python app.py  →  http://localhost:5000"""

from servidor_admin import create_app

if __name__ == "__main__":
    create_app().run(port=5000, debug=True)

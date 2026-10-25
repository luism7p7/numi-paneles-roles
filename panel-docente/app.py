"""Arranca el panel docente:  python app.py  →  http://localhost:5001"""

from servidor_docente import create_app

if __name__ == "__main__":
    create_app().run(port=5001, debug=True)

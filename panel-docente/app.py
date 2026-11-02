"""Arranca el panel docente:  python app.py  →  http://localhost:5001"""

import sys
from pathlib import Path

# El paquete `comun/` (lo que comparten los dos paneles) está en la carpeta raíz del proyecto
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from servidor_docente import create_app

if __name__ == "__main__":
    create_app().run(port=5001, debug=True)

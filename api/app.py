"""Arranca la API:  python app.py  →  http://localhost:5001/api/v1/salud"""

import sys
from pathlib import Path

# La carpeta `api/` tiene que estar en la ruta de Python para poder importar el paquete `app`
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import crear_app

if __name__ == "__main__":
    crear_app().run(port=5001, debug=True)

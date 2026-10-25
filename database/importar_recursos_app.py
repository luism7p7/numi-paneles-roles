"""Importa a Recursos (panel administrativo) las imágenes, audios y videos reales de la app.

Copia cada archivo de frontend/assets de la app a panel-administrativo/uploads/app/
y lo registra en la tabla `recursos` con la carpeta de su materia. Se puede
ejecutar varias veces: solo agrega lo nuevo.

Uso, desde la raíz del proyecto:
    python database/importar_recursos_app.py
    python database/importar_recursos_app.py --app "C:/ruta/a/app-educativa-medellin/frontend"
    python database/importar_recursos_app.py --conservar-ejemplos   # no borra los 21 recursos de ejemplo
"""

import argparse
import os
import shutil
from pathlib import Path

from init_db import CARPETA, conectar

CARPETA_UPLOADS = CARPETA.parent / "panel-administrativo" / "uploads"
APP_POR_DEFECTO = Path.home() / "Documents" / "app-educativa-medellin" / "frontend"

TIPOS = {".png": "Imagen", ".jpg": "Imagen", ".jpeg": "Imagen", ".mp3": "Audio", ".mp4": "Video"}

# Fragmento de la ruta en la app → carpeta del panel (la que usa el constructor)
MATERIAS = {
    "ciencias": "actividades/ciencias",
    "matematicas": "actividades/matematicas",
    "espanol": "actividades/espanol",
    "sociales": "actividades/sociales",
    "ingles": "actividades/ingles",
}


def clasificar(relativa):
    """'images/actividades/ciencias_naturales/pantalla 1/perro.png'
    → ('actividades/ciencias', 'pantalla 1/perro.png')"""
    partes = relativa.split("/")
    for i, parte in enumerate(partes[:-1]):
        for clave, carpeta in MATERIAS.items():
            if parte.lower().startswith(clave):
                return carpeta, "/".join(partes[i + 1:])
    return "app/general", relativa  # fondos, avatares, música, sonidos de correcto/incorrecto...


def importar(cur, assets, uploads, quitar_ejemplos=True):
    # Las bases creadas antes de esta versión no aceptaban videos
    cur.execute("ALTER TABLE recursos MODIFY tipo ENUM('Imagen', 'Audio', 'Video') NOT NULL")
    borrados = 0
    if quitar_ejemplos:
        # Los recursos de ejemplo no tienen archivo; sus vínculos con actividades se borran en cascada
        borrados = cur.execute("DELETE FROM recursos WHERE archivo IS NULL")

    nuevos = existentes = 0
    for ruta in sorted(assets.rglob("*")):
        tipo = TIPOS.get(ruta.suffix.lower())
        if tipo is None or not ruta.is_file():
            continue
        relativa = ruta.relative_to(assets).as_posix()
        carpeta, nombre = clasificar(relativa)
        archivo = f"app/{relativa}"
        destino = uploads / archivo
        if not destino.exists() or destino.stat().st_size != ruta.stat().st_size:
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ruta, destino)
        cur.execute("SELECT id FROM recursos WHERE carpeta = %s AND nombre = %s", (carpeta, nombre[:120]))
        if cur.fetchone():
            existentes += 1
            continue
        cur.execute(
            "INSERT INTO recursos (nombre, tipo, carpeta, archivo) VALUES (%s, %s, %s, %s)",
            (nombre[:120], tipo, carpeta, archivo),
        )
        nuevos += 1
    return {"nuevos": nuevos, "existentes": existentes, "ejemplos_borrados": borrados}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Importa los recursos reales de la app al panel administrativo.")
    parser.add_argument("--app", type=Path, default=APP_POR_DEFECTO, help="carpeta frontend de la app")
    parser.add_argument("--conservar-ejemplos", action="store_true", help="no borrar los recursos de ejemplo")
    args = parser.parse_args()

    assets = args.app / "assets"
    if not assets.is_dir():
        raise SystemExit(f"No encuentro {assets}. Indica la carpeta frontend de la app con --app.")
    con = conectar(os.environ.get("DB_NAME", "numi"))
    try:
        with con.cursor() as cur:
            resultado = importar(cur, assets, CARPETA_UPLOADS, not args.conservar_ejemplos)
        con.commit()
    finally:
        con.close()
    print(f"Recursos nuevos: {resultado['nuevos']} · ya estaban: {resultado['existentes']} · "
          f"ejemplos borrados: {resultado['ejemplos_borrados']}")

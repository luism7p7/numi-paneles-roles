"""Reglas de los recursos: catálogo, compatibilidad con las versiones de la app y subida de archivos."""

import re
from urllib.parse import quote

from flask import current_app
from werkzeug.utils import secure_filename

from app.compartido.textos import version
from app.excepciones import ErrorDeDatos

from . import repositorios as repo

EXTENSIONES = {".png": "Imagen", ".jpg": "Imagen", ".jpeg": "Imagen", ".mp3": "Audio", ".mp4": "Video"}
CARPETA_VALIDA = re.compile(r"^actividades/[a-z0-9_-]{1,40}$")
PREFIJO_ARCHIVOS = "/api/v1/archivos"


def versiones_en_uso():
    return repo.versiones_en_uso()


def equipos_por_debajo_de(minima, versiones=None):
    versiones = repo.versiones_en_uso() if versiones is None else versiones
    return sum(n for v, n in versiones.items() if version(v) < version(minima))


def recurso_json(fila, versiones):
    incompatibles = equipos_por_debajo_de(fila["version_minima"], versiones) if fila["version_minima"] else 0
    return {
        "id": fila["id"],
        "nombre": fila["nombre"],
        "tipo": fila["tipo"],
        "carpeta": fila["carpeta"],
        "emoji": fila["emoji"],
        # quote(): las carpetas de la app tienen espacios ("pantalla 1")
        "url": f"{PREFIJO_ARCHIVOS}/{quote(fila['archivo'])}" if fila["archivo"] else None,
        "version_minima": fila["version_minima"],
        "compatibilidad": f"Desde v{fila['version_minima']}" if fila["version_minima"] else "Todas las versiones",
        # Un recurso nuevo no se puede usar mientras haya equipos que no lo muestran
        "compatible": incompatibles == 0,
        "equipos_incompatibles": incompatibles,
    }


def listar():
    versiones = repo.versiones_en_uso()
    minima = current_app.config["VERSION_MINIMA_ACTIVIDADES"]
    viejas = sorted((v for v in versiones if version(v) < version(minima)), key=version)
    return {
        "recursos": [recurso_json(f, versiones) for f in repo.listar()],
        "equipos_desactualizados": equipos_por_debajo_de(minima, versiones),
        "version_desactualizada": viejas[0] if viejas else None,
    }


def elegidos(ids):
    """Los recursos con esos ids, ya con su compatibilidad. Falla si alguno ya no existe."""
    encontrados = repo.por_ids(ids) if ids else []
    if len(encontrados) != len(ids):
        raise ErrorDeDatos("Uno de los recursos seleccionados ya no existe.")
    versiones = repo.versiones_en_uso()
    return [(r, recurso_json(r, versiones)) for r in encontrados]


def subir(archivos, carpeta):
    """Guarda los archivos PNG, JPG, MP3 o MP4 en la carpeta y los registra. Devuelve (subidos, omitidos)."""
    if not archivos or not any(a.filename for a in archivos):
        raise ErrorDeDatos("Selecciona al menos un archivo PNG, JPG, MP3 o MP4.")
    carpeta = (carpeta or "").strip() or "actividades/general"
    if not CARPETA_VALIDA.match(carpeta):
        raise ErrorDeDatos("La carpeta no es válida.")

    destino = current_app.config["CARPETA_UPLOADS"] / carpeta
    subidos, omitidos = [], []
    for archivo in archivos:
        nombre = secure_filename(archivo.filename or "").lower()
        extension = "." + nombre.rsplit(".", 1)[-1] if "." in nombre else ""
        if extension not in EXTENSIONES:
            omitidos.append(f"{archivo.filename}: solo se aceptan PNG, JPG, MP3 o MP4")
            continue
        if repo.existe_en_carpeta(carpeta, nombre):
            omitidos.append(f"{nombre}: ya existe en {carpeta}")
            continue
        destino.mkdir(parents=True, exist_ok=True)
        archivo.save(destino / nombre)
        tipo = EXTENSIONES[extension]
        repo.crear(nombre, tipo, carpeta, "🖼️" if tipo == "Imagen" else None, f"{carpeta}/{nombre}")
        subidos.append(nombre)
    return subidos, omitidos

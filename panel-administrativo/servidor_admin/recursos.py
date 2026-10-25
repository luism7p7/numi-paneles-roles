"""Recursos: imágenes y audios que usan las actividades."""

import re
from urllib.parse import quote

from flask import Blueprint, current_app, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

from .db import consultar, ejecutar
from .utilidades import ErrorDeDatos, version

bp = Blueprint("recursos", __name__)

EXTENSIONES = {".png": "Imagen", ".jpg": "Imagen", ".jpeg": "Imagen", ".mp3": "Audio", ".mp4": "Video"}
CARPETA_VALIDA = re.compile(r"^actividades/[a-z0-9_-]{1,40}$")


def versiones_en_uso():
    """{'1.4.0': 549, '1.3.2': 142, ...}: cuántos equipos tienen cada versión de la app."""
    filas = consultar(
        "SELECT version_app, COUNT(*) AS equipos FROM estudiantes WHERE version_app IS NOT NULL GROUP BY version_app"
    )
    return {f["version_app"]: f["equipos"] for f in filas}


def equipos_por_debajo_de(minima, versiones=None):
    versiones = versiones_en_uso() if versiones is None else versiones
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
        "url": f"/uploads/{quote(fila['archivo'])}" if fila["archivo"] else None,
        "version_minima": fila["version_minima"],
        "compatibilidad": f"Desde v{fila['version_minima']}" if fila["version_minima"] else "Todas las versiones",
        # Un recurso nuevo no se puede usar mientras haya equipos que no lo muestran
        "compatible": incompatibles == 0,
        "equipos_incompatibles": incompatibles,
    }


@bp.get("/api/recursos")
def listar():
    versiones = versiones_en_uso()
    filas = consultar("SELECT * FROM recursos ORDER BY carpeta, tipo, id")
    minima = current_app.config["VERSION_MINIMA_ACTIVIDADES"]
    viejas = sorted((v for v in versiones if version(v) < version(minima)), key=version)
    return jsonify(
        recursos=[recurso_json(f, versiones) for f in filas],
        equipos_desactualizados=equipos_por_debajo_de(minima, versiones),
        version_desactualizada=viejas[0] if viejas else None,
    )


@bp.post("/api/recursos")
def subir():
    archivos = request.files.getlist("archivos")
    if not archivos or not any(a.filename for a in archivos):
        raise ErrorDeDatos("Selecciona al menos un archivo PNG, JPG, MP3 o MP4.")
    carpeta = request.form.get("carpeta", "").strip() or "actividades/general"
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
        if consultar("SELECT 1 FROM recursos WHERE carpeta = %s AND nombre = %s", (carpeta, nombre), uno=True):
            omitidos.append(f"{nombre}: ya existe en {carpeta}")
            continue
        destino.mkdir(parents=True, exist_ok=True)
        archivo.save(destino / nombre)
        tipo = EXTENSIONES[extension]
        ejecutar(
            "INSERT INTO recursos (nombre, tipo, carpeta, emoji, archivo) VALUES (%s, %s, %s, %s, %s)",
            (nombre, tipo, carpeta, "🖼️" if tipo == "Imagen" else None, f"{carpeta}/{nombre}"),
        )
        subidos.append(nombre)
    return jsonify(subidos=subidos, omitidos=omitidos), 201 if subidos else 400


@bp.get("/uploads/<path:archivo>")
def archivo_subido(archivo):
    return send_from_directory(current_app.config["CARPETA_UPLOADS"], archivo)

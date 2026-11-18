"""Rutas de recursos: catálogo y subida (administrador) y descarga de los archivos (pública)."""

from flask import Blueprint, current_app, request, send_from_directory

from app.respuestas import exito, fallo
from app.seguridad import requiere_admin

from . import servicios

recursos_bp = Blueprint("recursos", __name__)
archivos_bp = Blueprint("archivos", __name__)


@recursos_bp.get("")
@requiere_admin
def listar(usuario_id):
    return exito(servicios.listar())


@recursos_bp.post("")
@requiere_admin
def subir(usuario_id):
    subidos, omitidos = servicios.subir(request.files.getlist("archivos"), request.form.get("carpeta"))
    if not subidos:
        return fallo("No se subió ningún archivo.", 400, {"omitidos": omitidos})
    return exito({"subidos": subidos, "omitidos": omitidos}, codigo=201)


@archivos_bp.get("/<path:archivo>")
def archivo_subido(archivo):
    """Las imágenes y audios se muestran con <img> y <audio>, que no pueden mandar el token: son públicos."""
    return send_from_directory(current_app.config["CARPETA_UPLOADS"], archivo)

"""Rutas del monitoreo técnico y de los informes de sincronización (solo administrador)."""

from flask import Blueprint, Response

from app.respuestas import exito
from app.seguridad import requiere_admin

from . import servicios

monitoreo_bp = Blueprint("monitoreo", __name__)
informes_bp = Blueprint("informes", __name__)


@monitoreo_bp.get("")
@requiere_admin
def resumen(usuario_id):
    return exito(servicios.resumen())


@informes_bp.post("")
@requiere_admin
def generar_informe(usuario_id):
    return exito(servicios.generar_informe(), "Informe generado.", 201)


@informes_bp.get("/<int:informe_id>/descargar")
@requiere_admin
def descargar_informe(usuario_id, informe_id):
    contenido, nombre, tipo = servicios.informe_para_descargar(informe_id)
    return Response(contenido, mimetype=tipo, headers={"Content-Disposition": f'attachment; filename="{nombre}"'})

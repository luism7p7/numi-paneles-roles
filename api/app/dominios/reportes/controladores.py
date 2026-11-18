"""Rutas de los reportes del grupo (solo docente)."""

from flask import Blueprint, request

from app.compartido.archivos import enviar
from app.compartido.validaciones import cargar
from app.dominios.grupos.contexto import con_grupo_activo
from app.respuestas import exito
from app.seguridad import requiere_docente

from . import servicios
from .dtos import DescargarReporteDTO

reportes_bp = Blueprint("reportes", __name__)


@reportes_bp.get("")
@requiere_docente
@con_grupo_activo
def datos_reporte(usuario_id, grupo):
    return exito(servicios.datos_reporte(grupo, request.args.get("periodo")))


@reportes_bp.get("/descargar")
@requiere_docente
@con_grupo_activo
def descargar(usuario_id, grupo):
    datos = cargar(DescargarReporteDTO(), request.args.to_dict())
    return enviar(*servicios.descargar(grupo, datos))

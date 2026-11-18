"""Ruta de la pantalla de Inicio (solo administrador)."""

from flask import Blueprint

from app.respuestas import exito
from app.seguridad import requiere_admin

from . import servicios

inicio_bp = Blueprint("inicio", __name__)


@inicio_bp.get("")
@requiere_admin
def resumen(usuario_id):
    return exito(servicios.resumen())

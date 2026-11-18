"""Rutas del perfil del docente y del cambio de grupo."""

from flask import Blueprint, request

from app.compartido.validaciones import cargar
from app.respuestas import exito
from app.seguridad import requiere_docente

from . import servicios
from .dtos import CambiarGrupoDTO

docente_bp = Blueprint("docente", __name__)


@docente_bp.get("/me")
@requiere_docente
def perfil(usuario_id):
    return exito(servicios.perfil(usuario_id, request.headers.get("X-Grupo-Id")))


@docente_bp.post("/grupo-activo")
@requiere_docente
def cambiar_grupo(usuario_id):
    datos = cargar(CambiarGrupoDTO(), request.get_json(silent=True))
    return exito(servicios.cambiar_grupo(usuario_id, datos["grupo_id"]))

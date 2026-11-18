"""Rutas de la gestión del grupo (solo docente)."""

from flask import Blueprint, request

from app.compartido.validaciones import cargar
from app.dominios.grupos.contexto import con_grupo_activo
from app.respuestas import exito
from app.seguridad import requiere_docente

from . import servicios
from .dtos import AsistenteIaDTO

gestion_bp = Blueprint("gestion", __name__)


@gestion_bp.get("")
@requiere_docente
@con_grupo_activo
def ver(usuario_id, grupo):
    return exito(servicios.ver(grupo))


@gestion_bp.post("/codigo")
@requiere_docente
@con_grupo_activo
def renovar_codigo(usuario_id, grupo):
    return exito(servicios.renovar_codigo(grupo), "Código nuevo generado.")


@gestion_bp.patch("/ia")
@requiere_docente
@con_grupo_activo
def cambiar_ia(usuario_id, grupo):
    datos = cargar(AsistenteIaDTO(), request.get_json(silent=True))
    return exito(servicios.cambiar_ia(grupo, datos["activada"]))


@gestion_bp.post("/paquete")
@requiere_docente
@con_grupo_activo
def actualizar_paquete(usuario_id, grupo):
    return exito(servicios.actualizar_paquete(grupo), "Paquete actualizado.")

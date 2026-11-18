"""Rutas de actividades e historial (solo administrador)."""

from flask import Blueprint, request

from app.compartido.validaciones import cargar
from app.respuestas import exito
from app.seguridad import requiere_admin

from . import servicios
from .dtos import ActividadDTO

actividades_bp = Blueprint("actividades", __name__)
historial_bp = Blueprint("historial", __name__)


@actividades_bp.get("")
@requiere_admin
def listar(usuario_id):
    return exito(servicios.listar())


@actividades_bp.get("/<slug>")
@requiere_admin
def detalle(usuario_id, slug):
    return exito(servicios.detalle(slug))


@actividades_bp.post("")
@requiere_admin
def crear(usuario_id):
    datos = cargar(ActividadDTO(), request.get_json(silent=True))
    return exito(servicios.crear(datos, usuario_id), "Actividad guardada.", 201)


@actividades_bp.put("/<slug>")
@requiere_admin
def editar(usuario_id, slug):
    datos = cargar(ActividadDTO(), request.get_json(silent=True))
    return exito(servicios.editar(slug, datos, usuario_id), "Actividad actualizada.")


@actividades_bp.delete("/<slug>")
@requiere_admin
def eliminar(usuario_id, slug):
    return exito(servicios.eliminar(slug, usuario_id), "Actividad eliminada.")


@historial_bp.get("")
@requiere_admin
def historial(usuario_id):
    return exito(servicios.historial())

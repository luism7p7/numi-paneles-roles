"""Rutas de instituciones y grupos (solo administrador)."""

from flask import Blueprint, request

from app.compartido.validaciones import cargar
from app.respuestas import exito
from app.seguridad import requiere_admin

from . import servicios
from .dtos import CrearGrupoDTO, CrearInstitucionDTO

instituciones_bp = Blueprint("instituciones", __name__)


@instituciones_bp.get("")
@requiere_admin
def listar(usuario_id):
    return exito(servicios.listar())


@instituciones_bp.get("/<int:institucion_id>")
@requiere_admin
def detalle(usuario_id, institucion_id):
    return exito(servicios.detalle(institucion_id))


@instituciones_bp.post("")
@requiere_admin
def crear(usuario_id):
    datos = cargar(CrearInstitucionDTO(), request.get_json(silent=True))
    return exito({"id": servicios.crear(datos)}, "Institución creada.", 201)


@instituciones_bp.post("/<int:institucion_id>/grupos")
@requiere_admin
def crear_grupo(usuario_id, institucion_id):
    datos = cargar(CrearGrupoDTO(), request.get_json(silent=True))
    return exito(servicios.crear_grupo(institucion_id, datos), "Grupo creado.", 201)

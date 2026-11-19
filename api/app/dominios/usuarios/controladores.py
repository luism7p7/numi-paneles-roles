"""Rutas de usuarios y roles (solo administrador)."""

from flask import Blueprint, request

from app.compartido.validaciones import cargar
from app.respuestas import exito
from app.seguridad import requiere_admin

from . import servicios
from .dtos import CambiarEstadoDTO, UsuarioDTO

usuarios_bp = Blueprint("usuarios", __name__)


@usuarios_bp.get("")
@requiere_admin
def listar(usuario_id):
    return exito(servicios.listar())


@usuarios_bp.post("")
@requiere_admin
def crear(usuario_id):
    datos = cargar(UsuarioDTO(), request.get_json(silent=True))
    return exito(servicios.crear(datos), "Cuenta creada. Queda pendiente hasta que la actives.", 201)


@usuarios_bp.put("/<int:id_usuario>")
@requiere_admin
def editar(usuario_id, id_usuario):
    datos = cargar(UsuarioDTO(), request.get_json(silent=True))
    return exito(servicios.editar(id_usuario, datos), "Cuenta actualizada.")


@usuarios_bp.delete("/<int:id_usuario>")
@requiere_admin
def eliminar(usuario_id, id_usuario):
    return exito(servicios.eliminar(id_usuario, usuario_id), "Cuenta eliminada.")


@usuarios_bp.patch("/<int:id_usuario>/estado")
@requiere_admin
def cambiar_estado(usuario_id, id_usuario):
    datos = cargar(CambiarEstadoDTO(), request.get_json(silent=True))
    return exito(servicios.cambiar_estado(id_usuario, datos["estado"], usuario_id))


@usuarios_bp.post("/<int:id_usuario>/password-temporal")
@requiere_admin
def restablecer_password(usuario_id, id_usuario):
    return exito(servicios.restablecer_password(id_usuario))


@usuarios_bp.post("/importar")
@requiere_admin
def importar(usuario_id):
    resultado = servicios.importar(
        request.files.get("archivo"), request.form.get("rol"), request.form.get("institucion")
    )
    return exito(resultado)

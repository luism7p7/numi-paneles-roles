"""Rutas públicas de acceso: iniciar sesión y pedir una cuenta."""

from flask import Blueprint, request

from app.compartido.validaciones import cargar
from app.dominios.usuarios import servicios as usuarios
from app.dominios.usuarios.dtos import SolicitudCuentaDTO
from app.respuestas import exito

from . import servicios
from .dtos import LoginDTO

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/login")
def login():
    datos = cargar(LoginDTO(), request.get_json(silent=True))
    return exito(servicios.iniciar_sesion(datos["correo"], datos["password"], datos["rol"]), "Inicio de sesión exitoso.")


@auth_bp.post("/registro")
def registro():
    """Solicitud de cuenta desde la pantalla pública (no pide token). Queda pendiente."""
    datos = cargar(SolicitudCuentaDTO(), request.get_json(silent=True))
    return exito(None, usuarios.solicitar_cuenta(datos), 201)

"""Inicio de sesión del panel administrativo."""

from flask import Blueprint, jsonify, session

from comun.db import ejecutar
from comun.sesion import autenticar

bp = Blueprint("auth", __name__)

MENSAJE_ESTADO = {
    "Pendiente": "Tu cuenta todavía está pendiente de aprobación.",
    "Inactivo": "Tu cuenta está desactivada. Habla con otro administrador.",
}


@bp.post("/api/login")
def login():
    usuario, fallo = autenticar("Administrador", "Esta cuenta no tiene permisos de administrador.", MENSAJE_ESTADO)
    if fallo:
        return fallo

    session.clear()
    session["usuario_id"] = usuario["id"]
    ejecutar("UPDATE usuarios SET ultimo_acceso = NOW() WHERE id = %s", (usuario["id"],))
    return jsonify(nombre=f"{usuario['nombre']} {usuario['apellido']}")

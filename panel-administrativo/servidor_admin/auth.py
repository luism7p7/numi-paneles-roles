"""Inicio de sesión del panel administrativo."""

from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash

from .db import consultar, ejecutar
from .utilidades import error

bp = Blueprint("auth", __name__)

MENSAJE_ESTADO = {
    "Pendiente": "Tu cuenta todavía está pendiente de aprobación.",
    "Inactivo": "Tu cuenta está desactivada. Habla con otro administrador.",
}


@bp.post("/api/login")
def login():
    datos = request.get_json(silent=True) or {}
    correo = str(datos.get("correo", "")).strip().lower()
    password = str(datos.get("password", ""))
    if not correo or not password:
        return error("Escribe tu correo y tu contraseña.")

    usuario = consultar(
        "SELECT id, nombre, apellido, password_hash, rol, estado FROM usuarios WHERE correo = %s",
        (correo,),
        uno=True,
    )
    # Mismo mensaje si el correo no existe o la contraseña falla: así no se revela qué correos hay.
    if usuario is None or not usuario["password_hash"] or not check_password_hash(usuario["password_hash"], password):
        return error("Correo o contraseña incorrectos.", 401)
    if usuario["rol"] != "Administrador":
        return error("Esta cuenta no tiene permisos de administrador.", 403)
    if usuario["estado"] != "Activo":
        return error(MENSAJE_ESTADO[usuario["estado"]], 403)

    session.clear()
    session["usuario_id"] = usuario["id"]
    session["nombre"] = f"{usuario['nombre']} {usuario['apellido']}"
    ejecutar("UPDATE usuarios SET ultimo_acceso = NOW() WHERE id = %s", (usuario["id"],))
    return jsonify(nombre=session["nombre"])

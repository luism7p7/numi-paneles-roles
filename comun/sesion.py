"""Verificación de correo y contraseña, igual en los dos paneles (cada uno acepta un solo rol)."""

from flask import request
from werkzeug.security import check_password_hash

from .db import consultar
from .errores import error


def autenticar(rol, mensaje_otro_rol, mensajes_estado):
    """Valida lo que mandó el formulario de inicio de sesión.

    Devuelve (usuario, None) si todo está bien, o (None, respuesta_de_error) para devolverla tal cual.
    `mensajes_estado` dice qué responder a una cuenta que no está Activa (por ejemplo, Pendiente).
    """
    datos = request.get_json(silent=True) or {}
    correo = str(datos.get("correo", "")).strip().lower()
    password = str(datos.get("password", ""))
    if not correo or not password:
        return None, error("Escribe tu correo y tu contraseña.")

    usuario = consultar(
        "SELECT id, nombre, apellido, password_hash, rol, estado FROM usuarios WHERE correo = %s",
        (correo,),
        uno=True,
    )
    # Mismo mensaje si el correo no existe o la contraseña falla: así no se revela qué correos hay.
    if usuario is None or not usuario["password_hash"] or not check_password_hash(usuario["password_hash"], password):
        return None, error("Correo o contraseña incorrectos.", 401)
    if usuario["rol"] != rol:
        return None, error(mensaje_otro_rol, 403)
    if usuario["estado"] != "Activo":
        return None, error(mensajes_estado[usuario["estado"]], 403)
    return usuario, None

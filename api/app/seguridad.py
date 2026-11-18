"""Autenticación con JWT y decoradores de acceso por rol.

El token viaja en la cabecera `Authorization: Bearer <token>`. Lleva el id del usuario (`sub`)
y su rol; los decoradores lo verifican y le pasan `usuario_id` a la ruta.
"""

from datetime import UTC, datetime, timedelta
from functools import wraps

import jwt
from flask import current_app, request

from app.excepciones import NoAutenticado, PermisoDenegado

MENSAJE_SESION_TERMINADA = "Tu sesión terminó. Vuelve a iniciar sesión."

ADMINISTRADOR = "Administrador"
DOCENTE = "Docente"


def emitir_token(usuario):
    """JWT de acceso para un usuario ya autenticado."""
    ahora = datetime.now(UTC)
    vence = ahora + timedelta(minutes=current_app.config["JWT_EXP_MINUTES"])
    claims = {"sub": str(usuario["id"]), "rol": usuario["rol"], "iat": ahora, "exp": vence}
    return jwt.encode(claims, current_app.config["SECRET_KEY"], algorithm="HS256")


def _claims_de_la_peticion():
    cabecera = request.headers.get("Authorization", "")
    partes = cabecera.split()
    if len(partes) != 2 or partes[0].lower() != "bearer":
        raise NoAutenticado(MENSAJE_SESION_TERMINADA)
    try:
        return jwt.decode(partes[1], current_app.config["SECRET_KEY"], algorithms=["HS256"])
    except jwt.InvalidTokenError:  # incluye el token vencido
        raise NoAutenticado(MENSAJE_SESION_TERMINADA) from None


def requiere_rol(rol):
    """Exige un token válido de un usuario con ese rol e inyecta `usuario_id` en la ruta."""

    def decorador(vista):
        @wraps(vista)
        def envoltura(*args, **kwargs):
            claims = _claims_de_la_peticion()
            if claims.get("rol") != rol:
                raise PermisoDenegado("No tienes permisos para esta sección.")
            return vista(*args, usuario_id=int(claims["sub"]), **kwargs)

        return envoltura

    return decorador


requiere_admin = requiere_rol(ADMINISTRADOR)
requiere_docente = requiere_rol(DOCENTE)

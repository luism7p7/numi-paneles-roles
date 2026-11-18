"""Decorador de las rutas del docente que trabajan sobre su grupo activo."""

from functools import wraps

from flask import request

from . import servicios


def con_grupo_activo(vista):
    """Inyecta `grupo` (el grupo activo del docente) en la ruta. Va después de `@requiere_docente`."""

    @wraps(vista)
    def envoltura(*args, usuario_id, **kwargs):
        grupo = servicios.grupo_activo(usuario_id, request.headers.get("X-Grupo-Id"))
        return vista(*args, usuario_id=usuario_id, grupo=grupo, **kwargs)

    return envoltura

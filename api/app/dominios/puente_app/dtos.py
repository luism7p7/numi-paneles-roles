"""Validación de lo que manda el backend de la app. Es un contrato con la app: no se cambia."""

from marshmallow import fields

from app.compartido.validaciones import Esquema
from app.excepciones import ErrorDeDatos

MAX_ITEMS_PROGRESO = 500


def uid_valido(valor):
    uid = str(valor or "").strip()
    if not 1 <= len(uid) <= 128:
        raise ErrorDeDatos("Falta el uid del estudiante.")
    return uid


class UnirseDTO(Esquema):
    uid = fields.Raw(load_default="")
    nombre = fields.Raw(load_default="")
    codigo = fields.Raw(load_default="")


class ProgresoDTO(Esquema):
    uid = fields.Raw(load_default="")
    items = fields.Raw(load_default=None)
    racha_dias = fields.Raw(load_default=None)
    version_app = fields.Raw(load_default=None)

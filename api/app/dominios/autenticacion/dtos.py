"""Validación de los datos del inicio de sesión."""

from marshmallow import fields, validate

from app.compartido.validaciones import Esquema
from app.seguridad import ADMINISTRADOR, DOCENTE


class LoginDTO(Esquema):
    correo = fields.String(load_default="")
    password = fields.String(load_default="")
    # Cada panel dice con qué rol quiere entrar: una cuenta de otro rol no pasa
    rol = fields.String(
        required=True,
        validate=validate.OneOf((ADMINISTRADOR, DOCENTE), error="Indica el rol con el que entras."),
        error_messages={"required": "Indica el rol con el que entras.", "null": "Indica el rol con el que entras."},
    )

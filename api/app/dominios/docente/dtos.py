"""Validación de lo que llega al cambiar de grupo."""

from marshmallow import fields

from app.compartido.validaciones import Esquema


class CambiarGrupoDTO(Esquema):
    grupo_id = fields.Raw(load_default=None)

"""Validación de lo que llega al crear instituciones y grupos."""

from marshmallow import fields, validate

from app.compartido.validaciones import Entero, Esquema, Texto

COMUNAS = ("San Cristóbal", "Palmitas", "Santa Elena", "Altavista", "San Antonio de Prado")
LETRAS = "ABCDEFGH"


class CrearInstitucionDTO(Esquema):
    nombre = Texto("el nombre de la institución", 120)
    comuna = fields.String(
        required=True,
        validate=validate.OneOf(COMUNAS, error="Elige una comuna o corregimiento."),
        error_messages={"required": "Elige una comuna o corregimiento.", "null": "Elige una comuna o corregimiento."},
    )
    sedes = Entero("el número de sedes", 1, 50, required=False, load_default=1)
    estado = fields.String(
        load_default="Activa",
        validate=validate.OneOf(("Activa", "Inactiva"), error="El estado debe ser Activa o Inactiva."),
    )


class CrearGrupoDTO(Esquema):
    grado = Entero("el grado", 1, 5)
    letra = fields.String(
        required=True,
        error_messages={"required": f"La letra del grupo debe ser una de {', '.join(LETRAS)}."},
    )

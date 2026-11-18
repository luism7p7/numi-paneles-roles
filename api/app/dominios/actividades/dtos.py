"""Validación de lo que llega al crear o editar una actividad."""

from marshmallow import fields, validate

from app.compartido.validaciones import Entero, Esquema, Texto

TIPOS = ("Arrastrar", "Arrastrar y soltar", "Ordenar sílabas", "Selección múltiple",
         "Comprensión auditiva", "Memory match")


class Grado(Entero):
    """El grado llega como lo muestra el formulario («Grado 3°», «3°» o 3): solo importan los dígitos."""

    def _deserialize(self, valor, attr, data, **kwargs):
        return super()._deserialize("".join(c for c in str(valor) if c.isdigit()), attr, data, **kwargs)


class ActividadDTO(Esquema):
    nombre = Texto("el nombre de la actividad", 120)
    materia = fields.String(load_default="")
    grado = Grado("el grado", 1, 5)
    tipo = fields.String(
        required=True,
        validate=validate.OneOf(TIPOS, error="Elige un tipo de actividad válido."),
        error_messages={"required": "Elige un tipo de actividad válido.", "null": "Elige un tipo de actividad válido."},
    )
    estado = fields.String(
        required=True,
        validate=validate.OneOf(("Publicada", "Borrador"), error="El estado debe ser Publicada o Borrador."),
        error_messages={"required": "El estado debe ser Publicada o Borrador.",
                        "null": "El estado debe ser Publicada o Borrador."},
    )
    descripcion = Texto("la descripción", 255, obligatorio=False)
    recursos = fields.List(Entero("el recurso", 1, 10**9), load_default=list)
    contenido = fields.Raw(load_default=None)

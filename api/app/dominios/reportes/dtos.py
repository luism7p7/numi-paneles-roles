"""Validación de lo que se pide al descargar un reporte (llega en la dirección, como texto)."""

from datetime import date

from marshmallow import ValidationError, fields, validate

from app.compartido.textos import normalizar
from app.compartido.validaciones import Esquema

SECCIONES = {"avance", "detalle", "evaluacion", "notas", "racha"}


class _Fecha(fields.Field):
    def __init__(self, nombre, **kwargs):
        self.nombre = nombre
        mensaje = f"La fecha «{nombre}» no es válida."
        super().__init__(required=True, error_messages={"required": mensaje, "null": mensaje}, **kwargs)

    def _deserialize(self, valor, attr, data, **kwargs):
        try:
            return date.fromisoformat(valor)
        except (TypeError, ValueError):
            raise ValidationError(f"La fecha «{self.nombre}» no es válida.") from None


class DescargarReporteDTO(Esquema):
    formato = fields.String(
        required=True,
        validate=validate.OneOf(("xlsx", "pdf"), error="El formato debe ser xlsx o pdf."),
        error_messages={"required": "El formato debe ser xlsx o pdf.", "null": "El formato debe ser xlsx o pdf."},
    )
    periodo = fields.String(load_default="")
    desde = _Fecha("desde")
    hasta = _Fecha("hasta")
    estado = fields.String(load_default="")
    materias = fields.Method(deserialize="_materias", load_default=set())
    incluir = fields.Method(deserialize="_incluir", load_default=set())

    def _materias(self, valor):
        return {normalizar(e) for e in str(valor).split(",") if e}

    def _incluir(self, valor):
        return set(str(valor).split(",")) & SECCIONES

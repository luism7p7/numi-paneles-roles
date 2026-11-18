"""Campos de Marshmallow reutilizables por los DTOs, con los mismos mensajes que ve el usuario.

Cada DTO es un `Esquema`: ignora los campos que no conoce y trata `null` como si el campo no viniera.
"""

import re

from marshmallow import EXCLUDE, Schema, ValidationError, fields, pre_load

from app.excepciones import ErrorDeDatos

CORREO_VALIDO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Esquema(Schema):
    class Meta:
        unknown = EXCLUDE

    @pre_load
    def quitar_nulos(self, datos, **_):
        return {k: v for k, v in datos.items() if v is not None} if isinstance(datos, dict) else datos


def _obligatorio(mensaje):
    return {"required": mensaje, "null": mensaje}


class Texto(fields.Field):
    """Texto sin espacios sobrantes. `nombre` es cómo se le dice al usuario («el nombre»)."""

    def __init__(self, nombre, maximo, obligatorio=True, **kwargs):
        self.nombre, self.maximo, self.vacio_permitido = nombre, maximo, not obligatorio
        if obligatorio:
            kwargs.setdefault("required", True)
            kwargs.setdefault("error_messages", _obligatorio(f"Escribe {nombre}."))
        else:
            kwargs.setdefault("load_default", "")
        super().__init__(**kwargs)

    def _deserialize(self, valor, attr, data, **kwargs):
        texto = str(valor or "").strip()
        if not texto and not self.vacio_permitido:
            raise ValidationError(f"Escribe {self.nombre}.")
        if len(texto) > self.maximo:
            raise ValidationError(f"{self.nombre.capitalize()} no puede tener más de {self.maximo} caracteres.")
        return texto


class Correo(Texto):
    def __init__(self, nombre="el correo institucional", **kwargs):
        super().__init__(nombre, 120, **kwargs)

    def _deserialize(self, valor, attr, data, **kwargs):
        correo = super()._deserialize(valor, attr, data, **kwargs).lower()
        if not CORREO_VALIDO.match(correo):
            raise ValidationError("Escribe un correo válido.")
        return correo


class Entero(fields.Field):
    def __init__(self, nombre, minimo, maximo, **kwargs):
        self.nombre, self.minimo, self.maximo = nombre, minimo, maximo
        kwargs.setdefault("required", True)
        kwargs.setdefault("error_messages", _obligatorio(f"{nombre.capitalize()} debe ser un número."))
        super().__init__(**kwargs)

    def _deserialize(self, valor, attr, data, **kwargs):
        try:
            numero = int(str(valor).strip())
        except (TypeError, ValueError):
            raise ValidationError(f"{self.nombre.capitalize()} debe ser un número.") from None
        if not self.minimo <= numero <= self.maximo:
            raise ValidationError(f"{self.nombre.capitalize()} debe estar entre {self.minimo} y {self.maximo}.")
        return numero


class Booleano(fields.Field):
    """Solo acepta true o false de verdad (no 'si', 1 ni textos)."""

    def __init__(self, mensaje, **kwargs):
        self.mensaje = mensaje
        super().__init__(required=True, error_messages=_obligatorio(mensaje), **kwargs)

    def _deserialize(self, valor, attr, data, **kwargs):
        if not isinstance(valor, bool):
            raise ValidationError(self.mensaje)
        return valor


def cargar(esquema, datos):
    """Valida `datos` con el DTO. Un error de validación sale como ValidationError (400 con detalles)."""
    return esquema.load(datos if isinstance(datos, dict) else {})


def entero(valor, nombre, minimo, maximo):
    """Número entero dentro de un rango, para los datos que ya vienen dentro de un contenido (no de un DTO)."""
    try:
        numero = int(str(valor).strip())
    except (TypeError, ValueError):
        raise ErrorDeDatos(f"{nombre.capitalize()} debe ser un número.") from None
    if not minimo <= numero <= maximo:
        raise ErrorDeDatos(f"{nombre.capitalize()} debe estar entre {minimo} y {maximo}.")
    return numero

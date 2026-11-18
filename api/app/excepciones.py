"""Excepciones de dominio: el servicio las lanza y el manejador global las convierte en respuestas JSON."""


class ErrorDeDatos(Exception):
    """Un dato inválido o una regla de negocio que no se cumple. Se responde con 400 y el mensaje."""

    codigo = 400

    def __init__(self, mensaje, codigo=None, detalles=None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.detalles = detalles
        if codigo is not None:
            self.codigo = codigo


class NoAutenticado(ErrorDeDatos):
    codigo = 401


class PermisoDenegado(ErrorDeDatos):
    codigo = 403


class NoEncontrado(ErrorDeDatos):
    codigo = 404


class Conflicto(ErrorDeDatos):
    codigo = 409

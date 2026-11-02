"""Errores por datos inválidos y su respuesta JSON, iguales en los dos paneles."""

from flask import jsonify


class ErrorDeDatos(Exception):
    """Dato inválido enviado por el usuario. Se responde con 400 y el mensaje."""

    def __init__(self, mensaje, codigo=400):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo


def error(mensaje, codigo=400):
    return jsonify(error=mensaje), codigo

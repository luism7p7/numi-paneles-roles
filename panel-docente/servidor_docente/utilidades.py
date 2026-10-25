"""Funciones pequeñas que usan varias secciones del panel."""

import unicodedata

from flask import jsonify

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]


class ErrorDeDatos(Exception):
    """Dato inválido enviado por el usuario. Se responde con 400 y el mensaje."""

    def __init__(self, mensaje, codigo=400):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo


def error(mensaje, codigo=400):
    return jsonify(error=mensaje), codigo


def fecha_larga(dia):
    """date(2026, 9, 15) → '15 de septiembre'."""
    return f"{dia.day} de {MESES[dia.month - 1]}"


def iniciales(nombre):
    return "".join(p[0] for p in nombre.split()[:2]).upper()


def normalizar(texto):
    """'¿Vivo o no Vivo?' y '¿vivo o no vivo?' dan lo mismo, igual que en MySQL."""
    sin_tildes = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()
    return sin_tildes.strip().lower()


def nombre_grupo(grado, letra):
    return f"Grado {grado}° — grupo {letra}"

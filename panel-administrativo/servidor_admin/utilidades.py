"""Funciones pequeñas que usan varias secciones del panel."""

import re
import secrets
import unicodedata
from datetime import date, timedelta

from flask import jsonify

MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
MESES_LARGOS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                "septiembre", "octubre", "noviembre", "diciembre"]
CORREO_VALIDO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ErrorDeDatos(Exception):
    """Dato inválido enviado por el usuario. Se responde con 400 y el mensaje."""

    def __init__(self, mensaje, codigo=400):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo


def error(mensaje, codigo=400):
    return jsonify(error=mensaje), codigo


def fecha_corta(momento):
    """'Hoy, 11:52' · 'Ayer, 16:02' · '12 jun 2026' · 'Nunca'."""
    if momento is None:
        return "Nunca"
    hoy = date.today()
    if momento.date() == hoy:
        return f"Hoy, {momento:%H:%M}"
    if momento.date() == hoy - timedelta(days=1):
        return f"Ayer, {momento:%H:%M}"
    return f"{momento.day} {MESES[momento.month - 1]} {momento.year}"


def texto(datos, campo, nombre, maximo, obligatorio=True):
    valor = str(datos.get(campo) or "").strip()
    if obligatorio and not valor:
        raise ErrorDeDatos(f"Escribe {nombre}.")
    if len(valor) > maximo:
        raise ErrorDeDatos(f"{nombre.capitalize()} no puede tener más de {maximo} caracteres.")
    return valor


def correo(datos, campo="correo"):
    valor = texto(datos, campo, "el correo institucional", 120).lower()
    if not CORREO_VALIDO.match(valor):
        raise ErrorDeDatos("Escribe un correo válido.")
    return valor


def entero(valor, nombre, minimo, maximo):
    try:
        numero = int(str(valor).strip())
    except (TypeError, ValueError):
        raise ErrorDeDatos(f"{nombre.capitalize()} debe ser un número.") from None
    if not minimo <= numero <= maximo:
        raise ErrorDeDatos(f"{nombre.capitalize()} debe estar entre {minimo} y {maximo}.")
    return numero


def slug(nombre):
    """'¿Vivo o no vivo?' → 'vivo-o-no-vivo'."""
    sin_tildes = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", sin_tildes.lower()).strip("-") or "actividad"


def version(valor):
    """'1.3.2' → (1, 3, 2), para poder comparar versiones."""
    return tuple(int(p) for p in re.findall(r"\d+", valor or "0"))


def iniciales(nombre):
    return "".join(p[0] for p in nombre.split()[:2]).upper()


def password_temporal():
    alfabeto = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    caracteres = "".join(secrets.choice(alfabeto) for _ in range(8))
    return f"{caracteres[:4]}-{caracteres[4:]}"


def tamano_legible(bytes_):
    if bytes_ >= 1024 * 1024:
        return f"{bytes_ / 1024 / 1024:.1f} MB"
    return f"{max(1, round(bytes_ / 1024))} KB"

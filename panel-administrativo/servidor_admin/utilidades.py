"""Funciones pequeñas que usan varias secciones del panel."""

import re
import unicodedata
from datetime import date, timedelta

from comun.errores import ErrorDeDatos

MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
MESES_LARGOS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                "septiembre", "octubre", "noviembre", "diciembre"]
CORREO_VALIDO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


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


def tamano_legible(bytes_):
    if bytes_ >= 1024 * 1024:
        return f"{bytes_ / 1024 / 1024:.1f} MB"
    return f"{max(1, round(bytes_ / 1024))} KB"

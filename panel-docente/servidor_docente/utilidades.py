"""Funciones pequeñas que usan varias secciones del panel."""

import unicodedata

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]


def fecha_larga(dia):
    """date(2026, 9, 15) → '15 de septiembre'."""
    return f"{dia.day} de {MESES[dia.month - 1]}"


def normalizar(texto):
    """'¿Vivo o no Vivo?' y '¿vivo o no vivo?' dan lo mismo, igual que en MySQL."""
    sin_tildes = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()
    return sin_tildes.strip().lower()

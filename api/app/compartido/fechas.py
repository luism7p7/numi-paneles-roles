"""Fechas escritas para las pantallas."""

from datetime import date, timedelta

MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
MESES_LARGOS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                "septiembre", "octubre", "noviembre", "diciembre"]


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


def fecha_larga(dia):
    """date(2026, 9, 15) → '15 de septiembre'."""
    return f"{dia.day} de {MESES_LARGOS[dia.month - 1]}"

"""Textos que se arman igual en todos los dominios."""

import re
import unicodedata


def iniciales(nombre):
    """'Luisa Muñoz Rendón' → 'LM'."""
    return "".join(p[0] for p in nombre.split()[:2]).upper()


def nombre_grupo(grado, letra):
    return f"Grado {grado}° — grupo {letra}"


def version(valor):
    """'1.3.2' → (1, 3, 2), para poder comparar versiones."""
    return tuple(int(p) for p in re.findall(r"\d+", valor or "0"))


def _sin_tildes(texto):
    return unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()


def normalizar(texto):
    """'¿Vivo o no Vivo?' y '¿vivo o no vivo?' dan lo mismo, igual que en MySQL."""
    return _sin_tildes(texto).strip().lower()


def slug(nombre):
    """'¿Vivo o no vivo?' → 'vivo-o-no-vivo'."""
    return re.sub(r"[^a-z0-9]+", "-", _sin_tildes(nombre).lower()).strip("-") or "actividad"


def tamano_legible(bytes_):
    if bytes_ >= 1024 * 1024:
        return f"{bytes_ / 1024 / 1024:.1f} MB"
    return f"{max(1, round(bytes_ / 1024))} KB"

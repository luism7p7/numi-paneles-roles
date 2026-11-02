"""Textos que se arman igual en los dos paneles."""

import re


def iniciales(nombre):
    """'Luisa Muñoz Rendón' → 'LM'."""
    return "".join(p[0] for p in nombre.split()[:2]).upper()


def nombre_grupo(grado, letra):
    return f"Grado {grado}° — grupo {letra}"


def version(valor):
    """'1.3.2' → (1, 3, 2), para poder comparar versiones."""
    return tuple(int(p) for p in re.findall(r"\d+", valor or "0"))

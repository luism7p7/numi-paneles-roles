"""Textos que se arman igual en los dos paneles."""


def iniciales(nombre):
    """'Luisa Muñoz Rendón' → 'LM'."""
    return "".join(p[0] for p in nombre.split()[:2]).upper()


def nombre_grupo(grado, letra):
    return f"Grado {grado}° — grupo {letra}"

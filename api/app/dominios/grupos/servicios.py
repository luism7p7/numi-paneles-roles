"""Reglas de los grupos: el grupo con el que trabaja un docente y los códigos de ingreso."""

from app.compartido.codigos import generar_codigo_de_grupo
from app.excepciones import Conflicto

from . import repositorios as grupos


def codigo_de_grupo_libre():
    """Código para que los niños se unan al grupo, que ningún otro grupo tenga."""
    while True:
        codigo = generar_codigo_de_grupo()
        if not grupos.existe_codigo(codigo):
            return codigo


def del_docente(docente_id):
    return grupos.del_docente(docente_id)


def grupo_activo(docente_id, grupo_id_pedido=None):
    """Grupo con el que trabaja el docente. Siempre es uno de sus grupos.

    La pantalla manda en `X-Grupo-Id` el que el docente eligió; si falta o no es suyo, se usa el primero.
    """
    del_docente_ = grupos.del_docente(docente_id)
    if not del_docente_:
        raise Conflicto("No tienes grupos asignados. La coordinación de la sede los habilita.")
    for g in del_docente_:
        if str(g["id"]) == str(grupo_id_pedido):
            return g
    return del_docente_[0]


def grupos_por_docente():
    """{docente_id: [{"id": 3, "corto": "3° A"}, ...]}"""
    resultado = {}
    for g in grupos.a_cargo_de_los_docentes():
        resultado.setdefault(g["docente_id"], []).append({"id": g["id"], "corto": f"{g['grado']}° {g['letra']}"})
    return resultado

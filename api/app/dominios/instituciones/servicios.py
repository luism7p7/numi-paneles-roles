"""Reglas de las instituciones y de sus grupos."""

from datetime import date

from app.compartido.codigos import vencimiento_del_codigo
from app.compartido.textos import nombre_grupo
from app.dominios.grupos import repositorios as grupos
from app.dominios.grupos.servicios import codigo_de_grupo_libre
from app.excepciones import Conflicto, ErrorDeDatos, NoEncontrado

from . import repositorios as instituciones
from .dtos import LETRAS


def _grupo_json(g):
    return {
        "id": g["id"],
        "grado": g["grado"],
        "letra": g["letra"],
        "corto": f"{g['grado']}° {g['letra']}",
        "nombre": nombre_grupo(g["grado"], g["letra"]),
        "docente_id": g["docente_id"],
        "docente_nombre": g["docente"],
        # Texto que ya usaba el modal de detalle de la institución
        "docente": f"{g['docente']} · {g['estudiantes']} estudiantes" if g["docente"] else None,
    }


def grupos_de(institucion_id):
    return [_grupo_json(g) for g in grupos.de_la_institucion(institucion_id)]


def listar():
    return instituciones.listar()


def detalle(institucion_id):
    institucion = instituciones.obtener(institucion_id)
    if institucion is None:
        raise NoEncontrado("La institución no existe.")
    institucion["grupos"] = grupos_de(institucion_id)
    return institucion


def crear(datos):
    if instituciones.existe_nombre(datos["nombre"]):
        raise Conflicto("Ya existe una institución con ese nombre.")
    return instituciones.crear(datos["nombre"], datos["comuna"], datos["sedes"], datos["estado"])


def crear_grupo(institucion_id, datos):
    if not instituciones.existe(institucion_id):
        raise NoEncontrado("La institución no existe.")
    grado = datos["grado"]
    letra = str(datos["letra"]).strip().upper()
    if len(letra) != 1 or letra not in LETRAS:
        raise ErrorDeDatos(f"La letra del grupo debe ser una de {', '.join(LETRAS)}.")
    if grupos.existe(institucion_id, grado, letra):
        raise Conflicto(f"Ya existe el grupo {grado}° {letra} en esta institución.")
    nuevo_id = grupos.crear(institucion_id, grado, letra, codigo_de_grupo_libre(), vencimiento_del_codigo(), date.today())
    return next(g for g in grupos_de(institucion_id) if g["id"] == nuevo_id)

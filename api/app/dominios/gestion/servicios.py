"""Reglas de la gestión del grupo: código de ingreso, asistente de IA y paquete de contenido."""

from datetime import date

from flask import current_app

from app.compartido.codigos import vencimiento_del_codigo
from app.compartido.fechas import fecha_larga
from app.dominios.grupos import repositorios as grupos
from app.dominios.grupos.servicios import codigo_de_grupo_libre
from app.excepciones import ErrorDeDatos
from app.integraciones import backend_app

GRADO_MINIMO_IA = 3  # el asistente de IA de la app solo existe para 3°, 4° y 5°


def gestion_json(g):
    vencido = g["codigo_vence"] < date.today()
    return {
        "codigo": g["codigo"],
        "vence": f"{'Venció' if vencido else 'Vence'} el {fecha_larga(g['codigo_vence'])}",
        "usos": f"{max(0, g['codigo_usos_max'] - g['codigo_usos'])} de {g['codigo_usos_max']} usos disponibles",
        "ia": bool(g["ia_activada"]),
        "ia_disponible": g["grado"] >= GRADO_MINIMO_IA,
        "paquete": f"v{g['paquete_version']} · {g['paquete_mb']} MB · "
                   + ("actualizado hoy" if g["paquete_actualizado"] == date.today()
                      else f"actualizado el {fecha_larga(g['paquete_actualizado'])}"),
    }


def ver(grupo):
    return gestion_json(grupo)


def renovar_codigo(grupo):
    """Código nuevo: libre, con los usos reiniciados y 30 días de vigencia."""
    grupos.renovar_codigo(grupo["id"], codigo_de_grupo_libre(), vencimiento_del_codigo())
    return gestion_json(grupos.obtener(grupo["id"]))


def cambiar_ia(grupo, activada):
    if activada and grupo["grado"] < GRADO_MINIMO_IA:
        raise ErrorDeDatos("El asistente de IA solo está disponible para 3°, 4° y 5°.")
    grupos.cambiar_ia(grupo["id"], activada)
    return gestion_json(grupos.obtener(grupo["id"]))


def actualizar_paquete(grupo):
    base = current_app.config["APP_API_URL"]
    if not base:
        raise ErrorDeDatos("Falta APP_API_URL en el .env: no se sabe dónde consultar el paquete.", 503)
    try:
        version = backend_app.version_mas_reciente_de_paquetes(base)
    except Exception:
        raise ErrorDeDatos("No se pudo consultar el servidor de contenido de Numi. Intenta más tarde.", 502) from None
    grupos.cambiar_paquete(grupo["id"], version[:20], date.today())
    return gestion_json(grupos.obtener(grupo["id"]))

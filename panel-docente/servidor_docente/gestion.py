"""Gestión del grupo: código para unirse, asistente de IA y paquete de conocimiento."""

import json
import urllib.request
from datetime import date

from flask import Blueprint, current_app, jsonify, request

from comun.codigos import codigo_de_grupo_libre, vencimiento_del_codigo
from comun.db import ejecutar
from comun.errores import ErrorDeDatos, error
from comun.textos import version

from .auth import grupo_actual
from .utilidades import fecha_larga

bp = Blueprint("gestion", __name__)

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


@bp.get("/api/gestion")
def ver():
    return jsonify(gestion_json(grupo_actual()))


@bp.post("/api/gestion/codigo")
def nuevo_codigo():
    grupo = grupo_actual()
    ejecutar(
        "UPDATE grupos SET codigo = %s, codigo_usos = 0, codigo_vence = %s WHERE id = %s",
        (codigo_de_grupo_libre(), vencimiento_del_codigo(), grupo["id"]),
    )
    return jsonify(gestion_json(grupo_actual()))


@bp.patch("/api/gestion/ia")
def cambiar_ia():
    grupo = grupo_actual()
    activada = (request.get_json(silent=True) or {}).get("activada")
    if not isinstance(activada, bool):
        raise ErrorDeDatos("Indica si el asistente queda activado (true) o desactivado (false).")
    if activada and grupo["grado"] < GRADO_MINIMO_IA:
        raise ErrorDeDatos("El asistente de IA solo está disponible para 3°, 4° y 5°.")
    ejecutar("UPDATE grupos SET ia_activada = %s WHERE id = %s", (activada, grupo["id"]))
    return jsonify(gestion_json(grupo_actual()))


def version_de_paquetes(base):
    """Consulta GET /api/paquetes del backend de la app y devuelve la versión más reciente."""
    with urllib.request.urlopen(f"{base}/api/paquetes", timeout=8) as resp:
        paquetes = json.load(resp)["paquetes"]
    versiones = [p["version"] for p in paquetes if p.get("version")]
    return max(versiones, key=version)


@bp.post("/api/gestion/paquete")
def actualizar_paquete():
    grupo = grupo_actual()
    base = current_app.config["APP_API_URL"]
    if not base:
        return error("Falta APP_API_URL en el .env: no se sabe dónde consultar el paquete.", 503)
    try:
        version = version_de_paquetes(base)
    except Exception:
        return error("No se pudo consultar el servidor de contenido de Numi. Intenta más tarde.", 502)
    ejecutar(
        "UPDATE grupos SET paquete_version = %s, paquete_actualizado = %s WHERE id = %s",
        (version[:20], date.today(), grupo["id"]),
    )
    return jsonify(gestion_json(grupo_actual()))

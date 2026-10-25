"""Gestión del grupo: código para unirse, asistente de IA y paquete de conocimiento."""

import json
import secrets
import urllib.request
from datetime import date, timedelta

from flask import Blueprint, current_app, jsonify, request

from .auth import grupo_actual
from .db import consultar, ejecutar
from .utilidades import ErrorDeDatos, error, fecha_larga

bp = Blueprint("gestion", __name__)

ALFABETO_CODIGO = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # sin 0/O ni 1/I para no confundirlos
DIAS_VIGENCIA_CODIGO = 30
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
    while True:
        bloque = "".join(secrets.choice(ALFABETO_CODIGO) for _ in range(4))
        codigo = f"{bloque}-{secrets.randbelow(90) + 10}"
        if not consultar("SELECT 1 FROM grupos WHERE codigo = %s", (codigo,), uno=True):
            break
    ejecutar(
        "UPDATE grupos SET codigo = %s, codigo_usos = 0, codigo_vence = %s WHERE id = %s",
        (codigo, date.today() + timedelta(days=DIAS_VIGENCIA_CODIGO), grupo["id"]),
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
    return max(versiones, key=lambda v: tuple(int(x) for x in v.split(".") if x.isdigit()))


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

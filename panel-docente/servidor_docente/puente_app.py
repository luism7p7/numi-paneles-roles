"""Puente con la app Numi: lo llama el BACKEND de la app (servidor a servidor).

Autenticación: cabecera  X-Api-Key: <APP_API_KEY del .env>.
La clave nunca debe ir dentro de la app del celular; el celular habla con su
backend y el backend reenvía aquí.

    POST /api/app/v1/unirse       el niño escribe el código del grupo
    GET  /api/app/v1/actividades  actividades activas para el grupo del niño
    PUT  /api/app/v1/progreso     sube el progreso (gana el mayor avance, como en la app)
"""

import hmac
from datetime import date, datetime

from flask import Blueprint, current_app, jsonify, request

from . import calculos
from .db import confirmar, consultar, ejecutar
from .utilidades import ErrorDeDatos, error

bp = Blueprint("puente_app", __name__, url_prefix="/api/app/v1")

MAX_ITEMS_PROGRESO = 500


@bp.before_request
def exigir_clave():
    clave = current_app.config["APP_API_KEY"]
    if not clave:
        return error("El puente con la app está apagado: falta APP_API_KEY en el .env.", 503)
    if not hmac.compare_digest(request.headers.get("X-Api-Key", ""), clave):
        return error("Clave de la app inválida.", 401)
    return None


def datos_json():
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        raise ErrorDeDatos("El cuerpo debe ser un objeto JSON.")
    return datos


def uid_valido(valor):
    uid = str(valor or "").strip()
    if not 1 <= len(uid) <= 128:
        raise ErrorDeDatos("Falta el uid del estudiante.")
    return uid


def buscar_estudiante(uid):
    est = consultar(
        """SELECT e.*, g.grado FROM estudiantes e LEFT JOIN grupos g ON g.id = e.grupo_id
           WHERE e.uid = %s""",
        (uid,),
        uno=True,
    )
    if est is None:
        raise ErrorDeDatos("El estudiante no se ha unido a ningún grupo.", 404)
    return est


@bp.post("/unirse")
def unirse():
    datos = datos_json()
    uid = uid_valido(datos.get("uid"))
    nombre = str(datos.get("nombre") or "").strip()[:60] or "Estudiante"
    codigo = str(datos.get("codigo") or "").strip().upper()

    grupo = consultar(
        """SELECT g.*, i.nombre AS institucion FROM grupos g JOIN instituciones i ON i.id = g.institucion_id
           WHERE g.codigo = %s""",
        (codigo,),
        uno=True,
    )
    if grupo is None:
        raise ErrorDeDatos("El código no existe. Revísalo con tu docente.", 404)
    if grupo["codigo_vence"] < date.today():
        raise ErrorDeDatos("El código ya venció. Pide uno nuevo a tu docente.", 410)

    actual = consultar("SELECT id, grupo_id FROM estudiantes WHERE uid = %s", (uid,), uno=True)
    if actual and actual["grupo_id"] == grupo["id"]:
        ejecutar("UPDATE estudiantes SET nombre = %s WHERE id = %s", (nombre, actual["id"]))
    else:
        if grupo["codigo_usos"] >= grupo["codigo_usos_max"]:
            raise ErrorDeDatos("El código ya no tiene usos disponibles. Pide uno nuevo a tu docente.", 409)
        if actual:
            ejecutar("UPDATE estudiantes SET nombre = %s, grupo_id = %s WHERE id = %s",
                     (nombre, grupo["id"], actual["id"]), guardar=False)
        else:
            ejecutar("INSERT INTO estudiantes (uid, nombre, grupo_id) VALUES (%s, %s, %s)",
                     (uid, nombre, grupo["id"]), guardar=False)
        ejecutar("UPDATE grupos SET codigo_usos = codigo_usos + 1 WHERE id = %s", (grupo["id"],), guardar=False)
        confirmar()
    return jsonify(grupo={"grado": grupo["grado"], "letra": grupo["letra"], "institucion": grupo["institucion"],
                          "ia_activada": bool(grupo["ia_activada"])})


@bp.get("/actividades")
def actividades():
    est = buscar_estudiante(uid_valido(request.args.get("uid")))
    if est["grupo_id"] is None:
        raise ErrorDeDatos("El estudiante no tiene grupo.", 404)
    grupo = consultar("SELECT * FROM grupos WHERE id = %s", (est["grupo_id"],), uno=True)
    lista = []
    for a in calculos.actividades_del_grupo(grupo):
        if not a["activa"]:
            continue
        recursos = consultar(
            """SELECT r.nombre, r.tipo, r.carpeta, r.version_minima FROM actividad_recurso ar
               JOIN recursos r ON r.id = ar.recurso_id WHERE ar.actividad_id = %s""",
            (a["id"],),
        )
        lista.append({"id": a["slug"], "nombre": a["nombre"], "materia": a["materia"], "recursos": recursos})
    return jsonify(grado=grupo["grado"], ia_activada=bool(grupo["ia_activada"]), actividades=lista)


def fecha_iso(valor):
    if not valor:
        return None
    try:
        momento = datetime.fromisoformat(str(valor).replace("Z", "+00:00"))
    except ValueError:
        return None
    return momento.astimezone().replace(tzinfo=None) if momento.tzinfo else momento


@bp.put("/progreso")
def progreso():
    datos = datos_json()
    est = buscar_estudiante(uid_valido(datos.get("uid")))
    items = datos.get("items")
    if not isinstance(items, list) or len(items) > MAX_ITEMS_PROGRESO:
        raise ErrorDeDatos(f"items debe ser una lista de máximo {MAX_ITEMS_PROGRESO} registros.")
    claves = {m["clave"].lower() for m in calculos.materias()}

    guardados, rechazados = 0, 0
    for it in items:
        try:
            grado = int(it["grado"])
            materia = str(it["materia"]).strip().lower()
            actividad = str(it["actividad"]).strip()[:120]
            porcentaje = max(0.0, min(100.0, float(it.get("porcentaje", 0))))
            intentos = max(0, int(it.get("intentos", 0)))
        except (KeyError, TypeError, ValueError):
            rechazados += 1
            continue
        if not 1 <= grado <= 5 or not actividad or materia.replace("espanol", "español") not in claves:
            rechazados += 1
            continue
        # Misma regla que la app y su backend: gana el mayor avance
        ejecutar(
            """INSERT INTO progreso (estudiante_id, grado, materia, actividad, porcentaje, intentos, ultima_vez)
               VALUES (%s, %s, %s, %s, %s, %s, %s) AS nuevo
               ON DUPLICATE KEY UPDATE
                 ultima_vez = IF(nuevo.porcentaje >= progreso.porcentaje,
                                 COALESCE(nuevo.ultima_vez, progreso.ultima_vez), progreso.ultima_vez),
                 porcentaje = GREATEST(progreso.porcentaje, nuevo.porcentaje),
                 intentos = GREATEST(progreso.intentos, nuevo.intentos)""",
            (est["id"], grado, materia.replace("espanol", "español"), actividad, porcentaje, intentos,
             fecha_iso(it.get("ultima_vez"))),
            guardar=False,
        )
        guardados += 1

    racha = datos.get("racha_dias")
    ejecutar(
        """UPDATE estudiantes SET ultima_sincronizacion = NOW(),
                  version_app = COALESCE(%s, version_app), racha_dias = COALESCE(%s, racha_dias)
           WHERE id = %s""",
        (str(datos["version_app"])[:10] if datos.get("version_app") else None,
         int(racha) if isinstance(racha, int) and racha >= 0 else None, est["id"]),
        guardar=False,
    )
    confirmar()
    return jsonify(guardados=guardados, rechazados=rechazados)

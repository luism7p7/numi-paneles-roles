"""Reglas del puente con la app: unirse a un grupo, recibir actividades y subir el progreso."""

import json
from datetime import date, datetime

from app.compartido.base_datos import confirmar
from app.dominios.grupos import repositorios as grupos
from app.dominios.seguimiento import calculos
from app.dominios.seguimiento import repositorios as seguimiento
from app.excepciones import Conflicto, ErrorDeDatos, NoEncontrado

from . import repositorios as repo
from .dtos import MAX_ITEMS_PROGRESO, uid_valido


def _buscar_estudiante(uid):
    est = repo.estudiante_con_grado(uid)
    if est is None:
        raise NoEncontrado("El estudiante no se ha unido a ningún grupo.")
    return est


def unirse(datos):
    uid = uid_valido(datos["uid"])
    nombre = str(datos["nombre"] or "").strip()[:60] or "Estudiante"
    codigo = str(datos["codigo"] or "").strip().upper()

    grupo = grupos.por_codigo(codigo)
    if grupo is None:
        raise NoEncontrado("El código no existe. Revísalo con tu docente.")
    if grupo["codigo_vence"] < date.today():
        raise ErrorDeDatos("El código ya venció. Pide uno nuevo a tu docente.", 410)

    actual = repo.estudiante_por_uid(uid)
    if actual and actual["grupo_id"] == grupo["id"]:
        repo.actualizar_nombre(actual["id"], nombre)
    else:
        if grupo["codigo_usos"] >= grupo["codigo_usos_max"]:
            raise Conflicto("El código ya no tiene usos disponibles. Pide uno nuevo a tu docente.")
        if actual:
            repo.mover_de_grupo(actual["id"], nombre, grupo["id"])
        else:
            repo.crear_estudiante(uid, nombre, grupo["id"])
        grupos.gastar_uso_del_codigo(grupo["id"])
        confirmar()
    return {"grupo": {"grado": grupo["grado"], "letra": grupo["letra"], "institucion": grupo["institucion"],
                      "ia_activada": bool(grupo["ia_activada"])}}


def actividades(uid):
    est = _buscar_estudiante(uid_valido(uid))
    if est["grupo_id"] is None:
        raise NoEncontrado("El estudiante no tiene grupo.")
    grupo = grupos.obtener(est["grupo_id"])
    lista = []
    for a in calculos.actividades_del_grupo(grupo):
        activa = bool(a["activa"])
        base = {
            "id": a["slug"],
            "nombre": a["nombre"],  # el mismo texto con que la app guarda el progreso
            "materia": a["materia"],
            "tipo": a["tipo"],
            # en_app: ya tiene pantalla propia en la app. Si no, se juega con la plantilla de su tipo
            "en_app": bool(a["en_app"]),
            "activa": activa,
            # La app vuelve a descargar la actividad solo si cambió esta fecha
            "actualizada": a["actualizada_en"].isoformat(),
        }
        if not activa:
            # El docente la desactivó para este grupo: la app la oculta y no la cuenta en el avance.
            # Va marcada, sin contenido ni archivos, para que la app sepa cuál ocultar.
            lista.append(base | {"contenido": None, "recursos": []})
            continue
        recursos = repo.recursos_de_la_actividad(a["id"])
        lista.append({
            **base,
            "contenido": json.loads(a["contenido"]) if a["contenido"] else None,
            "recursos": [r | {"descargable": bool(r["descargable"])} for r in recursos],
        })
    return {"grado": grupo["grado"], "ia_activada": bool(grupo["ia_activada"]), "actividades": lista}


def archivo_del_recurso(recurso_id):
    archivo = repo.archivo_del_recurso(recurso_id)
    if not archivo:
        raise NoEncontrado("El recurso no existe o no tiene archivo.")
    return archivo


def _fecha_iso(valor):
    if not valor:
        return None
    try:
        momento = datetime.fromisoformat(str(valor).replace("Z", "+00:00"))
    except ValueError:
        return None
    return momento.astimezone().replace(tzinfo=None) if momento.tzinfo else momento


def subir_progreso(datos):
    est = _buscar_estudiante(uid_valido(datos["uid"]))
    items = datos["items"]
    if not isinstance(items, list) or len(items) > MAX_ITEMS_PROGRESO:
        raise ErrorDeDatos(f"items debe ser una lista de máximo {MAX_ITEMS_PROGRESO} registros.")
    claves = {m["clave"].lower() for m in seguimiento.materias()}

    guardados, rechazados = 0, 0
    for it in items:
        try:
            grado = int(it["grado"])
            materia = str(it["materia"]).strip().lower()
            actividad = str(it["actividad"]).strip()[:120]
            porcentaje = max(0.0, min(100.0, float(it.get("porcentaje", 0))))
            intentos = max(0, int(it.get("intentos", 0)))
        except (KeyError, TypeError, ValueError, AttributeError):
            rechazados += 1
            continue
        if not 1 <= grado <= 5 or not actividad or materia.replace("espanol", "español") not in claves:
            rechazados += 1
            continue
        repo.guardar_progreso(est["id"], grado, materia.replace("espanol", "español"), actividad, porcentaje,
                              intentos, _fecha_iso(it.get("ultima_vez")))
        guardados += 1

    racha = datos["racha_dias"]
    repo.registrar_sincronizacion(
        est["id"],
        str(datos["version_app"])[:10] if datos["version_app"] else None,
        int(racha) if isinstance(racha, int) and racha >= 0 else None,
    )
    confirmar()
    return {"guardados": guardados, "rechazados": rechazados}

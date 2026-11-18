"""Reglas del monitoreo técnico: ¿la app responde?, equipos, versiones, eventos e informes."""

import csv
import io
from datetime import datetime, timedelta

from flask import current_app

from app.compartido.base_datos import confirmar
from app.compartido.fechas import MESES_LARGOS, fecha_corta
from app.compartido.textos import slug, tamano_legible, version
from app.dominios.recursos import servicios as recursos
from app.excepciones import NoEncontrado
from app.integraciones import backend_app

from . import repositorios as repo

SEGUNDOS_ENTRE_REVISIONES = 60
DIAS_SIN_SINCRONIZAR = 7


def revisar_servicios():
    """Consulta el backend de la app (como mucho una vez por minuto) y guarda el resultado.

    Si un servicio cambia de estado se registra un evento. Sin APP_API_URL en el .env
    los servicios quedan "sin configurar" (operativo = NULL).
    """
    base = current_app.config["APP_API_URL"]
    ahora = datetime.now()
    for s in repo.servicios():
        if not base:
            continue
        if s["revisado_en"] and ahora - s["revisado_en"] < timedelta(seconds=SEGUNDOS_ENTRE_REVISIONES):
            continue
        operativo = backend_app.servicio_responde(base, s["clave"])
        # MySQL devuelve BOOLEAN como 0/1 (o None si nunca se revisó)
        estaba_caido = s["operativo"] is not None and not s["operativo"]
        caido_desde = None if operativo else (s["caido_desde"] or ahora)
        repo.guardar_revision(s["clave"], operativo, caido_desde, ahora)
        if not operativo and not estaba_caido:
            repo.registrar_evento("Crítico", f"{s['nombre']} sin respuesta")
        elif operativo and estaba_caido:
            repo.registrar_evento("Info", f"{s['nombre']} volvió a responder")
    confirmar()
    return repo.servicios()


def contar_sin_sincronizar():
    return repo.contar_sin_sincronizar(DIAS_SIN_SINCRONIZAR)


def servicio_json(s):
    return {
        "clave": s["clave"],
        "nombre": s["nombre"],
        "operativo": None if s["operativo"] is None else bool(s["operativo"]),
        "desde": f"{s['caido_desde']:%H:%M}" if s["caido_desde"] else None,
    }


def servicios_caidos():
    return [servicio_json(s) for s in revisar_servicios() if s["operativo"] is not None and not s["operativo"]]


def resumen():
    servicios = revisar_servicios()
    versiones = recursos.versiones_en_uso()
    total_equipos = sum(versiones.values())
    minima = current_app.config["VERSION_MINIMA_ACTIVIDADES"]
    viejas = sorted((v for v in versiones if version(v) < version(minima)), key=version)
    return {
        "actualizado": f"{datetime.now():%H:%M}",
        "servicios": [servicio_json(s) for s in servicios],
        "sin_sincronizar": contar_sin_sincronizar(),
        "errores_24h": repo.errores_ultimas_24h(),
        "equipos": total_equipos,
        "versiones": [
            {"version": v, "equipos": n, "porcentaje": round(n * 100 / total_equipos) if total_equipos else 0,
             "desactualizada": version(v) < version(minima)}
            for v, n in sorted(versiones.items(), key=lambda par: version(par[0]), reverse=True)
        ],
        "desactualizados": {"equipos": recursos.equipos_por_debajo_de(minima, versiones),
                            "version": viejas[0] if viejas else None},
        "informes": [{"id": i["id"], "titulo": i["titulo"], "formato": i["formato"],
                      "tamano": tamano_legible(i["bytes"])} for i in repo.informes_recientes()],
        "eventos": [{"nivel": e["nivel"], "mensaje": e["mensaje"], "fecha": fecha_corta(e["fecha"])}
                    for e in repo.eventos_recientes()],
    }


def generar_informe():
    """Informe de sincronización en CSV: un renglón por equipo (estudiante)."""
    salida = io.StringIO()
    escritor = csv.writer(salida)
    escritor.writerow(["institucion", "grupo", "estudiante", "version_app", "ultima_sincronizacion",
                       "dias_sin_sincronizar", "sincronizado_ultimos_7_dias"])
    for f in repo.equipos_para_informe():
        escritor.writerow([
            f["institucion"] or "Sin grupo",
            f"{f['grado']}° {f['letra']}" if f["grado"] else "",
            f["nombre"],
            f["version_app"] or "",
            f"{f['ultima_sincronizacion']:%Y-%m-%d %H:%M}" if f["ultima_sincronizacion"] else "Nunca",
            "" if f["dias"] is None else f["dias"],
            "sí" if f["dias"] is not None and f["dias"] < DIAS_SIN_SINCRONIZAR else "no",
        ])
    hoy = datetime.now()
    titulo = f"Sincronización · {MESES_LARGOS[hoy.month - 1]} {hoy.year}"
    # utf-8-sig para que Excel muestre bien las tildes
    return {"id": repo.crear_informe(titulo, salida.getvalue().encode("utf-8-sig")), "titulo": titulo}


def informe_para_descargar(informe_id):
    """(contenido, nombre del archivo, tipo) de un informe ya generado."""
    informe = repo.obtener_informe(informe_id)
    if informe is None:
        raise NoEncontrado("El informe no existe.")
    extension, tipo = ("csv", "text/csv") if informe["formato"] == "CSV" else ("pdf", "application/pdf")
    return informe["contenido"], f"{slug(informe['titulo'])}.{extension}", tipo

"""Monitoreo técnico: servicios de la app, equipos, versiones, eventos e informes."""

import csv
import io
import urllib.request
from datetime import datetime, timedelta

from flask import Blueprint, Response, abort, current_app, jsonify

from . import recursos
from .db import confirmar, consultar, ejecutar
from .utilidades import MESES_LARGOS, fecha_corta, slug, tamano_legible, version

bp = Blueprint("monitoreo", __name__)

# Ruta del backend de la app que se consulta para saber si cada servicio responde
RUTAS_SERVICIOS = {"datos": "/salud", "contenido": "/api/paquetes"}
SEGUNDOS_ENTRE_REVISIONES = 60
DIAS_SIN_SINCRONIZAR = 7


def responde(url):
    """True si la URL contesta 200 en menos de 5 segundos."""
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


def revisar_servicios():
    """Consulta el backend de la app (como mucho una vez por minuto) y guarda el resultado.

    Si un servicio cambia de estado se registra un evento. Sin APP_API_URL en el .env
    los servicios quedan "sin configurar" (operativo = NULL).
    """
    base = current_app.config["APP_API_URL"]
    ahora = datetime.now()
    for s in consultar("SELECT * FROM servicios"):
        if not base:
            continue
        if s["revisado_en"] and ahora - s["revisado_en"] < timedelta(seconds=SEGUNDOS_ENTRE_REVISIONES):
            continue
        operativo = responde(base + RUTAS_SERVICIOS[s["clave"]])
        # MySQL devuelve BOOLEAN como 0/1 (o None si nunca se revisó)
        estaba_caido = s["operativo"] is not None and not s["operativo"]
        caido_desde = None if operativo else (s["caido_desde"] or ahora)
        ejecutar(
            "UPDATE servicios SET operativo = %s, caido_desde = %s, revisado_en = %s WHERE clave = %s",
            (operativo, caido_desde, ahora, s["clave"]),
            guardar=False,
        )
        if not operativo and not estaba_caido:
            ejecutar("INSERT INTO eventos (nivel, mensaje) VALUES ('Crítico', %s)",
                     (f"{s['nombre']} sin respuesta",), guardar=False)
        elif operativo and estaba_caido:
            ejecutar("INSERT INTO eventos (nivel, mensaje) VALUES ('Info', %s)",
                     (f"{s['nombre']} volvió a responder",), guardar=False)
    confirmar()
    return consultar("SELECT * FROM servicios ORDER BY FIELD(clave, 'datos', 'contenido')")


def contar_sin_sincronizar():
    fila = consultar(
        """SELECT COUNT(*) AS n FROM estudiantes
           WHERE ultima_sincronizacion IS NULL OR ultima_sincronizacion < NOW() - INTERVAL %s DAY""",
        (DIAS_SIN_SINCRONIZAR,),
        uno=True,
    )
    return fila["n"]


def servicio_json(s):
    return {
        "clave": s["clave"],
        "nombre": s["nombre"],
        "operativo": None if s["operativo"] is None else bool(s["operativo"]),
        "desde": f"{s['caido_desde']:%H:%M}" if s["caido_desde"] else None,
    }


@bp.get("/api/monitoreo")
def resumen():
    servicios = revisar_servicios()
    versiones = recursos.versiones_en_uso()
    total_equipos = sum(versiones.values())
    minima = current_app.config["VERSION_MINIMA_ACTIVIDADES"]
    viejas = sorted((v for v in versiones if version(v) < version(minima)), key=version)
    informes = consultar(
        "SELECT id, titulo, formato, LENGTH(contenido) AS bytes FROM informes ORDER BY creado_en DESC LIMIT 5"
    )
    eventos = consultar("SELECT nivel, mensaje, fecha FROM eventos ORDER BY fecha DESC, id DESC LIMIT 8")
    errores = consultar(
        "SELECT COUNT(*) AS n FROM eventos WHERE nivel IN ('Crítico', 'Alerta') AND fecha >= NOW() - INTERVAL 1 DAY",
        uno=True,
    )
    return jsonify(
        actualizado=f"{datetime.now():%H:%M}",
        servicios=[servicio_json(s) for s in servicios],
        sin_sincronizar=contar_sin_sincronizar(),
        errores_24h=errores["n"],
        equipos=total_equipos,
        versiones=[
            {"version": v, "equipos": n, "porcentaje": round(n * 100 / total_equipos) if total_equipos else 0,
             "desactualizada": version(v) < version(minima)}
            for v, n in sorted(versiones.items(), key=lambda par: version(par[0]), reverse=True)
        ],
        desactualizados={"equipos": recursos.equipos_por_debajo_de(minima, versiones),
                         "version": viejas[0] if viejas else None},
        informes=[{"id": i["id"], "titulo": i["titulo"], "formato": i["formato"],
                   "tamano": tamano_legible(i["bytes"])} for i in informes],
        eventos=[{"nivel": e["nivel"], "mensaje": e["mensaje"], "fecha": fecha_corta(e["fecha"])} for e in eventos],
    )


@bp.post("/api/informes")
def generar_informe():
    """Informe de sincronización: un renglón por equipo (estudiante)."""
    filas = consultar(
        """SELECT i.nombre AS institucion, g.grado, g.letra, e.nombre, e.version_app,
                  e.ultima_sincronizacion, DATEDIFF(NOW(), e.ultima_sincronizacion) AS dias
           FROM estudiantes e
           LEFT JOIN grupos g ON g.id = e.grupo_id
           LEFT JOIN instituciones i ON i.id = g.institucion_id
           ORDER BY i.nombre, g.grado, g.letra, e.nombre"""
    )
    salida = io.StringIO()
    escritor = csv.writer(salida)
    escritor.writerow(["institucion", "grupo", "estudiante", "version_app", "ultima_sincronizacion",
                       "dias_sin_sincronizar", "sincronizado_ultimos_7_dias"])
    for f in filas:
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
    nuevo_id = ejecutar("INSERT INTO informes (titulo, formato, contenido) VALUES (%s, 'CSV', %s)",
                        (titulo, salida.getvalue().encode("utf-8-sig")))
    return jsonify(id=nuevo_id, titulo=titulo), 201


@bp.get("/api/informes/<int:informe_id>/descargar")
def descargar_informe(informe_id):
    informe = consultar("SELECT * FROM informes WHERE id = %s", (informe_id,), uno=True)
    if informe is None:
        abort(404, "El informe no existe.")
    extension, tipo = ("csv", "text/csv") if informe["formato"] == "CSV" else ("pdf", "application/pdf")
    return Response(
        informe["contenido"],
        mimetype=tipo,
        headers={"Content-Disposition": f'attachment; filename="{slug(informe["titulo"])}.{extension}"'},
    )

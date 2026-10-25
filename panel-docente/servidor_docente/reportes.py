"""Reportes por periodo y descarga en Excel o PDF."""

from datetime import date
from statistics import mean

from flask import Blueprint, abort, jsonify, request

from . import archivos, calculos
from .auth import grupo_actual
from .db import consultar
from .utilidades import ErrorDeDatos, nombre_grupo, normalizar

bp = Blueprint("reportes", __name__)

SECCIONES = {"avance", "detalle", "evaluacion", "notas", "racha"}


def buscar_periodo(clave):
    periodo = consultar("SELECT * FROM periodos WHERE clave = %s", (clave,), uno=True)
    if periodo is None:
        abort(404, "El periodo no existe.")
    return periodo


@bp.get("/api/reportes")
def datos_reporte():
    grupo = grupo_actual()
    periodo = buscar_periodo(request.args.get("periodo", "p1"))
    resumen = calculos.resumen_grupo(grupo, periodo["desde"], periodo["hasta"])
    nombres = [m["nombre_corto"] for m in calculos.materias()]
    aplicables = [(v, n) for v, n in zip(resumen["materias"], nombres) if v is not None]
    minimo = min(aplicables) if aplicables else (0, "—")
    return jsonify(
        periodo={"clave": periodo["clave"], "nombre": periodo["nombre"],
                 "desde": periodo["desde"].isoformat(), "hasta": periodo["hasta"].isoformat()},
        materias=[v or 0 for v in resumen["materias"]],
        promedio=calculos.porcentaje(mean(v for v, _ in aplicables)) if aplicables else 0,
        minimo=minimo[0],
        minimo_nombre=minimo[1],
        estudiantes=sorted(([a["nombre"], a["avance"]] for a in resumen["estudiantes"]), key=lambda e: -e[1]),
    )


def fecha_parametro(nombre):
    try:
        return date.fromisoformat(request.args.get(nombre, ""))
    except ValueError:
        raise ErrorDeDatos(f"La fecha «{nombre}» no es válida.") from None


@bp.get("/api/reportes/descargar")
def descargar():
    grupo = grupo_actual()
    formato = request.args.get("formato")
    if formato not in ("xlsx", "pdf"):
        raise ErrorDeDatos("El formato debe ser xlsx o pdf.")
    periodo = buscar_periodo(request.args.get("periodo", "p1"))
    desde, hasta = fecha_parametro("desde"), fecha_parametro("hasta")
    if desde > hasta:
        raise ErrorDeDatos("La fecha «desde» debe ser anterior a «hasta».")
    estado = request.args.get("estado", "")
    materias = calculos.materias()
    elegidas = {normalizar(e) for e in request.args.get("materias", "").split(",") if e}
    indices = [i for i, m in enumerate(materias) if normalizar(m["clave"]) in elegidas]
    if not indices:
        raise ErrorDeDatos("Elige al menos una materia.")
    incluir = set(request.args.get("incluir", "").split(",")) & SECCIONES
    if not incluir:
        raise ErrorDeDatos("Elige al menos un contenido para incluir en el archivo.")

    resumen = calculos.resumen_grupo(grupo, desde, hasta)
    alumnos = [a for a in resumen["estudiantes"] if not estado or a["estado"] == estado]
    claves = {normalizar(materias[i]["clave"]) for i in indices}
    secciones = []

    if "avance" in incluir:
        encabezados = ["Estudiante", "Avance %"] + [f"{materias[i]['nombre_corto']} %" for i in indices]
        filas = [[a["nombre"], a["avance"], *["—" if a["materias"][i] is None else a["materias"][i] for i in indices]]
                 for a in alumnos]
        secciones.append(("Avance por materia", encabezados, filas))
    if "detalle" in incluir:
        filas = []
        for a in alumnos:
            for act in resumen["actividades"]:
                registro = resumen["progreso"].get((a["id"], normalizar(act["materia"]), normalizar(act["nombre"])))
                if registro and normalizar(act["materia"]) in claves:
                    filas.append([a["nombre"], act["nombre"], act["materia_nombre"], f"{calculos.porcentaje(registro['porcentaje'])}%",
                                  registro["intentos"], f"{registro['ultima_vez']:%Y-%m-%d}" if registro["ultima_vez"] else ""])
        secciones.append(("Detalle de actividades", ["Estudiante", "Actividad", "Materia", "Avance", "Intentos", "Última vez"], filas))
    if "evaluacion" in incluir and alumnos:
        marcas = ", ".join(["%s"] * len(alumnos))
        evaluaciones = consultar(
            f"""SELECT e.nombre, m.clave, m.nombre_corto, ev.correctas, ev.total, ev.fecha
                FROM evaluaciones ev JOIN estudiantes e ON e.id = ev.estudiante_id JOIN materias m ON m.clave = ev.materia
                WHERE ev.estudiante_id IN ({marcas}) AND ev.fecha BETWEEN %s AND %s
                ORDER BY e.nombre, ev.fecha""",
            [a["id"] for a in alumnos] + [desde, f"{hasta} 23:59:59"],
        )
        filas = [[ev["nombre"], ev["nombre_corto"], f"{ev['correctas']} de {ev['total']}", f"{ev['fecha']:%Y-%m-%d}"]
                 for ev in evaluaciones if normalizar(ev["clave"]) in claves]
        secciones.append(("Resultados de evaluación", ["Estudiante", "Materia", "Correctas", "Fecha"], filas))
    if "notas" in incluir:
        filas = [[a["nombre"], a["nota_docente"]] for a in alumnos if a["nota_docente"]]
        secciones.append(("Notas del docente", ["Estudiante", "Nota"], filas))
    if "racha" in incluir:
        filas = [[a["nombre"], a["racha_dias"], a["estado"],
                  f"{a['ultima_sincronizacion']:%Y-%m-%d %H:%M}" if a["ultima_sincronizacion"] else "Nunca"]
                 for a in alumnos]
        secciones.append(("Racha y conexiones", ["Estudiante", "Racha (días)", "Estado", "Última conexión"], filas))

    grupo_texto = nombre_grupo(grupo["grado"], grupo["letra"])
    subtitulo = f"{grupo_texto} · {periodo['nombre']} · del {desde:%d/%m/%Y} al {hasta:%d/%m/%Y}"
    if estado:
        subtitulo += f" · estudiantes: {estado}"
    nombre_archivo = f"reporte-{grupo['grado']}{grupo['letra']}-{periodo['clave']}.{formato}"
    if formato == "xlsx":
        contenido = archivos.excel([(titulo, encabezados, filas) for titulo, encabezados, filas in secciones])
        tipo = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        contenido = archivos.pdf(f"Reporte de {grupo_texto}", subtitulo, secciones)
        tipo = "application/pdf"
    return archivos.enviar(contenido, nombre_archivo, tipo)

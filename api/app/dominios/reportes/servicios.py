"""Reglas de los reportes: el periodo de hoy, las cifras por periodo y el Excel o PDF descargable."""

from app.compartido import archivos
from app.compartido.textos import nombre_grupo, normalizar
from app.dominios.seguimiento import calculos
from app.dominios.seguimiento import repositorios as seguimiento
from app.excepciones import ErrorDeDatos, NoEncontrado

from . import repositorios as repo


def periodo_actual():
    """El periodo que contiene la fecha de hoy (el más corto si hay varios). Si ninguno, el último del año."""
    fila = repo.periodo_que_contiene() or repo.ultimo_periodo()
    return fila["clave"]


def _buscar_periodo(clave):
    periodo = repo.obtener_periodo(clave)
    if periodo is None:
        raise NoEncontrado("El periodo no existe.")
    return periodo


def datos_reporte(grupo, clave_periodo):
    periodo = _buscar_periodo(clave_periodo or periodo_actual())
    resumen = calculos.resumen_grupo(grupo, periodo["desde"], periodo["hasta"])
    nombres = calculos.nombres_de_materias()
    aplicables = [(v, n) for v, n in zip(resumen["materias"], nombres, strict=True) if v is not None]
    minimo = min(aplicables) if aplicables else (0, "—")
    return {
        "periodo": {"clave": periodo["clave"], "nombre": periodo["nombre"],
                    "desde": periodo["desde"].isoformat(), "hasta": periodo["hasta"].isoformat()},
        "periodos": repo.listar_periodos(),
        "materias": [v or 0 for v in resumen["materias"]],
        "promedio": resumen["avance"],  # el mismo cálculo (valores exactos) que el avance de cada estudiante
        "minimo": minimo[0],
        "minimo_nombre": minimo[1],
        "estudiantes": sorted(([a["nombre"], a["avance"]] for a in resumen["estudiantes"]), key=lambda e: -e[1]),
    }


def descargar(grupo, datos):
    """Arma el reporte que eligió el docente: (contenido, nombre del archivo, tipo)."""
    formato, desde, hasta, estado = datos["formato"], datos["desde"], datos["hasta"], datos["estado"]
    periodo = _buscar_periodo(datos["periodo"] or periodo_actual())
    if desde > hasta:
        raise ErrorDeDatos("La fecha «desde» debe ser anterior a «hasta».")
    materias = seguimiento.materias()
    indices = [i for i, m in enumerate(materias) if normalizar(m["clave"]) in datos["materias"]]
    if not indices:
        raise ErrorDeDatos("Elige al menos una materia.")
    incluir = datos["incluir"]
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
        evaluaciones = repo.evaluaciones_de([a["id"] for a in alumnos], desde, hasta)
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
    nombre = f"reporte-{grupo['grado']}{grupo['letra']}-{periodo['clave']}.{formato}"
    if formato == "xlsx":
        return archivos.excel(secciones), nombre, archivos.TIPO_XLSX
    return archivos.pdf(f"Reporte de {grupo_texto}", subtitulo, secciones), nombre, "application/pdf"

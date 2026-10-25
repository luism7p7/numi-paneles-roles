"""Panel, estudiantes (lista, ficha, nota, Excel, PDF) y actividades del grupo."""

from itertools import chain, zip_longest
from statistics import mean

from flask import Blueprint, abort, jsonify, request

from . import archivos, calculos
from .auth import grupo_actual
from .db import consultar, ejecutar
from .utilidades import ErrorDeDatos, iniciales, nombre_grupo, normalizar

bp = Blueprint("seguimiento", __name__)

UMBRAL_BAJO_AVANCE = 30


def estudiante_json(alumno):
    return {
        "id": alumno["id"],
        "nombre": alumno["nombre"],
        "avance": alumno["avance"],
        "materias": [v or 0 for v in alumno["materias"]],
        "racha": f"{alumno['racha_dias']} d",
        "estado": alumno["estado"],
    }


def requieren_atencion(resumen, nombres_materias):
    """Hasta 3 estudiantes: uno inactivo, uno con bajo avance y uno sin sincronizar."""
    alumnos = resumen["estudiantes"]
    inactivos = sorted((a for a in alumnos if a["estado"] == "Inactivo"), key=lambda a: -(a["dias"] or 999))
    sin_sync = sorted((a for a in alumnos if a["estado"] == "Sin sincronizar"), key=lambda a: -a["dias"])
    bajos = []
    for a in alumnos:
        if a["estado"] == "Inactivo":
            continue
        valores = [(v, i) for i, v in enumerate(a["materias"]) if v is not None]
        if valores and min(valores)[0] < UMBRAL_BAJO_AVANCE:
            valor, i = min(valores)
            bajos.append((valor, a, nombres_materias[i]))
    bajos.sort(key=lambda t: t[0])

    candidatos = [
        [[a["nombre"], f"{a['dias']} días sin entrar" if a["dias"] is not None else "Nunca ha sincronizado", "danger", "Inactivo"] for a in inactivos],
        [[a["nombre"], f"{materia} en {valor}%", "warning", "Bajo avance"] for valor, a, materia in bajos],
        [[a["nombre"], "Sin sincronizar", "info", "Sincronizar"] for a in sin_sync],
    ]
    # Intercala las tres listas para que se vea un caso de cada tipo
    return [c for c in chain.from_iterable(zip_longest(*candidatos)) if c][:3]


@bp.get("/api/panel")
def panel():
    grupo = grupo_actual()
    resumen = calculos.resumen_grupo(grupo)
    nombres = [m["nombre_corto"] for m in calculos.materias()]
    return jsonify(
        activos=resumen["activos"],
        sin_conexion=len(resumen["estudiantes"]) - resumen["activos"],
        racha=f"{resumen['racha']} d",
        avance=resumen["avance"],
        materias=[v or 0 for v in resumen["materias"]],
        atencion=requieren_atencion(resumen, nombres),
    )


@bp.get("/api/estudiantes")
def listar_estudiantes():
    resumen = calculos.resumen_grupo(grupo_actual())
    return jsonify([estudiante_json(a) for a in resumen["estudiantes"]])


def ficha_de(grupo, estudiante_id):
    resumen = calculos.resumen_grupo(grupo)
    alumno = next((a for a in resumen["estudiantes"] if a["id"] == estudiante_id), None)
    if alumno is None:
        abort(404, "El estudiante no está en el grupo activo.")
    evaluaciones = consultar(
        """SELECT m.nombre_corto, ev.correctas, ev.total FROM evaluaciones ev
           JOIN materias m ON m.clave = ev.materia
           WHERE ev.estudiante_id = %s ORDER BY ev.fecha DESC LIMIT 3""",
        (estudiante_id,),
    )
    actividades = [
        [a["nombre"], calculos.texto_avance(calculos.avance_de(resumen["progreso"], estudiante_id, a))]
        for a in resumen["actividades"] if a["activa"]
    ]
    return alumno, estudiante_json(alumno) | {
        "iniciales": iniciales(alumno["nombre"]),
        "actividades": actividades,
        "evaluacion": [[f"Banco MCQ · {e['nombre_corto'].lower()}", f"{e['correctas']} de {e['total']} correctas"]
                       for e in evaluaciones],
        "nota": alumno["nota_docente"] or "",
    }


@bp.get("/api/estudiantes/<int:estudiante_id>")
def ficha(estudiante_id):
    return jsonify(ficha_de(grupo_actual(), estudiante_id)[1])


@bp.put("/api/estudiantes/<int:estudiante_id>/nota")
def guardar_nota(estudiante_id):
    grupo = grupo_actual()
    nota = str((request.get_json(silent=True) or {}).get("nota", "")).strip()
    if len(nota) > 2000:
        raise ErrorDeDatos("La nota no puede tener más de 2000 caracteres.")
    filas = consultar("SELECT id FROM estudiantes WHERE id = %s AND grupo_id = %s", (estudiante_id, grupo["id"]))
    if not filas:
        abort(404, "El estudiante no está en el grupo activo.")
    ejecutar("UPDATE estudiantes SET nota_docente = %s WHERE id = %s", (nota or None, estudiante_id))
    return jsonify(nota=nota)


@bp.get("/api/estudiantes/exportar")
def exportar_estudiantes():
    grupo = grupo_actual()
    resumen = calculos.resumen_grupo(grupo)
    nombres = [m["nombre_corto"] for m in calculos.materias()]
    filas = [
        [a["nombre"], a["avance"], *[("—" if v is None else v) for v in a["materias"]], a["racha_dias"], a["estado"],
         f"{a['ultima_sincronizacion']:%Y-%m-%d %H:%M}" if a["ultima_sincronizacion"] else "Nunca"]
        for a in resumen["estudiantes"]
    ]
    encabezados = ["Estudiante", "Avance %", *[f"{n} %" for n in nombres], "Racha (días)", "Estado", "Última sincronización"]
    contenido = archivos.excel([("Estudiantes", encabezados, filas)])
    return archivos.enviar(contenido, f"estudiantes-{grupo['grado']}{grupo['letra']}.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@bp.get("/api/estudiantes/<int:estudiante_id>/informe")
def informe_estudiante(estudiante_id):
    grupo = grupo_actual()
    alumno, ficha_json = ficha_de(grupo, estudiante_id)
    nombres = [m["nombre_corto"] for m in calculos.materias()]
    secciones = [
        ("Resumen", ["Avance", "Racha", "Estado"], [[f"{alumno['avance']}%", ficha_json["racha"], alumno["estado"]]]),
        ("Avance por materia", ["Materia", "Avance"],
         [[n, "No aplica" if v is None else f"{v}%"] for n, v in zip(nombres, alumno["materias"])]),
        ("Actividades", ["Actividad", "Estado"], ficha_json["actividades"]),
        ("Evaluación", ["Banco", "Resultado"], ficha_json["evaluacion"]),
    ]
    if ficha_json["nota"]:
        secciones.append(("Nota del docente", ["Observación"], [[ficha_json["nota"]]]))
    contenido = archivos.pdf(f"Informe de {alumno['nombre']}", nombre_grupo(grupo["grado"], grupo["letra"]), secciones)
    return archivos.enviar(contenido, f"informe-{normalizar(alumno['nombre']).replace(' ', '-')}.pdf", "application/pdf")


@bp.get("/api/actividades")
def listar_actividades():
    grupo = grupo_actual()
    resumen = calculos.resumen_grupo(grupo)
    alumnos = resumen["estudiantes"]
    resultado = []
    for a in resumen["actividades"]:
        valores = [calculos.avance_de(resumen["progreso"], al["id"], a) for al in alumnos]
        intentos = [resumen["progreso"][k]["intentos"] for k in resumen["progreso"]
                    if k[1] == normalizar(a["materia"]) and k[2] == normalizar(a["nombre"])]
        resultado.append({
            "id": a["slug"],
            "nombre": a["nombre"],
            "materia": a["materia_nombre"],
            "materia_indice": a["orden"] - 1,
            "descripcion": a["descripcion"],
            "activa": bool(a["activa"]),
            "avance": calculos.porcentaje(mean(valores)) if valores else 0,
            "intentos_promedio": mean(intentos) if intentos else 0,
            "estudiantes": [[al["nombre"], calculos.texto_avance(v)] for al, v in zip(alumnos, valores) if v],
        })
    # "Más errores": la actividad en la que más veces tuvieron que intentar
    con_intentos = [r for r in resultado if r["intentos_promedio"]]
    mas_errores = max(con_intentos, key=lambda r: r["intentos_promedio"])["id"] if con_intentos else None
    for r in resultado:
        r["mas_errores"] = r["id"] == mas_errores
        del r["intentos_promedio"]
    return jsonify(resultado)


@bp.patch("/api/actividades/<slug>")
def activar_actividad(slug):
    grupo = grupo_actual()
    activa = (request.get_json(silent=True) or {}).get("activa")
    if not isinstance(activa, bool):
        raise ErrorDeDatos("Indica si la actividad queda activa (true) o inactiva (false).")
    actividad = next((a for a in calculos.actividades_del_grupo(grupo) if a["slug"] == slug), None)
    if actividad is None:
        abort(404, "La actividad no está disponible para este grupo.")
    ejecutar(
        """INSERT INTO grupo_actividad (grupo_id, actividad_id, activa) VALUES (%s, %s, %s)
           ON DUPLICATE KEY UPDATE activa = VALUES(activa)""",
        (grupo["id"], actividad["id"], activa),
    )
    return jsonify(id=slug, activa=activa, nombre=actividad["nombre"], grupo=nombre_grupo(grupo["grado"], grupo["letra"]))

"""Casos de uso del seguimiento: panel, estudiantes (lista, ficha, nota, Excel, PDF) y actividades del grupo."""

from itertools import chain, zip_longest
from statistics import mean

from app.compartido import archivos
from app.compartido.textos import iniciales, nombre_grupo, normalizar
from app.excepciones import NoEncontrado

from . import calculos
from . import repositorios as repo

UMBRAL_BAJO_AVANCE = 30


def _estudiante_json(alumno):
    return {
        "id": alumno["id"],
        "nombre": alumno["nombre"],
        "avance": alumno["avance"],
        "materias": [v or 0 for v in alumno["materias"]],
        "racha": f"{alumno['racha_dias']} d",
        "estado": alumno["estado"],
    }


def _requieren_atencion(resumen, nombres_materias):
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


def panel(grupo):
    resumen = calculos.resumen_grupo(grupo)
    return {
        "activos": resumen["activos"],
        "sin_conexion": len(resumen["estudiantes"]) - resumen["activos"],
        "racha": f"{resumen['racha']} d",
        "avance": resumen["avance"],
        "materias": [v or 0 for v in resumen["materias"]],
        "atencion": _requieren_atencion(resumen, calculos.nombres_de_materias()),
    }


def listar_estudiantes(grupo):
    return [_estudiante_json(a) for a in calculos.resumen_grupo(grupo)["estudiantes"]]


def _ficha(grupo, estudiante_id):
    resumen = calculos.resumen_grupo(grupo)
    alumno = next((a for a in resumen["estudiantes"] if a["id"] == estudiante_id), None)
    if alumno is None:
        raise NoEncontrado("El estudiante no está en el grupo activo.")
    actividades = [
        [a["nombre"], calculos.texto_avance(calculos.avance_de(resumen["progreso"], estudiante_id, a))]
        for a in resumen["actividades"] if a["activa"]
    ]
    evaluaciones = repo.ultimas_evaluaciones(estudiante_id)
    return alumno, _estudiante_json(alumno) | {
        "iniciales": iniciales(alumno["nombre"]),
        "actividades": actividades,
        "evaluacion": [[f"Banco MCQ · {e['nombre_corto'].lower()}", f"{e['correctas']} de {e['total']} correctas"]
                       for e in evaluaciones],
        "nota": alumno["nota_docente"] or "",
    }


def ficha(grupo, estudiante_id):
    return _ficha(grupo, estudiante_id)[1]


def guardar_nota(grupo, estudiante_id, nota):
    if not repo.pertenece_al_grupo(estudiante_id, grupo["id"]):
        raise NoEncontrado("El estudiante no está en el grupo activo.")
    repo.guardar_nota(estudiante_id, nota or None)
    return {"nota": nota}


def exportar_estudiantes(grupo):
    """Excel con todos los estudiantes del grupo: (contenido, nombre del archivo)."""
    resumen = calculos.resumen_grupo(grupo)
    nombres = calculos.nombres_de_materias()
    filas = [
        [a["nombre"], a["avance"], *[("—" if v is None else v) for v in a["materias"]], a["racha_dias"], a["estado"],
         f"{a['ultima_sincronizacion']:%Y-%m-%d %H:%M}" if a["ultima_sincronizacion"] else "Nunca"]
        for a in resumen["estudiantes"]
    ]
    encabezados = ["Estudiante", "Avance %", *[f"{n} %" for n in nombres], "Racha (días)", "Estado", "Última sincronización"]
    return archivos.excel([("Estudiantes", encabezados, filas)]), f"estudiantes-{grupo['grado']}{grupo['letra']}.xlsx"


def informe_estudiante(grupo, estudiante_id):
    """PDF con el informe de un estudiante: (contenido, nombre del archivo)."""
    alumno, datos = _ficha(grupo, estudiante_id)
    nombres = calculos.nombres_de_materias()
    secciones = [
        ("Resumen", ["Avance", "Racha", "Estado"], [[f"{alumno['avance']}%", datos["racha"], alumno["estado"]]]),
        ("Avance por materia", ["Materia", "Avance"],
         [[n, "No aplica" if v is None else f"{v}%"] for n, v in zip(nombres, alumno["materias"], strict=True)]),
        ("Actividades", ["Actividad", "Estado"], datos["actividades"]),
        ("Evaluación", ["Banco", "Resultado"], datos["evaluacion"]),
    ]
    if datos["nota"]:
        secciones.append(("Nota del docente", ["Observación"], [[datos["nota"]]]))
    contenido = archivos.pdf(f"Informe de {alumno['nombre']}", nombre_grupo(grupo["grado"], grupo["letra"]), secciones)
    return contenido, f"informe-{normalizar(alumno['nombre']).replace(' ', '-')}.pdf"


def listar_actividades(grupo):
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
            "estudiantes": [[al["nombre"], calculos.texto_avance(v)] for al, v in zip(alumnos, valores, strict=True) if v],
        })
    # "Más errores": la actividad en la que más veces tuvieron que intentar
    con_intentos = [r for r in resultado if r["intentos_promedio"]]
    mas_errores = max(con_intentos, key=lambda r: r["intentos_promedio"])["id"] if con_intentos else None
    for r in resultado:
        r["mas_errores"] = r["id"] == mas_errores
        del r["intentos_promedio"]
    return resultado


def activar_actividad(grupo, slug, activa):
    """El docente enciende o apaga una actividad solo para su grupo."""
    actividad = next((a for a in calculos.actividades_del_grupo(grupo) if a["slug"] == slug), None)
    if actividad is None:
        raise NoEncontrado("La actividad no está disponible para este grupo.")
    repo.definir_actividad_activa(grupo["id"], actividad["id"], activa)
    return {"id": slug, "activa": activa, "nombre": actividad["nombre"], "grupo": nombre_grupo(grupo["grado"], grupo["letra"])}

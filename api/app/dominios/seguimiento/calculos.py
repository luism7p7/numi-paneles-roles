"""Cálculos de avance que comparten el panel, estudiantes, actividades y reportes.

Regla (la misma de la app): el avance de un estudiante en una materia es la suma
del % de cada actividad publicada de esa materia dividida entre (total × 100).
Las que no ha empezado cuentan 0. En la app las actividades son las mismas para
todos los grados, así que el grado NO filtra: si completa todo, tiene 100%.
"""

from statistics import mean

from app.compartido.textos import normalizar

from . import repositorios as repo

DIAS_INACTIVO = 7        # sin sincronizar en una semana → Inactivo
DIAS_SIN_SINCRONIZAR = 2


def porcentaje(valor):
    """Igual que la app (`pct.toInt()` en Dart): corta los decimales, no redondea.

    66,67 → 66. El 1e-9 evita que un 100 guardado como 99,9999999 se vuelva 99.
    """
    return int(valor + 1e-9)


def nombres_de_materias():
    return [m["nombre_corto"] for m in repo.materias()]


def estado_de(dias):
    if dias is None or dias >= DIAS_INACTIVO:
        return "Inactivo"
    if dias >= DIAS_SIN_SINCRONIZAR:
        return "Sin sincronizar"
    return "Al día"


def texto_avance(valor):
    """Cómo se muestra el avance de una actividad en la ficha del estudiante."""
    if not valor:
        return "Sin empezar"
    return "Completada" if valor >= 100 else f"{porcentaje(valor)}%"


def estudiantes_del_grupo(grupo_id):
    filas = repo.estudiantes_del_grupo(grupo_id)
    for f in filas:
        f["estado"] = estado_de(f["dias"])
    return filas


def actividades_del_grupo(grupo):
    """Actividades que el niño puede jugar, con su estado en el grupo.

    Jugable = publicada y, o bien ya programada en la app (en_app: son las mismas para todos
    los grados), o bien creada en el panel con contenido de plantilla (solo para el grado
    que eligió el administrador). Una actividad del panel sin contenido no cuenta.
    """
    return repo.actividades_del_grupo(grupo["id"], grupo["grado"])


def progreso_del_grupo(grupo_id, desde=None, hasta=None):
    """{(estudiante_id, materia, actividad) normalizados: {'porcentaje', 'intentos', 'ultima_vez'}}."""
    return {
        (f["estudiante_id"], normalizar(f["materia"]), normalizar(f["actividad"])): {
            "porcentaje": float(f["porcentaje"]), "intentos": f["intentos"], "ultima_vez": f["ultima_vez"],
        }
        for f in repo.progreso_del_grupo(grupo_id, desde, hasta)
    }


def avance_de(progreso, estudiante_id, actividad):
    fila = progreso.get((estudiante_id, normalizar(actividad["materia"]), normalizar(actividad["nombre"])))
    return fila["porcentaje"] if fila else 0.0


def resumen_grupo(grupo, desde=None, hasta=None):
    """Estudiantes con su avance por materia, y los promedios del grupo.

    Las materias sin actividades publicadas para el grado quedan en None: no cuentan
    en los promedios (por ejemplo, Inglés en 1°).
    """
    claves = [m["clave"] for m in repo.materias()]
    actividades = actividades_del_grupo(grupo)
    progreso = progreso_del_grupo(grupo["id"], desde, hasta)
    alumnos = estudiantes_del_grupo(grupo["id"])

    por_materia = {c: [a for a in actividades if normalizar(a["materia"]) == normalizar(c)] for c in claves}
    for alumno in alumnos:
        # Se guarda el valor exacto para los promedios y se muestra cortado, como la app
        exactos = [
            mean(avance_de(progreso, alumno["id"], a) for a in por_materia[c]) if por_materia[c] else None
            for c in claves
        ]
        alumno["materias"] = [None if v is None else porcentaje(v) for v in exactos]
        con_datos = [v for v in exactos if v is not None]
        alumno["avance_exacto"] = mean(con_datos) if con_datos else 0
        alumno["avance"] = porcentaje(alumno["avance_exacto"])
        alumno["materias_exactas"] = exactos

    promedios = []
    for i, c in enumerate(claves):
        valores = [a["materias_exactas"][i] for a in alumnos if a["materias_exactas"][i] is not None]
        promedios.append(porcentaje(mean(valores)) if valores and por_materia[c] else None)
    return {
        "estudiantes": alumnos,
        "materias": promedios,
        "avance": porcentaje(mean(a["avance_exacto"] for a in alumnos)) if alumnos else 0,
        "activos": sum(1 for a in alumnos if a["dias"] is not None and a["dias"] < DIAS_INACTIVO),
        "racha": round(mean(a["racha_dias"] for a in alumnos)) if alumnos else 0,
        "actividades": actividades,
        "progreso": progreso,
    }

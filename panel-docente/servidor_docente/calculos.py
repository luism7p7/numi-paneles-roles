"""Cálculos de avance que comparten el panel, estudiantes, actividades y reportes.

Regla (la misma de la app): el avance de un estudiante en una materia es la suma
del % de cada actividad publicada de esa materia dividida entre (total × 100).
Las que no ha empezado cuentan 0. En la app las actividades son las mismas para
todos los grados, así que el grado NO filtra: si completa todo, tiene 100%.
"""

from statistics import mean

from .db import consultar
from .utilidades import normalizar

DIAS_INACTIVO = 7        # sin sincronizar en una semana → Inactivo
DIAS_SIN_SINCRONIZAR = 2


def porcentaje(valor):
    """Igual que la app (`pct.toInt()` en Dart): corta los decimales, no redondea.

    66,67 → 66. El 1e-9 evita que un 100 guardado como 99,9999999 se vuelva 99.
    """
    return int(valor + 1e-9)


def materias():
    return consultar("SELECT clave, nombre_corto FROM materias ORDER BY orden")


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
    filas = consultar(
        """SELECT id, uid, nombre, racha_dias, nota_docente, version_app, ultima_sincronizacion,
                  DATEDIFF(NOW(), ultima_sincronizacion) AS dias
           FROM estudiantes WHERE grupo_id = %s ORDER BY nombre""",
        (grupo_id,),
    )
    for f in filas:
        f["estado"] = estado_de(f["dias"])
    return filas


def actividades_del_grupo(grupo):
    """Actividades publicadas (las mismas para todos los grados), con su estado en el grupo."""
    return consultar(
        """SELECT a.id, a.slug, a.nombre, a.materia, m.nombre_corto AS materia_nombre, m.orden,
                  a.descripcion, COALESCE(ga.activa, TRUE) AS activa
           FROM actividades a
           JOIN materias m ON m.clave = a.materia
           LEFT JOIN grupo_actividad ga ON ga.actividad_id = a.id AND ga.grupo_id = %s
           WHERE a.estado = 'Publicada' AND NOT a.eliminada
           ORDER BY m.orden, a.id""",
        (grupo["id"],),
    )


def progreso_del_grupo(grupo_id, desde=None, hasta=None):
    """{(estudiante_id, materia, actividad) normalizados: {'porcentaje', 'intentos', 'ultima_vez'}}."""
    filtro, parametros = "", [grupo_id]
    if desde and hasta:
        filtro = "AND p.ultima_vez BETWEEN %s AND %s"
        parametros += [desde, f"{hasta} 23:59:59"]
    filas = consultar(
        f"""SELECT p.estudiante_id, p.materia, p.actividad, MAX(p.porcentaje) AS porcentaje,
                   MAX(p.intentos) AS intentos, MAX(p.ultima_vez) AS ultima_vez
            FROM progreso p JOIN estudiantes e ON e.id = p.estudiante_id
            WHERE e.grupo_id = %s {filtro}
            GROUP BY p.estudiante_id, p.materia, p.actividad""",
        parametros,
    )
    return {
        (f["estudiante_id"], normalizar(f["materia"]), normalizar(f["actividad"])): {
            "porcentaje": float(f["porcentaje"]), "intentos": f["intentos"], "ultima_vez": f["ultima_vez"],
        }
        for f in filas
    }


def avance_de(progreso, estudiante_id, actividad):
    fila = progreso.get((estudiante_id, normalizar(actividad["materia"]), normalizar(actividad["nombre"])))
    return fila["porcentaje"] if fila else 0.0


def resumen_grupo(grupo, desde=None, hasta=None):
    """Estudiantes con su avance por materia, y los promedios del grupo.

    Las materias sin actividades publicadas para el grado quedan en None: no cuentan
    en los promedios (por ejemplo, Inglés en 1°).
    """
    claves = [m["clave"] for m in materias()]
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

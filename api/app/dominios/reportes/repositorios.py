"""Acceso a datos de los reportes: periodos y resultados de evaluación."""

from datetime import date

from app.compartido.base_datos import consultar


def periodo_que_contiene(dia=None):
    """El periodo que contiene la fecha (el más corto si hay varios), o None."""
    dia = dia or date.today()
    return consultar(
        "SELECT clave FROM periodos WHERE desde <= %s AND hasta >= %s ORDER BY DATEDIFF(hasta, desde), orden LIMIT 1",
        (dia, dia),
        uno=True,
    )


def ultimo_periodo():
    return consultar("SELECT clave FROM periodos ORDER BY hasta DESC, orden LIMIT 1", uno=True)


def obtener_periodo(clave):
    return consultar("SELECT * FROM periodos WHERE clave = %s", (clave,), uno=True)


def listar_periodos():
    return consultar("SELECT clave, nombre FROM periodos ORDER BY orden")


def evaluaciones_de(estudiantes_ids, desde, hasta):
    marcas = ", ".join(["%s"] * len(estudiantes_ids))
    return consultar(
        f"""SELECT e.nombre, m.clave, m.nombre_corto, ev.correctas, ev.total, ev.fecha
            FROM evaluaciones ev JOIN estudiantes e ON e.id = ev.estudiante_id JOIN materias m ON m.clave = ev.materia
            WHERE ev.estudiante_id IN ({marcas}) AND ev.fecha BETWEEN %s AND %s
            ORDER BY e.nombre, ev.fecha""",
        [*estudiantes_ids, desde, f"{hasta} 23:59:59"],
    )

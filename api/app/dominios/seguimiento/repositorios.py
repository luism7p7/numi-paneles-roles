"""Acceso a datos del seguimiento: estudiantes, actividades del grupo, progreso y evaluaciones."""

from app.compartido.base_datos import consultar, ejecutar


def materias():
    return consultar("SELECT clave, nombre_corto FROM materias ORDER BY orden")


def estudiantes_del_grupo(grupo_id):
    return consultar(
        """SELECT id, uid, nombre, racha_dias, nota_docente, version_app, ultima_sincronizacion,
                  DATEDIFF(NOW(), ultima_sincronizacion) AS dias
           FROM estudiantes WHERE grupo_id = %s ORDER BY nombre""",
        (grupo_id,),
    )


def actividades_del_grupo(grupo_id, grado):
    """Publicadas y no eliminadas: las ya programadas en la app (`en_app`) o las del panel con contenido, de ese grado."""
    return consultar(
        """SELECT a.id, a.slug, a.nombre, a.materia, m.nombre_corto AS materia_nombre, m.orden,
                  a.descripcion, a.tipo, a.en_app, a.contenido, a.actualizada_en,
                  COALESCE(ga.activa, TRUE) AS activa
           FROM actividades a
           JOIN materias m ON m.clave = a.materia
           LEFT JOIN grupo_actividad ga ON ga.actividad_id = a.id AND ga.grupo_id = %s
           WHERE a.estado = 'Publicada' AND NOT a.eliminada
             AND (a.en_app OR (a.contenido IS NOT NULL AND a.grado = %s))
           ORDER BY m.orden, a.id""",
        (grupo_id, grado),
    )


def progreso_del_grupo(grupo_id, desde=None, hasta=None):
    """Una fila por (estudiante, materia, actividad) con el mayor avance, intentos y última vez."""
    filtro, parametros = "", [grupo_id]
    if desde and hasta:
        filtro = "AND p.ultima_vez BETWEEN %s AND %s"
        parametros += [desde, f"{hasta} 23:59:59"]
    return consultar(
        f"""SELECT p.estudiante_id, p.materia, p.actividad, MAX(p.porcentaje) AS porcentaje,
                   MAX(p.intentos) AS intentos, MAX(p.ultima_vez) AS ultima_vez
            FROM progreso p JOIN estudiantes e ON e.id = p.estudiante_id
            WHERE e.grupo_id = %s {filtro}
            GROUP BY p.estudiante_id, p.materia, p.actividad""",
        parametros,
    )


def ultimas_evaluaciones(estudiante_id, limite=3):
    return consultar(
        """SELECT m.nombre_corto, ev.correctas, ev.total FROM evaluaciones ev
           JOIN materias m ON m.clave = ev.materia
           WHERE ev.estudiante_id = %s ORDER BY ev.fecha DESC LIMIT %s""",
        (estudiante_id, limite),
    )


def pertenece_al_grupo(estudiante_id, grupo_id):
    return consultar(
        "SELECT id FROM estudiantes WHERE id = %s AND grupo_id = %s", (estudiante_id, grupo_id), uno=True
    ) is not None


def guardar_nota(estudiante_id, nota):
    ejecutar("UPDATE estudiantes SET nota_docente = %s WHERE id = %s", (nota, estudiante_id))


def definir_actividad_activa(grupo_id, actividad_id, activa):
    ejecutar(
        """INSERT INTO grupo_actividad (grupo_id, actividad_id, activa) VALUES (%s, %s, %s) AS nuevo
           ON DUPLICATE KEY UPDATE activa = nuevo.activa""",
        (grupo_id, actividad_id, activa),
    )

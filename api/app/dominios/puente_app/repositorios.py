"""Acceso a datos del puente con la app: estudiantes, progreso y recursos de las actividades."""

from app.compartido.base_datos import consultar, ejecutar


def estudiante_con_grado(uid):
    return consultar(
        """SELECT e.*, g.grado FROM estudiantes e LEFT JOIN grupos g ON g.id = e.grupo_id
           WHERE e.uid = %s""",
        (uid,),
        uno=True,
    )


def estudiante_por_uid(uid):
    return consultar("SELECT id, grupo_id FROM estudiantes WHERE uid = %s", (uid,), uno=True)


def actualizar_nombre(estudiante_id, nombre):
    ejecutar("UPDATE estudiantes SET nombre = %s WHERE id = %s", (nombre, estudiante_id))


def mover_de_grupo(estudiante_id, nombre, grupo_id):
    ejecutar("UPDATE estudiantes SET nombre = %s, grupo_id = %s WHERE id = %s", (nombre, grupo_id, estudiante_id), guardar=False)


def crear_estudiante(uid, nombre, grupo_id):
    ejecutar("INSERT INTO estudiantes (uid, nombre, grupo_id) VALUES (%s, %s, %s)", (uid, nombre, grupo_id), guardar=False)


def recursos_de_la_actividad(actividad_id):
    return consultar(
        """SELECT r.id, r.nombre, r.tipo, r.version_minima, r.archivo IS NOT NULL AS descargable
           FROM actividad_recurso ar JOIN recursos r ON r.id = ar.recurso_id
           WHERE ar.actividad_id = %s ORDER BY r.id""",
        (actividad_id,),
    )


def archivo_del_recurso(recurso_id):
    fila = consultar("SELECT archivo FROM recursos WHERE id = %s", (recurso_id,), uno=True)
    return fila["archivo"] if fila else None


def guardar_progreso(estudiante_id, grado, materia, actividad, porcentaje, intentos, ultima_vez):
    """Gana el mayor avance, como en la app y su backend."""
    ejecutar(
        """INSERT INTO progreso (estudiante_id, grado, materia, actividad, porcentaje, intentos, ultima_vez)
           VALUES (%s, %s, %s, %s, %s, %s, %s) AS nuevo
           ON DUPLICATE KEY UPDATE
             ultima_vez = IF(nuevo.porcentaje >= progreso.porcentaje,
                             COALESCE(nuevo.ultima_vez, progreso.ultima_vez), progreso.ultima_vez),
             porcentaje = GREATEST(progreso.porcentaje, nuevo.porcentaje),
             intentos = GREATEST(progreso.intentos, nuevo.intentos)""",
        (estudiante_id, grado, materia, actividad, porcentaje, intentos, ultima_vez),
        guardar=False,
    )


def registrar_sincronizacion(estudiante_id, version_app, racha_dias):
    ejecutar(
        """UPDATE estudiantes SET ultima_sincronizacion = NOW(),
                  version_app = COALESCE(%s, version_app), racha_dias = COALESCE(%s, racha_dias)
           WHERE id = %s""",
        (version_app, racha_dias, estudiante_id),
        guardar=False,
    )

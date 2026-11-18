"""Acceso a datos del monitoreo técnico: servicios, eventos, informes y equipos sin sincronizar."""

from app.compartido.base_datos import consultar, ejecutar


def servicios():
    return consultar("SELECT * FROM servicios ORDER BY FIELD(clave, 'datos', 'contenido')")


def guardar_revision(clave, operativo, caido_desde, revisado_en):
    ejecutar(
        "UPDATE servicios SET operativo = %s, caido_desde = %s, revisado_en = %s WHERE clave = %s",
        (operativo, caido_desde, revisado_en, clave),
        guardar=False,
    )


def registrar_evento(nivel, mensaje):
    ejecutar("INSERT INTO eventos (nivel, mensaje) VALUES (%s, %s)", (nivel, mensaje), guardar=False)


def eventos_recientes(limite=8):
    return consultar("SELECT nivel, mensaje, fecha FROM eventos ORDER BY fecha DESC, id DESC LIMIT %s", (limite,))


def errores_ultimas_24h():
    fila = consultar(
        "SELECT COUNT(*) AS n FROM eventos WHERE nivel IN ('Crítico', 'Alerta') AND fecha >= NOW() - INTERVAL 1 DAY",
        uno=True,
    )
    return fila["n"]


def contar_sin_sincronizar(dias):
    fila = consultar(
        """SELECT COUNT(*) AS n FROM estudiantes
           WHERE ultima_sincronizacion IS NULL OR ultima_sincronizacion < NOW() - INTERVAL %s DAY""",
        (dias,),
        uno=True,
    )
    return fila["n"]


def informes_recientes(limite=5):
    return consultar(
        "SELECT id, titulo, formato, LENGTH(contenido) AS bytes FROM informes ORDER BY creado_en DESC LIMIT %s", (limite,)
    )


def obtener_informe(informe_id):
    return consultar("SELECT * FROM informes WHERE id = %s", (informe_id,), uno=True)


def crear_informe(titulo, contenido):
    return ejecutar("INSERT INTO informes (titulo, formato, contenido) VALUES (%s, 'CSV', %s)", (titulo, contenido))


def equipos_para_informe():
    """Un renglón por equipo (estudiante) con su institución, grupo, versión y días sin sincronizar."""
    return consultar(
        """SELECT i.nombre AS institucion, g.grado, g.letra, e.nombre, e.version_app,
                  e.ultima_sincronizacion, DATEDIFF(NOW(), e.ultima_sincronizacion) AS dias
           FROM estudiantes e
           LEFT JOIN grupos g ON g.id = e.grupo_id
           LEFT JOIN instituciones i ON i.id = g.institucion_id
           ORDER BY i.nombre, g.grado, g.letra, e.nombre"""
    )

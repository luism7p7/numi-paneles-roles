"""Acceso a datos de la pantalla de Inicio del administrador."""

from app.compartido.base_datos import consultar


def totales():
    return consultar(
        """SELECT (SELECT COUNT(*) FROM instituciones) AS instituciones,
                  (SELECT COUNT(*) FROM usuarios WHERE rol = 'Docente' AND estado = 'Activo') AS docentes,
                  (SELECT COUNT(*) FROM grupos) AS grupos,
                  (SELECT COUNT(*) FROM estudiantes) AS estudiantes,
                  (SELECT COUNT(*) FROM usuarios WHERE rol = 'Docente' AND estado = 'Pendiente') AS pendientes""",
        uno=True,
    )


def cobertura_por_comuna():
    return consultar(
        """SELECT i.comuna, COUNT(e.id) AS estudiantes
           FROM instituciones i
           JOIN grupos g ON g.institucion_id = i.id
           JOIN estudiantes e ON e.grupo_id = g.id
           GROUP BY i.comuna
           ORDER BY estudiantes DESC"""
    )

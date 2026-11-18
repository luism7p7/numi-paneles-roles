"""Acceso a datos de las actividades, sus recursos y el historial de cambios."""

from app.compartido.base_datos import consultar, ejecutar

# "Veces resuelta" = suma de los intentos que guardó la app para esa actividad.
# progreso.actividad guarda el NOMBRE de la actividad, igual que la app.
SQL_ACTIVIDADES = """
    SELECT a.id, a.slug, a.nombre, a.materia AS clave_materia, m.nombre AS materia, a.grado,
           a.tipo, a.descripcion, a.estado, a.en_app, a.contenido, COALESCE(SUM(p.intentos), 0) AS resuelta
    FROM actividades a
    JOIN materias m ON m.clave = a.materia
    LEFT JOIN progreso p ON p.actividad = a.nombre AND p.materia = a.materia
    WHERE NOT a.eliminada {filtro}
    GROUP BY a.id, m.nombre
    ORDER BY a.actualizada_en DESC, a.id DESC
"""


def listar():
    return consultar(SQL_ACTIVIDADES.format(filtro=""))


def por_slug(slug):
    return consultar(SQL_ACTIVIDADES.format(filtro="AND a.slug = %s"), (slug,), uno=True)


def nombre_repetido(nombre, excluir_id=0):
    return consultar(
        "SELECT 1 FROM actividades WHERE nombre = %s AND NOT eliminada AND id <> %s", (nombre, excluir_id), uno=True
    ) is not None


def slug_existe(slug):
    return consultar("SELECT 1 FROM actividades WHERE slug = %s", (slug,), uno=True) is not None


def materia_por_nombre_o_clave(valor):
    """La clave de la materia, que el formulario manda como la ve el usuario ("Ciencias naturales") o como clave."""
    fila = consultar("SELECT clave FROM materias WHERE nombre = %s OR clave = %s", (valor, valor), uno=True)
    return fila["clave"] if fila else None


def recursos_de(actividad_id):
    return consultar(
        """SELECT r.id, r.nombre FROM actividad_recurso ar JOIN recursos r ON r.id = ar.recurso_id
           WHERE ar.actividad_id = %s ORDER BY r.nombre""",
        (actividad_id,),
    )


def guardar_recursos(actividad_id, ids):
    ejecutar("DELETE FROM actividad_recurso WHERE actividad_id = %s", (actividad_id,), guardar=False)
    for recurso_id in ids:
        ejecutar("INSERT INTO actividad_recurso VALUES (%s, %s)", (actividad_id, recurso_id), guardar=False)


def crear(slug, datos):
    return ejecutar(
        """INSERT INTO actividades (slug, nombre, materia, grado, tipo, descripcion, estado, contenido)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (slug, datos["nombre"], datos["materia"], datos["grado"], datos["tipo"],
         datos["descripcion"], datos["estado"], datos["contenido"]),
        guardar=False,
    )


def actualizar(actividad_id, datos):
    ejecutar(
        """UPDATE actividades SET nombre = %s, materia = %s, grado = %s, tipo = %s, estado = %s, contenido = %s
           WHERE id = %s""",
        (datos["nombre"], datos["materia"], datos["grado"], datos["tipo"], datos["estado"],
         datos["contenido"], actividad_id),
        guardar=False,
    )


def marcar_eliminada(actividad_id):
    ejecutar("UPDATE actividades SET eliminada = TRUE WHERE id = %s", (actividad_id,), guardar=False)


def registrar_cambio(actividad_id, nombre, cambio, tipo, usuario_id):
    ejecutar(
        "INSERT INTO historial (actividad_id, actividad_nombre, cambio, tipo, usuario_id) VALUES (%s, %s, %s, %s, %s)",
        (actividad_id, nombre, cambio, tipo, usuario_id),
        guardar=False,
    )


def historial():
    return consultar(
        """SELECT h.fecha, h.actividad_nombre, h.cambio, h.tipo,
                  COALESCE(CONCAT(u.nombre, ' ', u.apellido), 'Sistema') AS hecho_por
           FROM historial h LEFT JOIN usuarios u ON u.id = h.usuario_id
           ORDER BY h.fecha DESC, h.id DESC"""
    )

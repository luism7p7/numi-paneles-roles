"""Acceso a datos de las instituciones."""

from app.compartido.base_datos import consultar, ejecutar


def listar():
    return consultar(
        """SELECT i.id, i.nombre, i.comuna, i.sedes, i.estado, COUNT(e.id) AS estudiantes
           FROM instituciones i
           LEFT JOIN grupos g ON g.institucion_id = i.id
           LEFT JOIN estudiantes e ON e.grupo_id = g.id
           GROUP BY i.id
           ORDER BY i.estado, estudiantes DESC, i.nombre"""
    )


def obtener(institucion_id):
    return consultar(
        """SELECT i.id, i.nombre, i.comuna, i.sedes, i.estado,
                  (SELECT COUNT(*) FROM estudiantes e JOIN grupos g ON g.id = e.grupo_id
                   WHERE g.institucion_id = i.id) AS estudiantes
           FROM instituciones i WHERE i.id = %s""",
        (institucion_id,),
        uno=True,
    )


def existe(institucion_id):
    return consultar("SELECT 1 FROM instituciones WHERE id = %s", (institucion_id,), uno=True) is not None


def existe_nombre(nombre):
    return consultar("SELECT 1 FROM instituciones WHERE nombre = %s", (nombre,), uno=True) is not None


def id_por_nombre(nombre):
    fila = consultar("SELECT id FROM instituciones WHERE nombre = %s", (nombre,), uno=True)
    return fila["id"] if fila else None


def crear(nombre, comuna, sedes, estado):
    return ejecutar(
        "INSERT INTO instituciones (nombre, comuna, sedes, estado) VALUES (%s, %s, %s, %s)",
        (nombre, comuna, sedes, estado),
    )

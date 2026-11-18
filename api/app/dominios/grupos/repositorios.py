"""Acceso a datos de los grupos (cursos de una institución)."""

from app.compartido.base_datos import consultar, ejecutar


def del_docente(docente_id):
    return consultar("SELECT * FROM grupos WHERE docente_id = %s ORDER BY grado, letra", (docente_id,))


def obtener(grupo_id):
    return consultar("SELECT * FROM grupos WHERE id = %s", (grupo_id,), uno=True)


def por_codigo(codigo):
    return consultar(
        """SELECT g.*, i.nombre AS institucion FROM grupos g JOIN instituciones i ON i.id = g.institucion_id
           WHERE g.codigo = %s""",
        (codigo,),
        uno=True,
    )


def existe_codigo(codigo):
    return consultar("SELECT 1 FROM grupos WHERE codigo = %s", (codigo,), uno=True) is not None


def de_la_institucion(institucion_id):
    """Grupos de una institución con su docente y cuántos estudiantes tiene cada uno."""
    return consultar(
        """SELECT g.id, g.grado, g.letra, g.docente_id, CONCAT(u.nombre, ' ', u.apellido) AS docente,
                  COUNT(e.id) AS estudiantes
           FROM grupos g
           LEFT JOIN usuarios u ON u.id = g.docente_id
           LEFT JOIN estudiantes e ON e.grupo_id = g.id
           WHERE g.institucion_id = %s
           GROUP BY g.id
           ORDER BY g.grado, g.letra""",
        (institucion_id,),
    )


def a_cargo_de_los_docentes():
    """Todos los grupos que ya tienen docente, para armar {docente_id: [grupos]}."""
    return consultar(
        "SELECT id, grado, letra, docente_id FROM grupos WHERE docente_id IS NOT NULL ORDER BY grado, letra"
    )


def existe(institucion_id, grado, letra):
    return consultar(
        "SELECT 1 FROM grupos WHERE institucion_id = %s AND grado = %s AND letra = %s",
        (institucion_id, grado, letra),
        uno=True,
    ) is not None


def ids_de_la_institucion(institucion_id, ids):
    marcas = ", ".join(["%s"] * len(ids))
    filas = consultar(f"SELECT id FROM grupos WHERE institucion_id = %s AND id IN ({marcas})", [institucion_id, *ids])
    return [f["id"] for f in filas]


def crear(institucion_id, grado, letra, codigo, vence, paquete_actualizado):
    return ejecutar(
        """INSERT INTO grupos (institucion_id, grado, letra, codigo, codigo_vence, paquete_actualizado)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (institucion_id, grado, letra, codigo, vence, paquete_actualizado),
    )


def quitar_docente(docente_id, guardar=False):
    ejecutar("UPDATE grupos SET docente_id = NULL WHERE docente_id = %s", (docente_id,), guardar=guardar)


def asignar_docente(docente_id, ids, guardar=False):
    marcas = ", ".join(["%s"] * len(ids))
    ejecutar(f"UPDATE grupos SET docente_id = %s WHERE id IN ({marcas})", [docente_id, *ids], guardar=guardar)


def renovar_codigo(grupo_id, codigo, vence):
    ejecutar("UPDATE grupos SET codigo = %s, codigo_usos = 0, codigo_vence = %s WHERE id = %s", (codigo, vence, grupo_id))


def gastar_uso_del_codigo(grupo_id, guardar=False):
    ejecutar("UPDATE grupos SET codigo_usos = codigo_usos + 1 WHERE id = %s", (grupo_id,), guardar=guardar)


def cambiar_ia(grupo_id, activada):
    ejecutar("UPDATE grupos SET ia_activada = %s WHERE id = %s", (activada, grupo_id))


def cambiar_paquete(grupo_id, version, dia):
    ejecutar("UPDATE grupos SET paquete_version = %s, paquete_actualizado = %s WHERE id = %s", (version, dia, grupo_id))

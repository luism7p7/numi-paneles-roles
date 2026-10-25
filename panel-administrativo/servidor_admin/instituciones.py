"""Instituciones y sus grupos."""

from flask import Blueprint, abort, jsonify, request

from .db import consultar, ejecutar
from .utilidades import ErrorDeDatos, entero, texto

bp = Blueprint("instituciones", __name__)

COMUNAS = ("San Cristóbal", "Palmitas", "Santa Elena", "Altavista", "San Antonio de Prado")


def nombre_grupo(grado, letra):
    return f"Grado {grado}° — grupo {letra}"


@bp.get("/api/instituciones")
def listar():
    filas = consultar(
        """SELECT i.id, i.nombre, i.comuna, i.sedes, i.estado, COUNT(e.id) AS estudiantes
           FROM instituciones i
           LEFT JOIN grupos g ON g.institucion_id = i.id
           LEFT JOIN estudiantes e ON e.grupo_id = g.id
           GROUP BY i.id
           ORDER BY i.estado, estudiantes DESC, i.nombre"""
    )
    return jsonify(filas)


@bp.get("/api/instituciones/<int:institucion_id>")
def detalle(institucion_id):
    institucion = consultar(
        """SELECT i.id, i.nombre, i.comuna, i.sedes, i.estado,
                  (SELECT COUNT(*) FROM estudiantes e JOIN grupos g ON g.id = e.grupo_id
                   WHERE g.institucion_id = i.id) AS estudiantes
           FROM instituciones i WHERE i.id = %s""",
        (institucion_id,),
        uno=True,
    )
    if institucion is None:
        abort(404, "La institución no existe.")
    grupos = consultar(
        """SELECT g.grado, g.letra, CONCAT(u.nombre, ' ', u.apellido) AS docente, COUNT(e.id) AS estudiantes
           FROM grupos g
           LEFT JOIN usuarios u ON u.id = g.docente_id
           LEFT JOIN estudiantes e ON e.grupo_id = g.id
           WHERE g.institucion_id = %s
           GROUP BY g.id
           ORDER BY g.grado, g.letra""",
        (institucion_id,),
    )
    institucion["grupos"] = [
        {
            "nombre": nombre_grupo(g["grado"], g["letra"]),
            "docente": f"{g['docente']} · {g['estudiantes']} estudiantes" if g["docente"] else None,
        }
        for g in grupos
    ]
    return jsonify(institucion)


@bp.post("/api/instituciones")
def crear():
    datos = request.get_json(silent=True) or {}
    nombre = texto(datos, "nombre", "el nombre de la institución", 120)
    comuna = str(datos.get("comuna", "")).strip()
    if comuna not in COMUNAS:
        raise ErrorDeDatos("Elige una comuna o corregimiento.")
    sedes = entero(datos.get("sedes", 1), "el número de sedes", 1, 50)
    estado = datos.get("estado", "Activa")
    if estado not in ("Activa", "Inactiva"):
        raise ErrorDeDatos("El estado debe ser Activa o Inactiva.")
    if consultar("SELECT 1 FROM instituciones WHERE nombre = %s", (nombre,), uno=True):
        raise ErrorDeDatos("Ya existe una institución con ese nombre.", 409)

    nuevo_id = ejecutar(
        "INSERT INTO instituciones (nombre, comuna, sedes, estado) VALUES (%s, %s, %s, %s)",
        (nombre, comuna, sedes, estado),
    )
    return jsonify(id=nuevo_id), 201

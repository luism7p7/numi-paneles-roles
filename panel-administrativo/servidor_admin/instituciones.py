"""Instituciones y sus grupos."""

import secrets
from datetime import date, timedelta

from flask import Blueprint, abort, jsonify, request

from .db import consultar, ejecutar
from .utilidades import ErrorDeDatos, entero, texto

bp = Blueprint("instituciones", __name__)

COMUNAS = ("San Cristóbal", "Palmitas", "Santa Elena", "Altavista", "San Antonio de Prado")
LETRAS = "ABCDEFGH"
ALFABETO_CODIGO = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # sin 0/O ni 1/I para no confundirlos


def nombre_grupo(grado, letra):
    return f"Grado {grado}° — grupo {letra}"


def codigo_libre():
    """Código para que los niños se unan al grupo, p. ej. 7K4M-92 (único)."""
    while True:
        bloque = "".join(secrets.choice(ALFABETO_CODIGO) for _ in range(4))
        codigo = f"{bloque}-{secrets.randbelow(90) + 10}"
        if not consultar("SELECT 1 FROM grupos WHERE codigo = %s", (codigo,), uno=True):
            return codigo


def grupos_de(institucion_id):
    filas = consultar(
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
    return [
        {
            "id": g["id"],
            "grado": g["grado"],
            "letra": g["letra"],
            "corto": f"{g['grado']}° {g['letra']}",
            "nombre": nombre_grupo(g["grado"], g["letra"]),
            "docente_id": g["docente_id"],
            "docente_nombre": g["docente"],
            # Texto que ya usaba el modal de detalle de la institución
            "docente": f"{g['docente']} · {g['estudiantes']} estudiantes" if g["docente"] else None,
        }
        for g in filas
    ]


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
    institucion["grupos"] = grupos_de(institucion_id)
    return jsonify(institucion)


@bp.post("/api/instituciones/<int:institucion_id>/grupos")
def crear_grupo(institucion_id):
    if not consultar("SELECT 1 FROM instituciones WHERE id = %s", (institucion_id,), uno=True):
        abort(404, "La institución no existe.")
    datos = request.get_json(silent=True) or {}
    grado = entero(datos.get("grado"), "el grado", 1, 5)
    letra = str(datos.get("letra", "")).strip().upper()
    if len(letra) != 1 or letra not in LETRAS:
        raise ErrorDeDatos(f"La letra del grupo debe ser una de {', '.join(LETRAS)}.")
    if consultar("SELECT 1 FROM grupos WHERE institucion_id = %s AND grado = %s AND letra = %s",
                 (institucion_id, grado, letra), uno=True):
        raise ErrorDeDatos(f"Ya existe el grupo {grado}° {letra} en esta institución.", 409)
    nuevo_id = ejecutar(
        """INSERT INTO grupos (institucion_id, grado, letra, codigo, codigo_vence, paquete_actualizado)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (institucion_id, grado, letra, codigo_libre(), date.today() + timedelta(days=30), date.today()),
    )
    return jsonify(next(g for g in grupos_de(institucion_id) if g["id"] == nuevo_id)), 201


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

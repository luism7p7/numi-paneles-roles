"""Actividades: catálogo, constructor, borradores, eliminación e historial."""

from flask import Blueprint, abort, jsonify, request, session

from . import recursos
from .db import confirmar, consultar, ejecutar
from .utilidades import ErrorDeDatos, entero, fecha_corta, slug, texto

bp = Blueprint("actividades", __name__)

TIPOS = ("Arrastrar", "Arrastrar y soltar", "Ordenar sílabas", "Selección múltiple",
         "Comprensión auditiva", "Memory match")

# "Veces resuelta" = suma de los intentos que guardó la app para esa actividad.
# progreso.actividad guarda el NOMBRE de la actividad, igual que la app.
SQL_ACTIVIDADES = """
    SELECT a.id, a.slug, a.nombre, a.materia AS clave_materia, m.nombre AS materia, a.grado,
           a.tipo, a.descripcion, a.estado, COALESCE(SUM(p.intentos), 0) AS resuelta
    FROM actividades a
    JOIN materias m ON m.clave = a.materia
    LEFT JOIN progreso p ON p.actividad = a.nombre AND p.materia = a.materia
    WHERE NOT a.eliminada {filtro}
    GROUP BY a.id, m.nombre
    ORDER BY a.actualizada_en DESC, a.id DESC
"""


def actividad_json(fila):
    return {
        "id": fila["slug"],
        "nombre": fila["nombre"],
        "materia": fila["materia"],
        "grado": f"{fila['grado']}°",
        "tipo": fila["tipo"],
        "descripcion": fila["descripcion"],
        "estado": fila["estado"],
        "resuelta": str(int(fila["resuelta"])) if fila["resuelta"] else "Sin uso registrado",
    }


def buscar(slug_actividad):
    fila = consultar(SQL_ACTIVIDADES.format(filtro="AND a.slug = %s"), (slug_actividad,), uno=True)
    if fila is None:
        abort(404, "La actividad no existe o fue eliminada.")
    return fila


def recursos_de(actividad_id):
    return consultar(
        """SELECT r.id, r.nombre FROM actividad_recurso ar JOIN recursos r ON r.id = ar.recurso_id
           WHERE ar.actividad_id = %s ORDER BY r.nombre""",
        (actividad_id,),
    )


def registrar(actividad_id, nombre, cambio, tipo):
    ejecutar(
        "INSERT INTO historial (actividad_id, actividad_nombre, cambio, tipo, usuario_id) VALUES (%s, %s, %s, %s, %s)",
        (actividad_id, nombre, cambio, tipo, session["usuario_id"]),
        guardar=False,
    )


def validar(datos, actividad_id=None):
    nombre = texto(datos, "nombre", "el nombre de la actividad", 120)
    repetida = consultar(
        "SELECT 1 FROM actividades WHERE nombre = %s AND NOT eliminada AND id <> %s",
        (nombre, actividad_id or 0),
        uno=True,
    )
    if repetida:
        raise ErrorDeDatos(f"Ya existe una actividad llamada «{nombre}».", 409)

    # La materia llega como la muestra el formulario ("Ciencias naturales") o como su clave
    materia = consultar(
        "SELECT clave FROM materias WHERE nombre = %s OR clave = %s",
        (str(datos.get("materia", "")).strip(),) * 2,
        uno=True,
    )
    if materia is None:
        raise ErrorDeDatos("Elige una materia válida.")

    grado = entero("".join(c for c in str(datos.get("grado", "")) if c.isdigit()), "el grado", 1, 5)
    tipo = str(datos.get("tipo", "")).strip()
    if tipo not in TIPOS:
        raise ErrorDeDatos("Elige un tipo de actividad válido.")
    estado = datos.get("estado")
    if estado not in ("Publicada", "Borrador"):
        raise ErrorDeDatos("El estado debe ser Publicada o Borrador.")

    ids = sorted({entero(i, "el recurso", 1, 10**9) for i in datos.get("recursos") or []})
    elegidos = []
    if ids:
        marcas = ", ".join(["%s"] * len(ids))
        elegidos = consultar(f"SELECT * FROM recursos WHERE id IN ({marcas})", ids)
        if len(elegidos) != len(ids):
            raise ErrorDeDatos("Uno de los recursos seleccionados ya no existe.")
        versiones = recursos.versiones_en_uso()
        for r in elegidos:
            if not recursos.recurso_json(r, versiones)["compatible"]:
                raise ErrorDeDatos(f"{r['nombre']} requiere la v{r['version_minima']} y hay equipos con versiones anteriores.")

    return {
        "nombre": nombre,
        "materia": materia["clave"],
        "grado": grado,
        "tipo": tipo,
        "estado": estado,
        "descripcion": texto(datos, "descripcion", "la descripción", 255, obligatorio=False),
        "recursos": {r["id"]: r["nombre"] for r in elegidos},
    }


def guardar_recursos(actividad_id, ids):
    ejecutar("DELETE FROM actividad_recurso WHERE actividad_id = %s", (actividad_id,), guardar=False)
    for recurso_id in ids:
        ejecutar("INSERT INTO actividad_recurso VALUES (%s, %s)", (actividad_id, recurso_id), guardar=False)


def slug_libre(nombre):
    base = slug(nombre)
    candidato, n = base, 2
    while consultar("SELECT 1 FROM actividades WHERE slug = %s", (candidato,), uno=True):
        candidato, n = f"{base}-{n}", n + 1
    return candidato


@bp.get("/api/actividades")
def listar():
    return jsonify([actividad_json(f) for f in consultar(SQL_ACTIVIDADES.format(filtro=""))])


@bp.get("/api/actividades/<slug_actividad>")
def detalle(slug_actividad):
    fila = buscar(slug_actividad)
    return jsonify(actividad_json(fila) | {"recursos": recursos_de(fila["id"])})


@bp.post("/api/actividades")
def crear():
    datos = validar(request.get_json(silent=True) or {})
    nuevo_slug = slug_libre(datos["nombre"])
    actividad_id = ejecutar(
        """INSERT INTO actividades (slug, nombre, materia, grado, tipo, descripcion, estado)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (nuevo_slug, datos["nombre"], datos["materia"], datos["grado"], datos["tipo"],
         datos["descripcion"], datos["estado"]),
        guardar=False,
    )
    guardar_recursos(actividad_id, datos["recursos"])
    if datos["estado"] == "Publicada":
        registrar(actividad_id, datos["nombre"], "Actividad publicada", "Publicada")
    else:
        registrar(actividad_id, datos["nombre"], "Guardada como borrador", "Borrador")
    confirmar()
    return jsonify(id=nuevo_slug, estado=datos["estado"]), 201


@bp.put("/api/actividades/<slug_actividad>")
def editar(slug_actividad):
    actual = buscar(slug_actividad)
    datos = validar(request.get_json(silent=True) or {}, actual["id"])
    antes = {r["id"]: r["nombre"] for r in recursos_de(actual["id"])}

    ejecutar(
        """UPDATE actividades SET nombre = %s, materia = %s, grado = %s, tipo = %s, estado = %s
           WHERE id = %s""",
        (datos["nombre"], datos["materia"], datos["grado"], datos["tipo"], datos["estado"], actual["id"]),
        guardar=False,
    )
    guardar_recursos(actual["id"], datos["recursos"])

    # Historial: una fila por cada cambio, como en la pantalla Historial
    nombre = datos["nombre"]
    if datos["estado"] == "Borrador":
        registrar(actual["id"], nombre, "Guardada como borrador", "Borrador")
    elif actual["estado"] != "Publicada":
        registrar(actual["id"], nombre, "Actividad publicada", "Publicada")
    cambios = [f"{antes[i]} retirado" for i in antes if i not in datos["recursos"]]
    cambios += [f"{datos['recursos'][i]} agregado" for i in datos["recursos"] if i not in antes]
    for campo, etiqueta in (("nombre", "Nombre"), ("materia", "Materia"), ("grado", "Grado"), ("tipo", "Tipo")):
        if str(actual["clave_materia" if campo == "materia" else campo]) != str(datos[campo]):
            cambios.append(f"{etiqueta} cambiado")
    if datos["estado"] == "Publicada" and actual["estado"] == "Publicada":
        for cambio in cambios:
            registrar(actual["id"], nombre, cambio, "Editada")
    confirmar()
    return jsonify(id=actual["slug"], estado=datos["estado"], antes=actual["estado"])


@bp.delete("/api/actividades/<slug_actividad>")
def eliminar(slug_actividad):
    actual = buscar(slug_actividad)
    ejecutar("UPDATE actividades SET eliminada = TRUE WHERE id = %s", (actual["id"],), guardar=False)
    registrar(actual["id"], actual["nombre"], "Actividad eliminada", "Eliminada")
    confirmar()
    return jsonify(nombre=actual["nombre"])


@bp.get("/api/historial")
def historial():
    filas = consultar(
        """SELECT h.fecha, h.actividad_nombre, h.cambio, h.tipo,
                  COALESCE(CONCAT(u.nombre, ' ', u.apellido), 'Sistema') AS hecho_por
           FROM historial h LEFT JOIN usuarios u ON u.id = h.usuario_id
           ORDER BY h.fecha DESC, h.id DESC"""
    )
    return jsonify([
        {
            "fecha": fecha_corta(f["fecha"]),
            "dia": f["fecha"].date().isoformat(),  # para los filtros Desde / Hasta
            "actividad": f["actividad_nombre"],
            "cambio": f["cambio"],
            "tipo": f["tipo"],
            "hecho_por": f["hecho_por"],
        }
        for f in filas
    ])

"""Usuarios y roles: docentes y administradores."""

import csv
import io
import json

from flask import Blueprint, abort, jsonify, request, session
from werkzeug.security import generate_password_hash

from .db import confirmar, consultar, ejecutar
from .utilidades import CORREO_VALIDO, ErrorDeDatos, correo, fecha_corta, iniciales, password_temporal, texto

bp = Blueprint("usuarios", __name__)

ROLES = ("Docente", "Administrador")
MAX_FILAS_IMPORTACION = 1000


def usuario_json(fila):
    return {
        "id": fila["id"],
        "nombre": fila["nombre"],
        "apellido": fila["apellido"],
        "nombre_completo": f"{fila['nombre']} {fila['apellido']}",
        "iniciales": iniciales(f"{fila['nombre']} {fila['apellido']}"),
        "correo": fila["correo"],
        "rol": fila["rol"],
        "institucion": fila["institucion"] or ("Todas" if fila["rol"] == "Administrador" else "Sin asignar"),
        "estado": fila["estado"],
        "ultimo_acceso": fecha_corta(fila["ultimo_acceso"]),
    }


def buscar(usuario_id):
    fila = consultar(
        """SELECT u.*, i.nombre AS institucion FROM usuarios u
           LEFT JOIN instituciones i ON i.id = u.institucion_id WHERE u.id = %s""",
        (usuario_id,),
        uno=True,
    )
    if fila is None:
        abort(404, "El usuario no existe.")
    return fila


def institucion_id(nombre, rol):
    """'Todas' (o vacío) solo vale para administradores."""
    if nombre in (None, "", "Todas"):
        if rol == "Docente":
            raise ErrorDeDatos("Un docente debe pertenecer a una institución.")
        return None
    fila = consultar("SELECT id FROM instituciones WHERE nombre = %s", (nombre,), uno=True)
    if fila is None:
        raise ErrorDeDatos("La institución elegida no existe.")
    return fila["id"]


def validar(datos, usuario_id=None):
    rol = datos.get("rol")
    if rol not in ROLES:
        raise ErrorDeDatos("Elige un rol válido.")
    valores = {
        "nombre": texto(datos, "nombre", "el nombre", 60),
        "apellido": texto(datos, "apellido", "el apellido", 60),
        "correo": correo(datos),
        "rol": rol,
        "institucion_id": institucion_id(datos.get("institucion"), rol),
    }
    if consultar("SELECT 1 FROM usuarios WHERE correo = %s AND id <> %s", (valores["correo"], usuario_id or 0), uno=True):
        raise ErrorDeDatos("Ya existe una cuenta con ese correo.", 409)
    return valores


@bp.get("/api/usuarios")
def listar():
    filas = consultar(
        """SELECT u.*, i.nombre AS institucion FROM usuarios u
           LEFT JOIN instituciones i ON i.id = u.institucion_id
           ORDER BY FIELD(u.estado, 'Pendiente', 'Activo', 'Inactivo'), u.nombre, u.apellido"""
    )
    return jsonify([usuario_json(f) for f in filas])


@bp.post("/api/usuarios")
def crear():
    v = validar(request.get_json(silent=True) or {})
    nuevo_id = ejecutar(
        """INSERT INTO usuarios (nombre, apellido, correo, rol, institucion_id, estado)
           VALUES (%s, %s, %s, %s, %s, 'Pendiente')""",
        (v["nombre"], v["apellido"], v["correo"], v["rol"], v["institucion_id"]),
    )
    return jsonify(usuario_json(buscar(nuevo_id))), 201


@bp.put("/api/usuarios/<int:usuario_id>")
def editar(usuario_id):
    buscar(usuario_id)
    v = validar(request.get_json(silent=True) or {}, usuario_id)
    if usuario_id == session["usuario_id"] and v["rol"] != "Administrador":
        raise ErrorDeDatos("No puedes quitarte a ti mismo el rol de administrador.")
    ejecutar(
        "UPDATE usuarios SET nombre = %s, apellido = %s, correo = %s, rol = %s, institucion_id = %s WHERE id = %s",
        (v["nombre"], v["apellido"], v["correo"], v["rol"], v["institucion_id"], usuario_id),
    )
    return jsonify(usuario_json(buscar(usuario_id)))


@bp.patch("/api/usuarios/<int:usuario_id>/estado")
def cambiar_estado(usuario_id):
    actual = buscar(usuario_id)
    nuevo = (request.get_json(silent=True) or {}).get("estado")
    if nuevo not in ("Activo", "Inactivo"):
        raise ErrorDeDatos("El estado debe ser Activo o Inactivo.")
    if usuario_id == session["usuario_id"] and nuevo == "Inactivo":
        raise ErrorDeDatos("No puedes desactivar tu propia cuenta.")

    # Una cuenta que nunca ha tenido contraseña recibe una temporal al activarse
    temporal = None
    if nuevo == "Activo" and not actual["password_hash"]:
        temporal = password_temporal()
        ejecutar("UPDATE usuarios SET password_hash = %s WHERE id = %s",
                 (generate_password_hash(temporal), usuario_id), guardar=False)
    ejecutar("UPDATE usuarios SET estado = %s WHERE id = %s", (nuevo, usuario_id), guardar=False)
    confirmar()
    return jsonify(usuario=usuario_json(buscar(usuario_id)), password_temporal=temporal)


def leer_filas(archivo):
    """Devuelve una lista de diccionarios con nombre, apellido y correo_institucional."""
    contenido = archivo.read().decode("utf-8-sig", errors="replace")
    if archivo.filename.lower().endswith(".json"):
        try:
            datos = json.loads(contenido)
        except json.JSONDecodeError:
            raise ErrorDeDatos("El archivo JSON no es válido.") from None
        if not isinstance(datos, list) or not all(isinstance(d, dict) for d in datos):
            raise ErrorDeDatos("El JSON debe ser una lista de objetos con nombre, apellido y correo_institucional.")
        return datos

    primera = contenido.splitlines()[0] if contenido.strip() else ""
    separador = ";" if primera.count(";") > primera.count(",") else ","  # Excel en español usa ;
    filas = [f for f in csv.reader(io.StringIO(contenido), delimiter=separador) if any(c.strip() for c in f)]
    if filas and filas[0][0].strip().lower() == "nombre":
        filas = filas[1:]  # el archivo trae encabezado
    columnas = ("nombre", "apellido", "correo_institucional")
    return [dict(zip(columnas, (c.strip() for c in f))) for f in filas]


@bp.post("/api/usuarios/importar")
def importar():
    archivo = request.files.get("archivo")
    if archivo is None or not archivo.filename:
        raise ErrorDeDatos("Selecciona un archivo .csv o .json.")
    if not archivo.filename.lower().endswith((".csv", ".json")):
        raise ErrorDeDatos("El archivo debe ser .csv o .json.")
    rol = request.form.get("rol")
    if rol not in ROLES:
        raise ErrorDeDatos("Elige un rol válido.")
    inst_id = institucion_id(request.form.get("institucion"), rol)

    filas = leer_filas(archivo)
    if not filas:
        raise ErrorDeDatos("El archivo no tiene filas para importar.")
    if len(filas) > MAX_FILAS_IMPORTACION:
        raise ErrorDeDatos(f"El archivo tiene más de {MAX_FILAS_IMPORTACION} filas.")

    creados, omitidos, vistos = 0, [], set()
    for numero, fila in enumerate(filas, start=1):
        nombre = str(fila.get("nombre") or "").strip()[:60]
        apellido = str(fila.get("apellido") or "").strip()[:60]
        email = str(fila.get("correo_institucional") or fila.get("correo") or "").strip().lower()
        if not nombre or not apellido or not CORREO_VALIDO.match(email) or len(email) > 120:
            omitidos.append(f"Fila {numero}: datos incompletos o correo inválido")
        elif email in vistos or consultar("SELECT 1 FROM usuarios WHERE correo = %s", (email,), uno=True):
            omitidos.append(f"Fila {numero}: {email} ya tiene cuenta")
        else:
            ejecutar(
                """INSERT INTO usuarios (nombre, apellido, correo, rol, institucion_id, estado)
                   VALUES (%s, %s, %s, %s, %s, 'Pendiente')""",
                (nombre, apellido, email, rol, inst_id),
                guardar=False,
            )
            creados += 1
        vistos.add(email)
    confirmar()
    return jsonify(creados=creados, omitidos=omitidos)


@bp.post("/api/registro")
def registro():
    """Solicitud de cuenta desde crear-usuario.html (no pide sesión). Queda pendiente."""
    datos = request.get_json(silent=True) or {}
    nombre = texto(datos, "nombre", "tu nombre", 60)
    apellido = texto(datos, "apellido", "tu apellido", 60)
    email = correo(datos)
    if consultar("SELECT 1 FROM usuarios WHERE correo = %s", (email,), uno=True):
        raise ErrorDeDatos("Ya existe una cuenta con ese correo.", 409)
    ejecutar(
        "INSERT INTO usuarios (nombre, apellido, correo, rol, estado) VALUES (%s, %s, %s, 'Docente', 'Pendiente')",
        (nombre, apellido, email),
    )
    return jsonify(mensaje="Solicitud enviada. Un administrador revisará tu cuenta."), 201

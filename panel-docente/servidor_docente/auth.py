"""Inicio de sesión del docente, su perfil y el grupo con el que trabaja."""

from flask import Blueprint, abort, jsonify, request, session
from werkzeug.security import check_password_hash

from . import calculos
from .db import consultar, ejecutar
from .utilidades import error, iniciales, nombre_grupo

bp = Blueprint("auth", __name__)

MENSAJE_ESTADO = {
    "Pendiente": "Tu cuenta todavía está pendiente de aprobación.",
    "Inactivo": "Tu cuenta está desactivada. Habla con la coordinación de tu sede.",
}


def grupos_del_docente(docente_id):
    return consultar(
        "SELECT * FROM grupos WHERE docente_id = %s ORDER BY grado, letra",
        (docente_id,),
    )


def grupo_actual():
    """Grupo activo de la sesión. Siempre es uno de los grupos del docente."""
    grupos = grupos_del_docente(session["usuario_id"])
    if not grupos:
        abort(409, "No tienes grupos asignados. La coordinación de la sede los habilita.")
    for g in grupos:
        if g["id"] == session.get("grupo_id"):
            return g
    session["grupo_id"] = grupos[0]["id"]
    return grupos[0]


def grupo_json(g, resumen=None):
    resumen = resumen or calculos.resumen_grupo(g)
    return {
        "id": g["id"],
        "grado": f"{g['grado']}°",
        "corto": f"{g['grado']}° {g['letra']}",
        "nombre": nombre_grupo(g["grado"], g["letra"]),
        "estudiantes": len(resumen["estudiantes"]),
        "codigo": g["codigo"],
        "avance": resumen["avance"],
        "activos": resumen["activos"],
    }


@bp.post("/api/login")
def login():
    datos = request.get_json(silent=True) or {}
    correo = str(datos.get("correo", "")).strip().lower()
    password = str(datos.get("password", ""))
    if not correo or not password:
        return error("Escribe tu correo y tu contraseña.")

    usuario = consultar(
        "SELECT id, nombre, apellido, password_hash, rol, estado FROM usuarios WHERE correo = %s",
        (correo,),
        uno=True,
    )
    if usuario is None or not usuario["password_hash"] or not check_password_hash(usuario["password_hash"], password):
        return error("Correo o contraseña incorrectos.", 401)
    if usuario["rol"] != "Docente":
        return error("Esta cuenta no es de docente. Usa el panel administrativo.", 403)
    if usuario["estado"] != "Activo":
        return error(MENSAJE_ESTADO[usuario["estado"]], 403)

    session.clear()
    session["usuario_id"] = usuario["id"]
    grupos = grupos_del_docente(usuario["id"])
    session["grupo_id"] = grupos[0]["id"] if grupos else None
    ejecutar("UPDATE usuarios SET ultimo_acceso = NOW() WHERE id = %s", (usuario["id"],))
    return jsonify(nombre=f"{usuario['nombre']} {usuario['apellido']}")


@bp.get("/api/me")
def yo():
    u = consultar(
        """SELECT u.nombre, u.apellido, u.correo, u.documento, u.sede, u.rol,
                  i.nombre AS institucion, i.comuna
           FROM usuarios u LEFT JOIN instituciones i ON i.id = u.institucion_id
           WHERE u.id = %s""",
        (session["usuario_id"],),
        uno=True,
    )
    grupos = grupos_del_docente(session["usuario_id"])
    activo = grupo_actual()["id"] if grupos else None
    documento = u["documento"] or ""
    return jsonify(
        nombre=u["nombre"],
        apellido=u["apellido"],
        nombre_completo=f"Prof. {u['nombre']} {u['apellido']}",
        iniciales=iniciales(f"{u['nombre']} {u['apellido']}"),
        correo=u["correo"],
        documento=f"C.C. {'•' * max(0, len(documento) - 4)}{documento[-4:]}" if documento else "Sin registrar",
        rol=u["rol"],
        institucion=u["institucion"] or "Sin institución asignada",
        sede=u["sede"],
        comuna=u["comuna"] or "—",
        grupos=[grupo_json(g) for g in grupos],
        grupo_activo=activo,
    )


@bp.post("/api/grupo-activo")
def cambiar_grupo():
    grupo_id = (request.get_json(silent=True) or {}).get("grupo_id")
    if not any(g["id"] == grupo_id for g in grupos_del_docente(session["usuario_id"])):
        return error("Ese grupo no está a tu cargo.", 403)
    session["grupo_id"] = grupo_id
    return jsonify(grupo_activo=grupo_id)

"""Inicio de sesión: valida correo, contraseña y rol, y entrega el token."""

from werkzeug.security import check_password_hash

from app.dominios.usuarios import repositorios as usuarios
from app.excepciones import ErrorDeDatos, NoAutenticado, PermisoDenegado
from app.seguridad import ADMINISTRADOR, DOCENTE, emitir_token

MENSAJE_OTRO_ROL = {
    ADMINISTRADOR: "Esta cuenta no tiene permisos de administrador.",
    DOCENTE: "Esta cuenta no es de docente. Usa el panel administrativo.",
}

MENSAJE_ESTADO = {
    ADMINISTRADOR: {
        "Pendiente": "Tu cuenta todavía está pendiente de aprobación.",
        "Inactivo": "Tu cuenta está desactivada. Habla con otro administrador.",
    },
    DOCENTE: {
        "Pendiente": "Tu cuenta todavía está pendiente de aprobación.",
        "Inactivo": "Tu cuenta está desactivada. Habla con la coordinación de tu sede.",
    },
}


def iniciar_sesion(correo, password, rol):
    correo = correo.strip().lower()
    if not correo or not password:
        raise ErrorDeDatos("Escribe tu correo y tu contraseña.")

    usuario = usuarios.buscar_para_login(correo)
    # Mismo mensaje si el correo no existe o la contraseña falla: así no se revela qué correos hay.
    if usuario is None or not usuario["password_hash"] or not check_password_hash(usuario["password_hash"], password):
        raise NoAutenticado("Correo o contraseña incorrectos.")
    if usuario["rol"] != rol:
        raise PermisoDenegado(MENSAJE_OTRO_ROL[rol])
    if usuario["estado"] != "Activo":
        raise PermisoDenegado(MENSAJE_ESTADO[rol][usuario["estado"]])

    usuarios.registrar_acceso(usuario["id"])
    return {
        "access_token": emitir_token(usuario),
        "nombre": f"{usuario['nombre']} {usuario['apellido']}",
        "rol": usuario["rol"],
    }

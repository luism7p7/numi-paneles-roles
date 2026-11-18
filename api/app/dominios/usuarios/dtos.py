"""Validación de lo que llega al crear, editar y solicitar cuentas."""

from marshmallow import fields, validate

from app.compartido.validaciones import Correo, Entero, Esquema, Texto

ROLES = ("Docente", "Administrador")
ESTADOS = ("Activo", "Inactivo")
MENSAJE_ROL = "Elige un rol válido."


class UsuarioDTO(Esquema):
    """Crear o editar una cuenta."""

    rol = fields.String(
        required=True,
        validate=validate.OneOf(ROLES, error=MENSAJE_ROL),
        error_messages={"required": MENSAJE_ROL, "null": MENSAJE_ROL},
    )
    nombre = Texto("el nombre", 60)
    apellido = Texto("el apellido", 60)
    correo = Correo()
    institucion = fields.String(load_default="")
    # Si no viene, no se tocan los grupos del docente
    grupos = fields.List(Entero("el grupo", 1, 10**9), load_default=None)


class SolicitudCuentaDTO(Esquema):
    """Solicitud de cuenta desde la pantalla pública: queda pendiente."""

    nombre = Texto("tu nombre", 60)
    apellido = Texto("tu apellido", 60)
    correo = Correo()


class CambiarEstadoDTO(Esquema):
    estado = fields.String(
        required=True,
        validate=validate.OneOf(ESTADOS, error="El estado debe ser Activo o Inactivo."),
        error_messages={"required": "El estado debe ser Activo o Inactivo.", "null": "El estado debe ser Activo o Inactivo."},
    )


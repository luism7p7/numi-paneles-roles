"""Acceso a datos de las cuentas (docentes y administradores)."""

from app.compartido.base_datos import consultar, ejecutar


def buscar_para_login(correo):
    return consultar(
        "SELECT id, nombre, apellido, password_hash, rol, estado FROM usuarios WHERE correo = %s",
        (correo,),
        uno=True,
    )


def registrar_acceso(usuario_id):
    ejecutar("UPDATE usuarios SET ultimo_acceso = NOW() WHERE id = %s", (usuario_id,))


def obtener(usuario_id):
    """La cuenta con el nombre de su institución, o None."""
    return consultar(
        """SELECT u.*, i.nombre AS institucion FROM usuarios u
           LEFT JOIN instituciones i ON i.id = u.institucion_id WHERE u.id = %s""",
        (usuario_id,),
        uno=True,
    )


def listar():
    """Todas las cuentas; las pendientes primero."""
    return consultar(
        """SELECT u.*, i.nombre AS institucion FROM usuarios u
           LEFT JOIN instituciones i ON i.id = u.institucion_id
           ORDER BY FIELD(u.estado, 'Pendiente', 'Activo', 'Inactivo'), u.nombre, u.apellido"""
    )


def perfil_del_docente(usuario_id):
    return consultar(
        """SELECT u.nombre, u.apellido, u.correo, u.documento, u.sede, u.rol,
                  i.nombre AS institucion, i.comuna
           FROM usuarios u LEFT JOIN instituciones i ON i.id = u.institucion_id
           WHERE u.id = %s""",
        (usuario_id,),
        uno=True,
    )


def correo_existe(correo, excluir_id=0):
    return consultar(
        "SELECT 1 FROM usuarios WHERE correo = %s AND id <> %s", (correo, excluir_id), uno=True
    ) is not None


def crear(nombre, apellido, correo, rol, institucion_id, guardar=False):
    """Cuenta nueva: queda Pendiente y sin contraseña hasta que un administrador la active."""
    return ejecutar(
        """INSERT INTO usuarios (nombre, apellido, correo, rol, institucion_id, estado)
           VALUES (%s, %s, %s, %s, %s, 'Pendiente')""",
        (nombre, apellido, correo, rol, institucion_id),
        guardar=guardar,
    )


def actualizar(usuario_id, nombre, apellido, correo, rol, institucion_id):
    ejecutar(
        "UPDATE usuarios SET nombre = %s, apellido = %s, correo = %s, rol = %s, institucion_id = %s WHERE id = %s",
        (nombre, apellido, correo, rol, institucion_id, usuario_id),
        guardar=False,
    )


def cambiar_estado(usuario_id, estado):
    ejecutar("UPDATE usuarios SET estado = %s WHERE id = %s", (estado, usuario_id), guardar=False)


def guardar_password_hash(usuario_id, password_hash, guardar=True):
    ejecutar("UPDATE usuarios SET password_hash = %s WHERE id = %s", (password_hash, usuario_id), guardar=guardar)

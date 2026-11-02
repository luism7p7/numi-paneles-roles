"""Códigos de grupo y contraseñas temporales: letras y números fáciles de leer y de dictar."""

import secrets
from datetime import date, timedelta

from .db import consultar

ALFABETO = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # sin 0/O ni 1/I para no confundirlos
DIAS_VIGENCIA_CODIGO = 30


def vencimiento_del_codigo():
    """Fecha en que vence un código de grupo recién creado."""
    return date.today() + timedelta(days=DIAS_VIGENCIA_CODIGO)


def codigo_de_grupo_libre():
    """Código para que los niños se unan al grupo, p. ej. 7K4M-92 (que ningún otro grupo tenga)."""
    while True:
        bloque = "".join(secrets.choice(ALFABETO) for _ in range(4))
        codigo = f"{bloque}-{secrets.randbelow(90) + 10}"
        if not consultar("SELECT 1 FROM grupos WHERE codigo = %s", (codigo,), uno=True):
            return codigo


def password_temporal():
    """Contraseña de un solo uso que ve el administrador al activar una cuenta, p. ej. K3M7-X9PQ."""
    caracteres = "".join(secrets.choice(ALFABETO) for _ in range(8))
    return f"{caracteres[:4]}-{caracteres[4:]}"

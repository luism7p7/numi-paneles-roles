"""Acceso a MySQL: una conexión por petición, guardada en `g`."""

import pymysql
from flask import current_app, g


def get_db():
    if "db" not in g:
        cfg = current_app.config
        g.db = pymysql.connect(
            host=cfg["DB_HOST"],
            port=cfg["DB_PORT"],
            user=cfg["DB_USER"],
            password=cfg["DB_PASSWORD"],
            database=cfg["DB_NAME"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,  # cada fila llega como diccionario
        )
    return g.db


def cerrar_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def consultar(sql, parametros=(), uno=False):
    """SELECT: devuelve una lista de filas, o una sola fila (o None) si uno=True."""
    with get_db().cursor() as cur:
        cur.execute(sql, parametros)
        return cur.fetchone() if uno else cur.fetchall()


def ejecutar(sql, parametros=(), guardar=True):
    """INSERT / UPDATE / DELETE. Devuelve el id insertado.

    Con guardar=False no hace commit: sirve para agrupar varios cambios en una
    transacción y confirmarlos juntos al final con confirmar().
    """
    db = get_db()
    with db.cursor() as cur:
        cur.execute(sql, parametros)
        nuevo_id = cur.lastrowid
    if guardar:
        db.commit()
    return nuevo_id


def confirmar():
    get_db().commit()

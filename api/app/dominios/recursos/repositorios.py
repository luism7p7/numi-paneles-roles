"""Acceso a datos de los recursos (imágenes, audios y videos) y de las versiones de la app en uso."""

from app.compartido.base_datos import consultar, ejecutar


def versiones_en_uso():
    """{'1.4.0': 549, '1.3.2': 142, ...}: cuántos equipos tienen cada versión de la app."""
    filas = consultar(
        "SELECT version_app, COUNT(*) AS equipos FROM estudiantes WHERE version_app IS NOT NULL GROUP BY version_app"
    )
    return {f["version_app"]: f["equipos"] for f in filas}


def listar():
    return consultar("SELECT * FROM recursos ORDER BY carpeta, tipo, id")


def por_ids(ids):
    marcas = ", ".join(["%s"] * len(ids))
    return consultar(f"SELECT * FROM recursos WHERE id IN ({marcas})", sorted(ids))


def existe_en_carpeta(carpeta, nombre):
    return consultar("SELECT 1 FROM recursos WHERE carpeta = %s AND nombre = %s", (carpeta, nombre), uno=True) is not None


def crear(nombre, tipo, carpeta, emoji, archivo):
    return ejecutar(
        "INSERT INTO recursos (nombre, tipo, carpeta, emoji, archivo) VALUES (%s, %s, %s, %s, %s)",
        (nombre, tipo, carpeta, emoji, archivo),
    )

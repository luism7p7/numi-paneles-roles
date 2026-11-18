"""Resumen de la pantalla de Inicio: indicadores generales, cobertura y lo que requiere acción."""

from datetime import datetime

from app.compartido.fechas import MESES
from app.dominios.monitoreo import servicios as monitoreo

from . import repositorios as repo


def resumen():
    ahora = datetime.now()
    return {
        "fecha": f"{ahora.day} {MESES[ahora.month - 1]}, {ahora:%H:%M}",
        "totales": repo.totales(),
        "cobertura": repo.cobertura_por_comuna(),
        "sin_sincronizar": monitoreo.contar_sin_sincronizar(),
        "servicios_caidos": monitoreo.servicios_caidos(),
    }

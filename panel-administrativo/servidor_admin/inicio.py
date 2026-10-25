"""Inicio: indicadores generales, cobertura y lo que requiere acción."""

from datetime import datetime

from flask import Blueprint, jsonify

from . import monitoreo
from .db import consultar
from .utilidades import MESES

bp = Blueprint("inicio", __name__)


@bp.get("/api/inicio")
def resumen():
    totales = consultar(
        """SELECT (SELECT COUNT(*) FROM instituciones) AS instituciones,
                  (SELECT COUNT(*) FROM usuarios WHERE rol = 'Docente' AND estado = 'Activo') AS docentes,
                  (SELECT COUNT(*) FROM grupos) AS grupos,
                  (SELECT COUNT(*) FROM estudiantes) AS estudiantes,
                  (SELECT COUNT(*) FROM usuarios WHERE rol = 'Docente' AND estado = 'Pendiente') AS pendientes""",
        uno=True,
    )
    cobertura = consultar(
        """SELECT i.comuna, COUNT(e.id) AS estudiantes
           FROM instituciones i
           JOIN grupos g ON g.institucion_id = i.id
           JOIN estudiantes e ON e.grupo_id = g.id
           GROUP BY i.comuna
           ORDER BY estudiantes DESC"""
    )
    ahora = datetime.now()
    return jsonify(
        fecha=f"{ahora.day} {MESES[ahora.month - 1]}, {ahora:%H:%M}",
        totales=totales,
        cobertura=cobertura,
        sin_sincronizar=monitoreo.contar_sin_sincronizar(),
        servicios_caidos=[monitoreo.servicio_json(s) for s in monitoreo.revisar_servicios() if s["operativo"] is not None and not s["operativo"]],
    )

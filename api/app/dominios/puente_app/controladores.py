"""Puente con la app Numi: lo llama el BACKEND de la app (servidor a servidor).

Autenticación: cabecera  X-Api-Key: <APP_API_KEY del .env>.
La clave nunca debe ir dentro de la app del celular; el celular habla con su
backend y el backend reenvía aquí. Es un contrato con la app: las respuestas son
JSON sin el envoltorio {success, data} y los errores son {"error": "mensaje"}.

    POST /api/app/v1/unirse          el niño escribe el código del grupo
    GET  /api/app/v1/actividades     actividades activas para el grupo del niño (con su contenido)
    GET  /api/app/v1/recursos/<id>   archivo de una imagen, audio o video
    PUT  /api/app/v1/progreso        sube el progreso (gana el mayor avance, como en la app)
"""

import hmac

from flask import Blueprint, current_app, jsonify, request, send_from_directory

from app.compartido.validaciones import cargar
from app.excepciones import ErrorDeDatos

from . import servicios
from .dtos import ProgresoDTO, UnirseDTO

puente_bp = Blueprint("puente_app", __name__)


@puente_bp.before_request
def exigir_clave():
    clave = current_app.config["APP_API_KEY"]
    if not clave:
        raise ErrorDeDatos("El puente con la app está apagado: falta APP_API_KEY en el .env.", 503)
    if not hmac.compare_digest(request.headers.get("X-Api-Key", ""), clave):
        raise ErrorDeDatos("Clave de la app inválida.", 401)


def _cuerpo():
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        raise ErrorDeDatos("El cuerpo debe ser un objeto JSON.")
    return datos


@puente_bp.post("/unirse")
def unirse():
    return jsonify(servicios.unirse(cargar(UnirseDTO(), _cuerpo())))


@puente_bp.get("/actividades")
def actividades():
    return jsonify(servicios.actividades(request.args.get("uid")))


@puente_bp.get("/recursos/<int:recurso_id>")
def recurso(recurso_id):
    """Archivo de un recurso para que la app lo guarde y lo use sin internet."""
    archivo = servicios.archivo_del_recurso(recurso_id)
    return send_from_directory(current_app.config["CARPETA_UPLOADS"], archivo, max_age=86400)


@puente_bp.put("/progreso")
def progreso():
    return jsonify(servicios.subir_progreso(cargar(ProgresoDTO(), _cuerpo())))

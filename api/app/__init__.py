"""API de Numi (Flask + MySQL): un solo backend para el panel administrativo y el panel docente.

Organización por dominios. Cada dominio tiene sus capas:

    controladores.py   rutas (Blueprint): reciben la petición y responden
    dtos.py            validación de lo que llega (Marshmallow)
    servicios.py       reglas de negocio
    repositorios.py    SQL: lo único que habla con la base de datos

Prefijos de las rutas:  /api/v1/auth · /api/v1/admin/... · /api/v1/docente/... · /api/app/v1/... (puente con la app)
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException

from app.compartido.base_datos import cerrar_db
from app.config import Config
from app.excepciones import ErrorDeDatos
from app.respuestas import exito, fallo

API_VERSION = "v1"
PREFIJO = f"/api/{API_VERSION}"


def _primer_mensaje(mensajes):
    """El primer mensaje de un error de validación de Marshmallow (puede venir anidado)."""
    if isinstance(mensajes, dict):
        mensajes = next(iter(mensajes.values()), "Datos de entrada inválidos.")
    if isinstance(mensajes, list):
        mensajes = mensajes[0] if mensajes else "Datos de entrada inválidos."
        return _primer_mensaje(mensajes) if isinstance(mensajes, (dict, list)) else mensajes
    return str(mensajes)


def _registrar_rutas(app):
    from app.dominios.actividades.controladores import actividades_bp, historial_bp
    from app.dominios.autenticacion.controladores import auth_bp
    from app.dominios.docente.controladores import docente_bp
    from app.dominios.gestion.controladores import gestion_bp
    from app.dominios.inicio.controladores import inicio_bp
    from app.dominios.instituciones.controladores import instituciones_bp
    from app.dominios.monitoreo.controladores import informes_bp, monitoreo_bp
    from app.dominios.puente_app.controladores import puente_bp
    from app.dominios.recursos.controladores import archivos_bp, recursos_bp
    from app.dominios.reportes.controladores import reportes_bp
    from app.dominios.seguimiento.controladores import seguimiento_bp
    from app.dominios.usuarios.controladores import usuarios_bp

    rutas = [
        (auth_bp, f"{PREFIJO}/auth"),
        (archivos_bp, f"{PREFIJO}/archivos"),
        # Administrador
        (inicio_bp, f"{PREFIJO}/admin/inicio"),
        (actividades_bp, f"{PREFIJO}/admin/actividades"),
        (historial_bp, f"{PREFIJO}/admin/historial"),
        (recursos_bp, f"{PREFIJO}/admin/recursos"),
        (instituciones_bp, f"{PREFIJO}/admin/instituciones"),
        (usuarios_bp, f"{PREFIJO}/admin/usuarios"),
        (monitoreo_bp, f"{PREFIJO}/admin/monitoreo"),
        (informes_bp, f"{PREFIJO}/admin/informes"),
        # Docente
        (docente_bp, f"{PREFIJO}/docente"),
        (seguimiento_bp, f"{PREFIJO}/docente"),
        (reportes_bp, f"{PREFIJO}/docente/reportes"),
        (gestion_bp, f"{PREFIJO}/docente/gestion"),
        # Puente con la app del celular (contrato propio, no usa /api/v1)
        (puente_bp, "/api/app/v1"),
    ]
    for blueprint, prefijo in rutas:
        app.register_blueprint(blueprint, url_prefix=prefijo)


def _registrar_errores(app):
    def responder(mensaje, codigo, detalles=None):
        # El puente con la app siempre respondió {"error": "mensaje"}: la app depende de ese formato
        if request.path.startswith("/api/app/"):
            return jsonify(error=mensaje), codigo
        return fallo(mensaje, codigo, detalles)

    @app.errorhandler(ErrorDeDatos)
    def error_de_datos(e):
        return responder(e.mensaje, e.codigo, e.detalles)

    @app.errorhandler(ValidationError)
    def datos_invalidos(e):
        return responder(_primer_mensaje(e.messages), 400, e.messages)

    @app.errorhandler(HTTPException)
    def error_http(e):
        # La API siempre responde JSON, también en errores 404 o 405
        if request.path.startswith("/api/"):
            return responder(e.description, e.code)
        return e

    @app.errorhandler(Exception)
    def error_interno(e):
        app.logger.exception(e)
        return responder("Error interno del servidor.", 500)


def crear_app(config_extra=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_extra:
        app.config.update(config_extra)

    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ALLOWED_ORIGINS"]}},
         expose_headers=["Content-Disposition"])
    app.teardown_appcontext(cerrar_db)

    @app.get(f"{PREFIJO}/salud")
    def salud():
        return exito({"servicio": "numi-api", "version": API_VERSION})

    _registrar_rutas(app)
    _registrar_errores(app)
    return app

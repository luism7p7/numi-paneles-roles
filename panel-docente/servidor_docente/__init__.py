"""Panel docente de Numi (Flask + MySQL).

Sirve los mismos archivos del front-end (.html, css/, js/, img/) sin modificarlos
y agrega la API JSON en /api/... que usa js/app.js, más el puente con la app
en /api/app/v1/...
"""

from flask import Flask, abort, redirect, request, send_from_directory, session
from werkzeug.exceptions import HTTPException

from . import auth, gestion, puente_app, reportes, seguimiento
from .config import CARPETA_PANEL, Config
from .db import cerrar_db
from .utilidades import ErrorDeDatos, error

# Páginas que se pueden abrir sin haber iniciado sesión
PAGINAS_PUBLICAS = {"index"}


def create_app(config_extra=None):
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)
    if config_extra:
        app.config.update(config_extra)

    app.teardown_appcontext(cerrar_db)
    for modulo in (auth, seguimiento, reportes, gestion, puente_app):
        app.register_blueprint(modulo.bp)

    @app.before_request
    def exigir_sesion():
        # El puente con la app usa su propia clave (ver puente_app.py)
        if "usuario_id" in session or request.path.startswith("/api/app/"):
            return None
        if request.path.startswith("/api/") and request.endpoint != "auth.login":
            return error("Tu sesión terminó. Vuelve a iniciar sesión.", 401)
        if request.endpoint == "pagina" and request.view_args["nombre"] not in PAGINAS_PUBLICAS:
            return redirect("/index.html")
        return None

    @app.errorhandler(ErrorDeDatos)
    def datos_invalidos(e):
        return error(e.mensaje, e.codigo)

    @app.errorhandler(HTTPException)
    def error_http(e):
        if request.path.startswith("/api/"):
            return error(e.description, e.code)
        return e

    @app.get("/")
    def raiz():
        return redirect("/panel.html" if "usuario_id" in session else "/index.html")

    @app.get("/<nombre>.html")
    def pagina(nombre):
        # "Cerrar sesión" lleva a index.html: abrir el login cierra la sesión
        if nombre == "index":
            session.clear()
        if not (CARPETA_PANEL / f"{nombre}.html").is_file():
            abort(404)
        return send_from_directory(CARPETA_PANEL, f"{nombre}.html")

    @app.get("/<any(css, js, img):carpeta>/<path:archivo>")
    def estatico(carpeta, archivo):
        return send_from_directory(CARPETA_PANEL / carpeta, archivo)

    return app

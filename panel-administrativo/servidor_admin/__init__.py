"""Panel administrativo de Numi (Flask + MySQL).

Sirve los mismos archivos del front-end (.html, css/, js/, img/) sin modificarlos
y agrega la API JSON en /api/... que usa js/app.js.
"""

from flask import Flask, redirect, request, session

from comun.db import cerrar_db
from comun.errores import error
from comun.web import instalar_front

from . import actividades, auth, inicio, instituciones, monitoreo, recursos, usuarios
from .config import CARPETA_PANEL, Config

# Páginas que se pueden abrir sin haber iniciado sesión
PAGINAS_PUBLICAS = {"index", "crear-usuario"}
# Endpoints de la API que no piden sesión
API_PUBLICA = {"auth.login", "usuarios.registro"}


def create_app(config_extra=None):
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)
    if config_extra:
        app.config.update(config_extra)

    app.teardown_appcontext(cerrar_db)
    for modulo in (auth, inicio, actividades, recursos, instituciones, usuarios, monitoreo):
        app.register_blueprint(modulo.bp)

    @app.before_request
    def exigir_sesion():
        if "usuario_id" in session:
            return None
        if request.path.startswith("/api/") and request.endpoint not in API_PUBLICA:
            return error("Tu sesión terminó. Vuelve a iniciar sesión.", 401)
        if request.endpoint == "pagina" and request.view_args["nombre"] not in PAGINAS_PUBLICAS:
            return redirect("/index.html")
        if request.endpoint == "recursos.archivo_subido":
            return redirect("/index.html")
        return None

    instalar_front(app, CARPETA_PANEL, pagina_inicial="inicio.html")

    return app

"""Panel administrativo de Numi (Flask + MySQL).

Sirve los mismos archivos del front-end (.html, css/, js/, img/) sin modificarlos
y agrega la API JSON en /api/... que usa js/app.js.
"""

from flask import Flask, abort, redirect, request, send_from_directory, session
from werkzeug.exceptions import HTTPException

from . import actividades, auth, inicio, instituciones, monitoreo, recursos, usuarios
from .config import CARPETA_PANEL, Config
from .db import cerrar_db
from .utilidades import ErrorDeDatos, error

# Páginas que se pueden abrir sin haber iniciado sesión
PAGINAS_PUBLICAS = {"index", "crear-usuario"}
# Endpoints de la API que no piden sesión
API_PUBLICA = {"auth.login", "usuarios.registro"}
# Páginas del front-end que no incluyen <script src="js/app.js">
PAGINAS_SIN_SCRIPT = {"crear-usuario"}


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

    @app.errorhandler(ErrorDeDatos)
    def datos_invalidos(e):
        return error(e.mensaje, e.codigo)

    @app.errorhandler(HTTPException)
    def error_http(e):
        # La API siempre responde JSON, también en errores 404 o 405
        if request.path.startswith("/api/"):
            return error(e.description, e.code)
        return e

    @app.get("/")
    def raiz():
        return redirect("/inicio.html" if "usuario_id" in session else "/index.html")

    @app.get("/<nombre>.html")
    def pagina(nombre):
        # "Cerrar sesión" en el menú lleva a index.html: abrir el login cierra la sesión
        if nombre == "index":
            session.clear()
        archivo = CARPETA_PANEL / f"{nombre}.html"
        if not archivo.is_file():
            abort(404)
        if nombre in PAGINAS_SIN_SCRIPT:
            # El HTML original no carga js/app.js: se agrega al enviarlo (el archivo no cambia)
            html = archivo.read_text(encoding="utf-8")
            return html.replace("</body>", '  <script src="js/app.js"></script>\n</body>')
        return send_from_directory(CARPETA_PANEL, f"{nombre}.html")

    @app.get("/<any(css, js, img):carpeta>/<path:archivo>")
    def estatico(carpeta, archivo):
        return send_from_directory(CARPETA_PANEL / carpeta, archivo)

    return app

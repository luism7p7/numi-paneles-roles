"""Armado común de cada panel: errores en JSON y rutas que sirven su front-end (HTML, css/, js/ e img/).

El control de sesión no está aquí porque cada panel decide qué páginas y qué rutas de la API son públicas.
"""

from flask import abort, redirect, request, send_from_directory, session
from werkzeug.exceptions import HTTPException

from .errores import ErrorDeDatos, error


def instalar_front(app, carpeta_panel, pagina_inicial):
    """Registra el manejo de errores y las rutas del front-end del panel que vive en `carpeta_panel`.

    `pagina_inicial` es la página a la que va quien ya inició sesión al abrir "/".
    """

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
        return redirect(f"/{pagina_inicial}" if "usuario_id" in session else "/index.html")

    @app.get("/<nombre>.html")
    def pagina(nombre):
        # "Cerrar sesión" en el menú lleva a index.html: abrir el login cierra la sesión
        if nombre == "index":
            session.clear()
        if not (carpeta_panel / f"{nombre}.html").is_file():
            abort(404)
        return send_from_directory(carpeta_panel, f"{nombre}.html")

    @app.get("/<any(css, js, img):subcarpeta>/<path:archivo>")
    def estatico(subcarpeta, archivo):
        return send_from_directory(carpeta_panel / subcarpeta, archivo)

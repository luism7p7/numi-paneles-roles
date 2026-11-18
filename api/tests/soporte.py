"""Ayudas de las pruebas: un cliente que se comporta como el navegador."""

CLAVE_APP = "clave-de-prueba"


class RespuestaPlana:
    """La respuesta de la API sin su envoltorio {success, message, data}, para comparar con lo que devuelve cada ruta."""

    def __init__(self, respuesta):
        self._respuesta = respuesta

    def __getattr__(self, nombre):
        return getattr(self._respuesta, nombre)

    def get_json(self, *args, **kwargs):
        cuerpo = self._respuesta.get_json(*args, **kwargs)
        if not isinstance(cuerpo, dict) or "success" not in cuerpo:
            return cuerpo  # el puente con la app no usa envoltorio
        if cuerpo["success"]:
            if cuerpo["data"] is None and "message" in cuerpo:
                return {"mensaje": cuerpo["message"]}
            return cuerpo["data"]
        error = cuerpo["error"]
        plano = {"error": error["message"]}
        detalles = error.get("details")
        if isinstance(detalles, dict) and "omitidos" in detalles:
            plano.update(detalles)
        return plano


class ClienteConSesion:
    """Hace de navegador: recuerda el token y el grupo activo, y traduce las rutas cortas `/api/...`.

    Cada panel habla con su parte de la API (`/api/v1/admin/...` o `/api/v1/docente/...`);
    el acceso (`/api/login`, `/api/registro`) y el puente con la app (`/api/app/...`) van aparte.
    """

    def __init__(self, app, prefijo, rol, cabeceras=None):
        self.application = app
        self._cliente = app.test_client()
        self._prefijo, self._rol = prefijo, rol
        self._cabeceras = dict(cabeceras or {})

    def _ruta(self, ruta):
        if ruta.startswith(("/api/app/", "/api/v1/")):
            return ruta  # ya es la ruta completa
        if ruta in ("/api/login", "/api/registro"):
            return "/api/v1/auth/" + ruta.rsplit("/", 1)[1]
        return ruta.replace("/api/", f"{self._prefijo}/", 1)

    def request(self, metodo, ruta, **kwargs):
        if ruta == "/api/login" and isinstance(kwargs.get("json"), dict):
            kwargs["json"] = {"rol": self._rol} | kwargs["json"]
        kwargs["headers"] = self._cabeceras | kwargs.get("headers", {})
        respuesta = getattr(self._cliente, metodo)(self._ruta(ruta), **kwargs)
        if respuesta.status_code == 200:
            cuerpo = respuesta.get_json(silent=True) or {}
            if ruta == "/api/login":
                self._cabeceras["Authorization"] = f"Bearer {cuerpo['data']['access_token']}"
            elif ruta == "/api/grupo-activo":
                self._cabeceras["X-Grupo-Id"] = str(cuerpo["data"]["grupo_activo"])
        return RespuestaPlana(respuesta)

    def get(self, ruta, **kwargs):
        return self.request("get", ruta, **kwargs)

    def post(self, ruta, **kwargs):
        return self.request("post", ruta, **kwargs)

    def put(self, ruta, **kwargs):
        return self.request("put", ruta, **kwargs)

    def patch(self, ruta, **kwargs):
        return self.request("patch", ruta, **kwargs)

    def delete(self, ruta, **kwargs):
        return self.request("delete", ruta, **kwargs)

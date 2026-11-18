"""Consumo del backend de la app Numi (FastAPI): lo único que esta API le pide a otro servidor.

La dirección viene de `APP_API_URL` en el .env. Sin ella, estas consultas no se hacen.
"""

import json
import urllib.request

from app.compartido.textos import version

RUTAS_SERVICIOS = {"datos": "/salud", "contenido": "/api/paquetes"}


def responde(url):
    """True si la URL contesta 200 en menos de 5 segundos."""
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


def servicio_responde(base, clave):
    """¿El servicio `clave` ('datos' o 'contenido') del backend de la app está contestando?"""
    return responde(base + RUTAS_SERVICIOS[clave])


def version_mas_reciente_de_paquetes(base):
    """Consulta GET /api/paquetes del backend de la app y devuelve la versión más reciente."""
    with urllib.request.urlopen(f"{base}/api/paquetes", timeout=8) as resp:
        paquetes = json.load(resp)["paquetes"]
    versiones = [p["version"] for p in paquetes if p.get("version")]
    return max(versiones, key=version)

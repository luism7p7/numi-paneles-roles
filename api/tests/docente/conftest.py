import pytest

from database.init_db import PASSWORD_DEMO
from soporte import CLAVE_APP, ClienteConSesion


@pytest.fixture
def client(app):
    """Navegador del panel docente, sin haber iniciado sesión."""
    return ClienteConSesion(app, "/api/v1/docente", "Docente")


@pytest.fixture
def docente(base_de_pruebas, client):
    """Navegador con la sesión de Luisa Muñoz (3° A, 4° B y 5° A de IE Rural La Aldea)."""
    resp = client.post("/api/login", json={"correo": "luisa.munoz@ielaaldea.edu.co", "password": PASSWORD_DEMO})
    assert resp.status_code == 200
    return client


@pytest.fixture
def app_numi(base_de_pruebas, app):
    """Cliente que hace de backend de la app (envía la clave X-Api-Key)."""
    return ClienteConSesion(app, "/api/v1/docente", "Docente", {"X-Api-Key": CLAVE_APP})

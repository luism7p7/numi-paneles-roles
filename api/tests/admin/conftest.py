import pytest

from database.init_db import PASSWORD_DEMO
from soporte import ClienteConSesion

ADMIN = "cvelez@medellin.gov.co"


@pytest.fixture
def client(app):
    """Navegador del panel administrativo, sin haber iniciado sesión."""
    return ClienteConSesion(app, "/api/v1/admin", "Administrador")


@pytest.fixture
def admin(base_de_pruebas, client):
    """Navegador con la sesión del administrador abierta."""
    resp = client.post("/api/login", json={"correo": ADMIN, "password": PASSWORD_DEMO})
    assert resp.status_code == 200
    return client

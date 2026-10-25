import sys
from pathlib import Path

import pymysql
import pytest

PANEL = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(PANEL), str(PANEL.parent)]

from database.init_db import PASSWORD_DEMO, crear_base  # noqa: E402
from servidor_admin import create_app  # noqa: E402

# Las pruebas usan su propia base para no tocar los datos de `numi`.
BD_PRUEBAS = "numi_test"
ADMIN = "cvelez@medellin.gov.co"


@pytest.fixture(scope="module")
def base_de_pruebas():
    """Cada archivo de pruebas empieza con la base recién creada."""
    try:
        crear_base(BD_PRUEBAS, reiniciar=True)
    except pymysql.err.OperationalError as e:
        pytest.skip(f"MySQL no disponible (revisa DB_USER y DB_PASSWORD en .env): {e}")


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "DB_NAME": BD_PRUEBAS, "APP_API_URL": "", "CARPETA_UPLOADS": tmp_path})
    return app.test_client()


@pytest.fixture
def admin(base_de_pruebas, client):
    """Cliente con la sesión del administrador abierta."""
    resp = client.post("/api/login", json={"correo": ADMIN, "password": PASSWORD_DEMO})
    assert resp.status_code == 200
    return client

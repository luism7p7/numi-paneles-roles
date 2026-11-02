import sys
from pathlib import Path

import pymysql
import pytest

PANEL = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(PANEL), str(PANEL.parent)]

from database.init_db import PASSWORD_DEMO, crear_base  # noqa: E402
from servidor_docente import create_app  # noqa: E402

# Las pruebas usan su propia base para no tocar los datos de `numi`.
BD_PRUEBAS = "numi_test"
CLAVE_APP = "clave-de-prueba"


@pytest.fixture(scope="module")
def base_de_pruebas():
    """Cada archivo de pruebas empieza con la base recién creada."""
    try:
        crear_base(BD_PRUEBAS, reiniciar=True)
    except pymysql.err.OperationalError as e:
        pytest.skip(f"MySQL no disponible (revisa DB_USER y DB_PASSWORD en .env): {e}")


@pytest.fixture
def client():
    app = create_app({"TESTING": True, "DB_NAME": BD_PRUEBAS, "APP_API_URL": "", "APP_API_KEY": CLAVE_APP})
    return app.test_client()


@pytest.fixture
def docente(base_de_pruebas, client):
    """Cliente con la sesión de Luisa Muñoz (3° A, 4° B y 5° A de IE Rural La Aldea)."""
    resp = client.post("/api/login", json={"correo": "luisa.munoz@ielaaldea.edu.co", "password": PASSWORD_DEMO})
    assert resp.status_code == 200
    return client


@pytest.fixture
def app_numi(base_de_pruebas, client):
    """Cliente que hace de backend de la app (envía la clave X-Api-Key)."""
    client.environ_base["HTTP_X_API_KEY"] = CLAVE_APP
    return client

"""Pruebas de la API. Usan su propia base de datos (`numi_test`) para no tocar los datos de `numi`."""

import sys
from pathlib import Path

import pymysql
import pytest

API = Path(__file__).resolve().parents[1]
RAIZ = API.parent
sys.path[:0] = [str(API), str(RAIZ), str(API / "tests")]

from app import crear_app  # noqa: E402
from database.init_db import crear_base  # noqa: E402
from soporte import CLAVE_APP  # noqa: E402

BD_PRUEBAS = "numi_test"


@pytest.fixture(scope="module")
def base_de_pruebas():
    """Cada archivo de pruebas empieza con la base recién creada."""
    try:
        crear_base(BD_PRUEBAS, reiniciar=True)
    except pymysql.err.OperationalError as e:
        pytest.skip(f"MySQL no disponible (revisa DB_USER y DB_PASSWORD en .env): {e}")


@pytest.fixture
def app(tmp_path):
    return crear_app({"TESTING": True, "DB_NAME": BD_PRUEBAS, "APP_API_URL": "", "APP_API_KEY": CLAVE_APP,
                      "CARPETA_UPLOADS": tmp_path})

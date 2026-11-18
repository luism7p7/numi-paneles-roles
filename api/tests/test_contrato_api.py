"""El contrato de la API: formato de las respuestas, tokens JWT, roles y grupo activo.

Aquí se habla con la API tal cual es (`/api/v1/...`), sin el cliente que traduce rutas.
"""

from datetime import UTC, datetime, timedelta

import jwt
import pytest

from database.init_db import PASSWORD_DEMO
from soporte import CLAVE_APP

ADMIN = "cvelez@medellin.gov.co"
DOCENTE = "luisa.munoz@ielaaldea.edu.co"


@pytest.fixture
def cliente(base_de_pruebas, app):
    return app.test_client()


def entrar(cliente, correo, rol):
    resp = cliente.post("/api/v1/auth/login", json={"correo": correo, "password": PASSWORD_DEMO, "rol": rol})
    assert resp.status_code == 200
    return {"Authorization": f"Bearer {resp.get_json()['data']['access_token']}"}


def test_salud_es_publica_y_usa_el_formato_estandar(cliente):
    resp = cliente.get("/api/v1/salud")
    assert resp.status_code == 200
    assert resp.get_json() == {"success": True, "data": {"servicio": "numi-api", "version": "v1"}}


def test_login_entrega_un_token_con_id_y_rol(cliente, app):
    resp = cliente.post("/api/v1/auth/login", json={"correo": ADMIN, "password": PASSWORD_DEMO, "rol": "Administrador"})
    cuerpo = resp.get_json()
    assert cuerpo["success"] is True and cuerpo["message"] == "Inicio de sesión exitoso."
    claims = jwt.decode(cuerpo["data"]["access_token"], app.config["SECRET_KEY"], algorithms=["HS256"])
    assert claims["rol"] == "Administrador" and int(claims["sub"]) > 0 and "exp" in claims
    assert cuerpo["data"]["nombre"] == "Carolina Vélez"


def test_los_errores_usan_success_false_y_un_mensaje(cliente):
    resp = cliente.post("/api/v1/auth/login", json={"correo": ADMIN, "password": "mal", "rol": "Administrador"})
    assert resp.status_code == 401
    assert resp.get_json() == {"success": False, "error": {"message": "Correo o contraseña incorrectos."}}


def test_los_errores_de_validacion_traen_el_detalle_por_campo(cliente):
    cabeceras = entrar(cliente, ADMIN, "Administrador")
    resp = cliente.post("/api/v1/admin/usuarios", headers=cabeceras, json={"rol": "Docente", "nombre": "Ana"})
    error = resp.get_json()["error"]
    assert resp.status_code == 400
    assert error["message"] == "Escribe el apellido."
    assert set(error["details"]) == {"apellido", "correo"}


def test_login_pide_el_rol(cliente):
    resp = cliente.post("/api/v1/auth/login", json={"correo": ADMIN, "password": PASSWORD_DEMO})
    assert resp.status_code == 400
    assert resp.get_json()["error"]["message"] == "Indica el rol con el que entras."


@pytest.mark.parametrize("ruta", ["/api/v1/admin/inicio", "/api/v1/docente/panel", "/api/v1/docente/me"])
def test_sin_token_responde_401(cliente, ruta):
    resp = cliente.get(ruta)
    assert resp.status_code == 401
    assert resp.get_json()["error"]["message"] == "Tu sesión terminó. Vuelve a iniciar sesión."


def test_token_falso_o_vencido_responde_401(cliente, app):
    assert cliente.get("/api/v1/admin/inicio", headers={"Authorization": "Bearer inventado"}).status_code == 401
    vencido = jwt.encode({"sub": "1", "rol": "Administrador", "exp": datetime.now(UTC) - timedelta(minutes=1)},
                         app.config["SECRET_KEY"], algorithm="HS256")
    assert cliente.get("/api/v1/admin/inicio", headers={"Authorization": f"Bearer {vencido}"}).status_code == 401
    firmado_por_otro = jwt.encode({"sub": "1", "rol": "Administrador"}, "otra-clave-de-32-caracteres-o-mas!!", algorithm="HS256")
    assert cliente.get("/api/v1/admin/inicio", headers={"Authorization": f"Bearer {firmado_por_otro}"}).status_code == 401


def test_cada_rol_solo_entra_a_su_parte(cliente):
    admin = entrar(cliente, ADMIN, "Administrador")
    docente = entrar(cliente, DOCENTE, "Docente")
    assert cliente.get("/api/v1/admin/inicio", headers=admin).status_code == 200
    assert cliente.get("/api/v1/admin/inicio", headers=docente).status_code == 403
    assert cliente.get("/api/v1/docente/panel", headers=docente).status_code == 200
    assert cliente.get("/api/v1/docente/panel", headers=admin).status_code == 403


def test_el_grupo_activo_viaja_en_la_cabecera_y_solo_vale_si_es_del_docente(cliente):
    docente = entrar(cliente, DOCENTE, "Docente")
    grupos = cliente.get("/api/v1/docente/me", headers=docente).get_json()["data"]["grupos"]
    segundo = grupos[1]["id"]

    yo = cliente.get("/api/v1/docente/me", headers=docente | {"X-Grupo-Id": str(segundo)}).get_json()["data"]
    assert yo["grupo_activo"] == segundo
    # Un grupo que no es suyo no se acepta: se usa el primero
    yo = cliente.get("/api/v1/docente/me", headers=docente | {"X-Grupo-Id": "999999"}).get_json()["data"]
    assert yo["grupo_activo"] == grupos[0]["id"]
    # Y el cambio explícito de grupo ajeno se rechaza
    resp = cliente.post("/api/v1/docente/grupo-activo", headers=docente, json={"grupo_id": 999999})
    assert resp.status_code == 403


def test_los_archivos_subidos_se_ven_sin_token(cliente, app):
    (app.config["CARPETA_UPLOADS"] / "actividades").mkdir(parents=True)
    (app.config["CARPETA_UPLOADS"] / "actividades" / "foto.png").write_bytes(b"png")
    assert cliente.get("/api/v1/archivos/actividades/foto.png").data == b"png"


def test_cors_deja_pasar_a_los_dos_frontends_y_a_nadie_mas(cliente):
    for origen in ("http://localhost:5173", "http://localhost:5174"):
        resp = cliente.options("/api/v1/salud", headers={"Origin": origen, "Access-Control-Request-Method": "GET"})
        assert resp.headers["Access-Control-Allow-Origin"] == origen
    resp = cliente.options("/api/v1/salud", headers={"Origin": "http://otro-sitio.com", "Access-Control-Request-Method": "GET"})
    assert "Access-Control-Allow-Origin" not in resp.headers


def test_el_puente_con_la_app_conserva_su_formato_sin_envoltorio(cliente):
    resp = cliente.get("/api/app/v1/actividades?uid=nadie", headers={"X-Api-Key": CLAVE_APP})
    assert resp.status_code == 404
    assert resp.get_json() == {"error": "El estudiante no se ha unido a ningún grupo."}
    assert cliente.get("/api/app/v1/actividades?uid=x").get_json() == {"error": "Clave de la app inválida."}


def test_una_ruta_que_no_existe_responde_json(cliente):
    resp = cliente.get("/api/v1/no-existe")
    assert resp.status_code == 404
    assert resp.get_json()["success"] is False

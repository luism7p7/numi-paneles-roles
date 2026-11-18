from database.init_db import PASSWORD_DEMO

# ---------- Sin base de datos ----------


def test_api_sin_sesion_responde_401(client):
    assert client.get("/api/actividades").status_code == 401


def test_login_sin_datos_responde_400(client):
    assert client.post("/api/login", json={}).status_code == 400


# ---------- Con base de datos ----------

def login(client, correo, password=PASSWORD_DEMO):
    return client.post("/api/login", json={"correo": correo, "password": password})


def test_login_administrador(base_de_pruebas, client):
    resp = login(client, "  CVelez@Medellin.gov.co ")
    assert resp.status_code == 200
    assert resp.get_json()["nombre"] == "Carolina Vélez"
    assert client.get("/api/inicio").status_code == 200  # el token ya quedó puesto


def test_password_incorrecta_y_correo_inexistente_dan_el_mismo_mensaje(base_de_pruebas, client):
    a = login(client, "cvelez@medellin.gov.co", "otra")
    b = login(client, "nadie@medellin.gov.co")
    assert a.status_code == b.status_code == 401
    assert a.get_json() == b.get_json()


def test_docente_no_entra_al_panel_administrativo(base_de_pruebas, client):
    resp = login(client, "luisa.munoz@ielaaldea.edu.co")
    assert resp.status_code == 403
    assert resp.get_json()["error"] == "Esta cuenta no tiene permisos de administrador."


def test_solicitud_de_cuenta_queda_pendiente(base_de_pruebas, client):
    datos = {"nombre": "Nueva", "apellido": "Docente", "correo": "nueva@ie.edu.co"}
    assert client.post("/api/registro", json=datos).status_code == 201
    assert client.post("/api/registro", json=datos).status_code == 409
    resp = login(client, "nueva@ie.edu.co")
    assert resp.status_code == 401  # todavía no tiene contraseña

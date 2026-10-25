from database.init_db import PASSWORD_DEMO

# ---------- Sin base de datos ----------

def test_sirve_el_front_end_sin_cambios(client):
    assert client.get("/index.html").status_code == 200
    assert client.get("/css/styles.css").status_code == 200
    assert client.get("/js/app.js").status_code == 200
    assert client.get("/img/logo-numi.png").status_code == 200


def test_crear_usuario_recibe_el_script_que_le_falta(client):
    html = client.get("/crear-usuario.html").get_data(as_text=True)
    assert html.count('<script src="js/app.js"></script>') == 1


def test_no_expone_el_codigo_python(client):
    assert client.get("/app.py").status_code == 404
    assert client.get("/servidor_admin/config.py").status_code == 404


def test_pagina_privada_sin_sesion_redirige_al_login(client):
    resp = client.get("/inicio.html")
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/index.html")


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
    assert client.get("/inicio.html").status_code == 200


def test_password_incorrecta_y_correo_inexistente_dan_el_mismo_mensaje(base_de_pruebas, client):
    a = login(client, "cvelez@medellin.gov.co", "otra")
    b = login(client, "nadie@medellin.gov.co")
    assert a.status_code == b.status_code == 401
    assert a.get_json() == b.get_json()


def test_docente_no_entra_al_panel_administrativo(base_de_pruebas, client):
    resp = login(client, "luisa.munoz@ielaaldea.edu.co")
    assert resp.status_code == 403
    assert resp.get_json()["error"] == "Esta cuenta no tiene permisos de administrador."


def test_cerrar_sesion_al_volver_al_login(admin):
    admin.get("/index.html")  # el enlace "Cerrar sesión" lleva aquí
    assert admin.get("/inicio.html").status_code == 302


def test_solicitud_de_cuenta_queda_pendiente(base_de_pruebas, client):
    datos = {"nombre": "Nueva", "apellido": "Docente", "correo": "nueva@ie.edu.co"}
    assert client.post("/api/registro", json=datos).status_code == 201
    assert client.post("/api/registro", json=datos).status_code == 409
    resp = login(client, "nueva@ie.edu.co")
    assert resp.status_code == 401  # todavía no tiene contraseña

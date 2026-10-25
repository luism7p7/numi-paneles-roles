from database.init_db import PASSWORD_DEMO


def test_sirve_el_front_end_sin_cambios(client):
    for ruta in ("/index.html", "/css/styles.css", "/js/app.js", "/img/logo-numi.png"):
        assert client.get(ruta).status_code == 200
    assert client.get("/app.py").status_code == 404


def test_sin_sesion(client):
    assert client.get("/panel.html").status_code == 302
    assert client.get("/api/panel").status_code == 401


def test_administrador_no_entra_al_panel_docente(base_de_pruebas, client):
    resp = client.post("/api/login", json={"correo": "cvelez@medellin.gov.co", "password": PASSWORD_DEMO})
    assert resp.status_code == 403


def test_docente_inactivo_no_entra(base_de_pruebas, client):
    # Jhon Quintero está Inactivo y no tiene contraseña válida para entrar
    resp = client.post("/api/login", json={"correo": "jquintero@iesanantonio.edu.co", "password": PASSWORD_DEMO})
    assert resp.status_code in (401, 403)


def test_perfil_y_grupos(docente):
    yo = docente.get("/api/me").get_json()
    assert yo["nombre_completo"] == "Prof. Luisa Muñoz"
    assert yo["documento"].endswith("4321") and "1036" not in yo["documento"]
    assert [g["corto"] for g in yo["grupos"]] == ["3° A", "4° B", "5° A"]
    assert yo["grupo_activo"] == yo["grupos"][0]["id"]
    assert yo["grupos"][0]["estudiantes"] == 24


def test_cambiar_de_grupo(docente):
    grupos = docente.get("/api/me").get_json()["grupos"]
    assert docente.post("/api/grupo-activo", json={"grupo_id": grupos[1]["id"]}).status_code == 200
    assert docente.get("/api/me").get_json()["grupo_activo"] == grupos[1]["id"]
    assert len(docente.get("/api/estudiantes").get_json()) == 21


def test_no_puede_entrar_a_un_grupo_ajeno(docente):
    propios = {g["id"] for g in docente.get("/api/me").get_json()["grupos"]}
    ajeno = next(i for i in range(1, 50) if i not in propios)
    assert docente.post("/api/grupo-activo", json={"grupo_id": ajeno}).status_code == 403

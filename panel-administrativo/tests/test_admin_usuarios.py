import io


def crear(admin, **cambios):
    datos = {"nombre": "Ana", "apellido": "Pérez", "correo": "aperez@ie.edu.co", "rol": "Docente",
             "institucion": "IE Palmitas"} | cambios
    return admin.post("/api/usuarios", json=datos)


def test_lista_con_pendientes_primero(admin):
    usuarios = admin.get("/api/usuarios").get_json()
    assert usuarios[0]["estado"] == "Pendiente"
    carolina = next(u for u in usuarios if u["correo"] == "cvelez@medellin.gov.co")
    assert carolina["institucion"] == "Todas"
    assert carolina["ultimo_acceso"].startswith("Hoy")


def test_crear_queda_pendiente_y_valida(admin):
    resp = crear(admin)
    assert resp.status_code == 201
    assert resp.get_json()["estado"] == "Pendiente"
    assert crear(admin).status_code == 409  # mismo correo
    assert crear(admin, correo="no-es-correo").status_code == 400
    assert crear(admin, correo="x@ie.edu.co", institucion="Todas").status_code == 400  # docente sin institución


def test_activar_genera_contrasena_temporal_que_sirve_para_entrar(admin, client):
    nuevo = crear(admin, correo="admin2@medellin.gov.co", rol="Administrador", institucion="Todas").get_json()
    resp = admin.patch(f"/api/usuarios/{nuevo['id']}/estado", json={"estado": "Activo"})
    temporal = resp.get_json()["password_temporal"]
    assert temporal and len(temporal) == 9

    admin.get("/index.html")  # cierra la sesión de Carolina
    assert client.post("/api/login", json={"correo": "admin2@medellin.gov.co", "password": temporal}).status_code == 200


def test_restablecer_contrasena(admin, client):
    nuevo = crear(admin, correo="olvido@medellin.gov.co", rol="Administrador", institucion="Todas").get_json()
    url = f"/api/usuarios/{nuevo['id']}/password-temporal"
    assert admin.post(url).status_code == 400  # todavía está Pendiente
    vieja = admin.patch(f"/api/usuarios/{nuevo['id']}/estado", json={"estado": "Activo"}).get_json()["password_temporal"]
    nueva = admin.post(url).get_json()["password_temporal"]
    assert nueva and nueva != vieja

    admin.get("/index.html")  # cierra la sesión de Carolina
    assert client.post("/api/login", json={"correo": "olvido@medellin.gov.co", "password": vieja}).status_code == 401
    assert client.post("/api/login", json={"correo": "olvido@medellin.gov.co", "password": nueva}).status_code == 200


def test_desactivar_impide_entrar(admin):
    luisa = next(u for u in admin.get("/api/usuarios").get_json() if u["correo"] == "luisa.munoz@ielaaldea.edu.co")
    resp = admin.patch(f"/api/usuarios/{luisa['id']}/estado", json={"estado": "Inactivo"})
    assert resp.get_json()["usuario"]["estado"] == "Inactivo"
    assert resp.get_json()["password_temporal"] is None
    admin.patch(f"/api/usuarios/{luisa['id']}/estado", json={"estado": "Activo"})


def test_no_puede_desactivarse_ni_quitarse_el_rol_a_si_mismo(admin):
    yo = next(u for u in admin.get("/api/usuarios").get_json() if u["correo"] == "cvelez@medellin.gov.co")
    assert admin.patch(f"/api/usuarios/{yo['id']}/estado", json={"estado": "Inactivo"}).status_code == 400
    datos = {"nombre": "Carolina", "apellido": "Vélez", "correo": yo["correo"], "rol": "Docente", "institucion": "IE Palmitas"}
    assert admin.put(f"/api/usuarios/{yo['id']}", json=datos).status_code == 400


def test_editar(admin):
    jhon = next(u for u in admin.get("/api/usuarios").get_json() if u["nombre"] == "Jhon")
    datos = {"nombre": "Jhon Jairo", "apellido": "Quintero", "correo": jhon["correo"], "rol": "Docente", "institucion": "IE Altavista"}
    resp = admin.put(f"/api/usuarios/{jhon['id']}", json=datos)
    assert resp.get_json()["nombre_completo"] == "Jhon Jairo Quintero"
    assert resp.get_json()["institucion"] == "IE Altavista"


def test_importar_csv_con_punto_y_coma_y_encabezado(admin):
    csv = "nombre;apellido;correo_institucional\nLuz;Mora;lmora@ie.edu.co\nMal;Correo;sin-arroba\nLuz;Mora;lmora@ie.edu.co\n"
    datos = {"rol": "Docente", "institucion": "IE Santa Elena",
             "archivo": (io.BytesIO(csv.encode("utf-8")), "docentes.csv")}
    resp = admin.post("/api/usuarios/importar", data=datos, content_type="multipart/form-data")
    resultado = resp.get_json()
    assert resultado["creados"] == 1
    assert len(resultado["omitidos"]) == 2


def test_importar_json(admin):
    contenido = b'[{"nombre": "Teo", "apellido": "Ruiz", "correo_institucional": "teo@ie.edu.co"}]'
    datos = {"rol": "Docente", "institucion": "IE Palmitas", "archivo": (io.BytesIO(contenido), "docentes.json")}
    assert admin.post("/api/usuarios/importar", data=datos, content_type="multipart/form-data").get_json()["creados"] == 1
    malo = {"rol": "Docente", "institucion": "IE Palmitas", "archivo": (io.BytesIO(b"{"), "x.json")}
    assert admin.post("/api/usuarios/importar", data=malo, content_type="multipart/form-data").status_code == 400


def test_instituciones(admin):
    lista = admin.get("/api/instituciones").get_json()
    aldea = next(i for i in lista if i["nombre"] == "IE Rural La Aldea")
    detalle = admin.get(f"/api/instituciones/{aldea['id']}").get_json()
    assert detalle["estudiantes"] == aldea["estudiantes"] == 81
    primero = detalle["grupos"][0]
    assert primero["nombre"] == "Grado 3° — grupo A" and primero["corto"] == "3° A"
    assert primero["docente"] == "Luisa Muñoz · 24 estudiantes" and primero["docente_nombre"] == "Luisa Muñoz"
    assert any(g["docente"] is None for g in detalle["grupos"])
    assert admin.get("/api/instituciones/9999").status_code == 404


def test_crear_institucion(admin):
    datos = {"nombre": "IE La Loma", "comuna": "San Cristóbal", "sedes": "2", "estado": "Activa"}
    assert admin.post("/api/instituciones", json=datos).status_code == 201
    assert admin.post("/api/instituciones", json=datos).status_code == 409
    assert admin.post("/api/instituciones", json=datos | {"nombre": "Otra", "comuna": "Marte"}).status_code == 400
    assert admin.post("/api/instituciones", json=datos | {"nombre": "Otra", "sedes": "0"}).status_code == 400


# ---------- Grupos a cargo del docente ----------

def grupos_de(admin, institucion):
    inst = next(i for i in admin.get("/api/instituciones").get_json() if i["nombre"] == institucion)
    return inst["id"], admin.get(f"/api/instituciones/{inst['id']}").get_json()["grupos"]


def test_crear_grupo_en_una_institucion(admin):
    inst_id, antes = grupos_de(admin, "IE Palmitas")
    resp = admin.post(f"/api/instituciones/{inst_id}/grupos", json={"grado": 1, "letra": "b"})
    assert resp.status_code == 201
    nuevo = resp.get_json()
    assert nuevo["corto"] == "1° B" and nuevo["docente_id"] is None
    assert len(grupos_de(admin, "IE Palmitas")[1]) == len(antes) + 1
    assert admin.post(f"/api/instituciones/{inst_id}/grupos", json={"grado": 1, "letra": "B"}).status_code == 409
    assert admin.post(f"/api/instituciones/{inst_id}/grupos", json={"grado": 6, "letra": "A"}).status_code == 400
    assert admin.post(f"/api/instituciones/{inst_id}/grupos", json={"grado": 2, "letra": "Ñ"}).status_code == 400


def test_docente_con_varios_grupos(admin):
    _, grupos = grupos_de(admin, "IE Palmitas")
    ids = [g["id"] for g in grupos[:2]]
    resp = crear(admin, correo="varios@ie.edu.co", grupos=ids)
    assert resp.status_code == 201
    docente = resp.get_json()
    assert sorted(g["id"] for g in docente["grupos"]) == sorted(ids)

    # Editar: queda solo con uno
    datos = {"nombre": "Ana", "apellido": "Pérez", "correo": "varios@ie.edu.co", "rol": "Docente",
             "institucion": "IE Palmitas", "grupos": ids[:1]}
    assert [g["id"] for g in admin.put(f"/api/usuarios/{docente['id']}", json=datos).get_json()["grupos"]] == ids[:1]
    _, grupos = grupos_de(admin, "IE Palmitas")
    assert next(g for g in grupos if g["id"] == ids[1])["docente_id"] is None  # el otro grupo quedó libre


def test_no_acepta_grupos_de_otra_institucion(admin):
    _, ajenos = grupos_de(admin, "IE Santa Elena")
    assert crear(admin, correo="ajeno@ie.edu.co", grupos=[ajenos[0]["id"]]).status_code == 400


def test_administrador_no_tiene_grupos(admin):
    _, grupos = grupos_de(admin, "IE Palmitas")
    resp = crear(admin, correo="admin3@medellin.gov.co", rol="Administrador", institucion="Todas", grupos=[grupos[0]["id"]])
    assert resp.status_code == 201 and resp.get_json()["grupos"] == []

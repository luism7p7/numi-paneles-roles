def ids_recursos(admin, *nombres):
    recursos = admin.get("/api/recursos").get_json()["recursos"]
    return [r["id"] for r in recursos if r["nombre"] in nombres]


def nueva(**cambios):
    datos = {"nombre": "El ciclo del agua", "materia": "Ciencias naturales", "grado": "Grado 2°",
             "tipo": "Arrastrar", "estado": "Publicada", "recursos": []}
    return datos | cambios


def test_lista_y_detalle(admin):
    lista = admin.get("/api/actividades").get_json()
    assert any(a["id"] == "los-numeros" and a["materia"] == "Matemáticas" for a in lista)
    detalle = admin.get("/api/actividades/los-numeros").get_json()
    assert detalle["grado"] == "1°"
    assert {r["nombre"] for r in detalle["recursos"]} == {"manzana.png", "globo.png", "contar.mp3"}
    assert admin.get("/api/actividades/no-existe").status_code == 404


def test_veces_resuelta_sale_del_progreso_de_la_app(admin):
    detalle = admin.get("/api/actividades/los-numeros").get_json()
    assert int(detalle["resuelta"]) > 0
    borrador = admin.get("/api/actividades/los-colores").get_json()
    assert borrador["estado"] == "Borrador"
    assert borrador["resuelta"] == "Sin uso registrado"


def test_publicar_actividad_nueva(admin):
    resp = admin.post("/api/actividades", json=nueva(recursos=ids_recursos(admin, "perro.png", "piedra.png")))
    assert resp.status_code == 201
    assert resp.get_json()["id"] == "el-ciclo-del-agua"
    detalle = admin.get("/api/actividades/el-ciclo-del-agua").get_json()
    assert detalle["estado"] == "Publicada"
    assert len(detalle["recursos"]) == 2
    historial = admin.get("/api/historial").get_json()
    assert historial[0]["actividad"] == "El ciclo del agua" and historial[0]["tipo"] == "Publicada"


def test_no_permite_nombres_repetidos(admin):
    resp = admin.post("/api/actividades", json=nueva(nombre="los numeros"))  # sin tilde ni mayúscula
    assert resp.status_code == 409
    # El nombre que trae el formulario del constructor ya existe en la app
    assert admin.post("/api/actividades", json=nueva(nombre="¿Vivo o no vivo?")).status_code == 409


def test_no_permite_recursos_incompatibles(admin):
    resp = admin.post("/api/actividades", json=nueva(nombre="Ballenas", recursos=ids_recursos(admin, "ballena.png")))
    assert resp.status_code == 400
    assert "ballena.png" in resp.get_json()["error"]


def test_validaciones(admin):
    assert admin.post("/api/actividades", json=nueva(nombre="")).status_code == 400
    assert admin.post("/api/actividades", json=nueva(nombre="X", materia="Química")).status_code == 400
    assert admin.post("/api/actividades", json=nueva(nombre="X", grado="Grado 9°")).status_code == 400
    assert admin.post("/api/actividades", json=nueva(nombre="X", tipo="Otro")).status_code == 400


def test_borrador_y_luego_publicar(admin):
    resp = admin.post("/api/actividades", json=nueva(nombre="Las formas", estado="Borrador"))
    slug = resp.get_json()["id"]
    assert admin.get(f"/api/actividades/{slug}").get_json()["estado"] == "Borrador"
    resp = admin.put(f"/api/actividades/{slug}", json=nueva(nombre="Las formas"))
    assert resp.get_json()["antes"] == "Borrador"
    assert admin.get(f"/api/actividades/{slug}").get_json()["estado"] == "Publicada"


def test_editar_registra_cada_cambio_en_el_historial(admin):
    actual = ids_recursos(admin, "manzana.png", "globo.png", "contar.mp3")
    sin_globo = [i for i in actual if i not in ids_recursos(admin, "globo.png")] + ids_recursos(admin, "banano.png")
    datos = nueva(nombre="Los números", materia="Matemáticas", grado="Grado 1°", tipo="Arrastrar y soltar", recursos=sin_globo)
    assert admin.put("/api/actividades/los-numeros", json=datos).status_code == 200
    cambios = {h["cambio"] for h in admin.get("/api/historial").get_json() if h["actividad"] == "Los números"}
    assert {"globo.png retirado", "banano.png agregado"} <= cambios


def test_eliminar(admin):
    resp = admin.delete("/api/actividades/module-1")
    assert resp.get_json()["nombre"] == "Module 1"
    assert admin.get("/api/actividades/module-1").status_code == 404
    assert all(a["id"] != "module-1" for a in admin.get("/api/actividades").get_json())
    assert admin.get("/api/historial").get_json()[0]["tipo"] == "Eliminada"

def ids_recursos(admin, *nombres):
    recursos = admin.get("/api/recursos").get_json()["recursos"]
    return [r["id"] for r in recursos if r["nombre"] in nombres]


def pregunta(enunciado="¿Cuál es una fruta?", opciones=None, audio=None):
    return {"enunciado": enunciado, "audio": audio, "opciones": opciones or [
        {"texto": "Manzana", "imagen": None, "correcta": True},
        {"texto": "Silla", "imagen": None, "correcta": False},
    ]}


def nueva(**cambios):
    """Actividad creada en el panel con la plantilla Selección múltiple (la que la app sabe jugar)."""
    datos = {"nombre": "El ciclo del agua", "materia": "Ciencias naturales", "grado": "Grado 2°",
             "tipo": "Selección múltiple", "estado": "Publicada", "recursos": [],
             "contenido": {"preguntas": [pregunta()]}}
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


# ---------- Plantilla Selección múltiple ----------

def test_detalle_devuelve_contenido_y_si_esta_en_la_app(admin):
    slug = admin.post("/api/actividades", json=nueva(nombre="Frutas")).get_json()["id"]
    detalle = admin.get(f"/api/actividades/{slug}").get_json()
    assert detalle["en_app"] is False
    assert detalle["contenido"]["preguntas"][0]["opciones"][0] == {"texto": "Manzana", "imagen": None, "correcta": True}
    assert admin.get("/api/actividades/los-numeros").get_json()["en_app"] is True


def test_tipo_sin_plantilla_solo_como_borrador(admin):
    resp = admin.post("/api/actividades", json=nueva(nombre="Parejas nuevas", tipo="Memory match"))
    assert resp.status_code == 400
    assert "borrador" in resp.get_json()["error"].lower()
    borrador = admin.post("/api/actividades", json=nueva(nombre="Parejas nuevas", tipo="Memory match", estado="Borrador"))
    assert borrador.status_code == 201


def test_contenido_incompleto_no_se_publica(admin):
    sin_correcta = pregunta(opciones=[{"texto": "A", "correcta": False}, {"texto": "B", "correcta": False}])
    dos_correctas = pregunta(opciones=[{"texto": "A", "correcta": True}, {"texto": "B", "correcta": True}])
    una_opcion = pregunta(opciones=[{"texto": "A", "correcta": True}])
    opcion_vacia = pregunta(opciones=[{"texto": "A", "correcta": True}, {"texto": "", "correcta": False}])
    for malas in ([], [sin_correcta], [dos_correctas], [una_opcion], [opcion_vacia], [pregunta(enunciado="")]):
        resp = admin.post("/api/actividades", json=nueva(nombre="Incompleta", contenido={"preguntas": malas}))
        assert resp.status_code == 400, malas
    # Como borrador sí se puede guardar a medias
    resp = admin.post("/api/actividades", json=nueva(nombre="Incompleta", estado="Borrador", contenido={"preguntas": [una_opcion]}))
    assert resp.status_code == 201


def test_contenido_valida_tipo_de_recurso_y_los_vincula(admin):
    imagen, = ids_recursos(admin, "manzana.png")
    audio, = ids_recursos(admin, "contar.mp3")
    con_imagen = pregunta(audio=audio, opciones=[{"texto": "", "imagen": imagen, "correcta": True},
                                                 {"texto": "Silla", "correcta": False}])
    slug = admin.post("/api/actividades", json=nueva(nombre="Con imagen", contenido={"preguntas": [con_imagen]})).get_json()["id"]
    assert {r["nombre"] for r in admin.get(f"/api/actividades/{slug}").get_json()["recursos"]} == {"manzana.png", "contar.mp3"}

    al_reves = pregunta(audio=imagen)  # una imagen donde va un audio
    assert admin.post("/api/actividades", json=nueva(nombre="Al revés", contenido={"preguntas": [al_reves]})).status_code == 400


def test_editar_contenido_queda_en_el_historial(admin):
    slug = admin.post("/api/actividades", json=nueva(nombre="Colores")).get_json()["id"]
    otra = pregunta(enunciado="¿De qué color es el cielo?")
    admin.put(f"/api/actividades/{slug}", json=nueva(nombre="Colores", contenido={"preguntas": [pregunta(), otra]}))
    assert admin.get("/api/historial").get_json()[0]["cambio"] == "Contenido actualizado"
    assert len(admin.get(f"/api/actividades/{slug}").get_json()["contenido"]["preguntas"]) == 2

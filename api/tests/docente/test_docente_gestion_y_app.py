from app.integraciones import backend_app


def test_gestion(docente):
    datos = docente.get("/api/gestion").get_json()
    assert datos["codigo"] == "7K4M-92"
    assert datos["usos"] == "6 de 30 usos disponibles"
    assert datos["vence"].startswith("Vence el")
    assert datos["ia"] is True and datos["ia_disponible"] is True


def test_nuevo_codigo(docente):
    nuevo = docente.post("/api/gestion/codigo").get_json()
    assert nuevo["codigo"] != "7K4M-92"
    assert nuevo["usos"] == "30 de 30 usos disponibles"
    assert docente.get("/api/me").get_json()["grupos"][0]["codigo"] == nuevo["codigo"]


def test_asistente_ia(docente):
    assert docente.patch("/api/gestion/ia", json={"activada": False}).get_json()["ia"] is False
    assert docente.patch("/api/gestion/ia", json={"activada": True}).get_json()["ia"] is True
    assert docente.patch("/api/gestion/ia", json={"activada": "no"}).status_code == 400


def test_paquete_sin_backend_configurado(docente):
    assert docente.post("/api/gestion/paquete").status_code == 503


def test_paquete_consulta_el_backend_de_la_app(docente, monkeypatch):
    docente.application.config["APP_API_URL"] = "http://backend-de-prueba"
    monkeypatch.setattr(backend_app, "version_mas_reciente_de_paquetes", lambda base: "2.3.0")
    datos = docente.post("/api/gestion/paquete").get_json()
    assert datos["paquete"] == "v2.3.0 · 340 MB · actualizado hoy"


def test_paquete_con_backend_caido(docente, monkeypatch):
    docente.application.config["APP_API_URL"] = "http://backend-de-prueba"

    def falla(base):
        raise OSError("sin conexión")

    monkeypatch.setattr(backend_app, "version_mas_reciente_de_paquetes", falla)
    assert docente.post("/api/gestion/paquete").status_code == 502


# ---------- Puente con la app (lo llama el backend de la app) ----------

def test_puente_exige_clave(base_de_pruebas, client):
    assert client.get("/api/app/v1/actividades?uid=x").status_code == 401
    assert client.get("/api/app/v1/actividades?uid=x", headers={"X-Api-Key": "otra"}).status_code == 401


def test_unirse_con_el_codigo_del_grupo(app_numi):
    codigo = "R5Q7-13"  # 5° A
    resp = app_numi.post("/api/app/v1/unirse", json={"uid": "firebase-abc", "nombre": "Ana", "codigo": codigo.lower()})
    assert resp.status_code == 200
    assert resp.get_json()["grupo"] == {"grado": 5, "letra": "A", "institucion": "IE Rural La Aldea", "ia_activada": True}
    # Volver a unirse al mismo grupo no gasta otro uso
    app_numi.post("/api/app/v1/unirse", json={"uid": "firebase-abc", "nombre": "Ana María", "codigo": codigo})
    assert app_numi.post("/api/app/v1/unirse", json={"uid": "x", "codigo": "NO-EXISTE"}).status_code == 404


def test_actividades_para_el_celular(app_numi):
    datos = app_numi.get("/api/app/v1/actividades?uid=firebase-abc").get_json()
    assert datos["grado"] == 5
    nombres = {a["nombre"] for a in datos["actividades"]}
    assert len(nombres) == 16
    assert "Héroes de la Ciudad" in nombres and "Los colores" not in nombres
    assert app_numi.get("/api/app/v1/actividades?uid=desconocido").status_code == 404


def test_la_actividad_desactivada_llega_marcada_para_que_la_app_la_oculte(docente, app_numi):
    """La app oculta lo que el docente desactiva: el panel debe avisarle cuál, con `activa: false`."""
    codigo = docente.get("/api/gestion").get_json()["codigo"]  # el vigente de 3° A (otra prueba pudo renovarlo)
    unido = app_numi.post("/api/app/v1/unirse", json={"uid": "nino-oculta", "nombre": "Ana", "codigo": codigo})
    assert unido.status_code == 200, unido.get_json()

    def actividades():
        return {a["id"]: a for a in app_numi.get("/api/app/v1/actividades?uid=nino-oculta").get_json()["actividades"]}

    antes = actividades()
    assert antes["los-numeros"]["activa"] is True and antes["los-numeros"]["recursos"] is not None

    assert docente.patch("/api/actividades/los-numeros", json={"activa": False}).status_code == 200
    despues = actividades()
    assert despues["los-numeros"]["activa"] is False  # sigue en la lista, marcada
    assert despues["los-numeros"]["contenido"] is None and despues["los-numeros"]["recursos"] == []
    assert despues["los-numeros"]["en_app"] is True  # la app necesita saberlo para restarla del avance
    assert set(despues) == set(antes)  # no desaparece ninguna otra

    assert docente.patch("/api/actividades/los-numeros", json={"activa": True}).status_code == 200
    assert actividades()["los-numeros"]["activa"] is True


def test_subir_progreso_gana_el_mayor_avance(app_numi):
    def subir(porcentaje, intentos):
        return app_numi.put("/api/app/v1/progreso", json={
            "uid": "firebase-abc", "version_app": "1.4.0", "racha_dias": 3,
            "items": [{"grado": 5, "materia": "espanol", "actividad": "Oraciones", "porcentaje": porcentaje,
                       "intentos": intentos, "ultima_vez": "2026-10-20T15:00:00Z"},
                      {"grado": 9, "materia": "ingles", "actividad": "Parejas", "porcentaje": 50}]}).get_json()

    assert subir(80, 2) == {"guardados": 1, "rechazados": 1}
    subir(40, 5)  # un avance menor no pisa el anterior
    from app.compartido.base_datos import consultar
    with app_numi.application.app_context():
        fila = consultar("""SELECT p.porcentaje, p.intentos FROM progreso p JOIN estudiantes e ON e.id = p.estudiante_id
                            WHERE e.uid = 'firebase-abc'""", uno=True)
        assert (float(fila["porcentaje"]), fila["intentos"]) == (80.0, 5)


def test_codigo_sin_usos(app_numi):
    from app.compartido.base_datos import ejecutar
    with app_numi.application.app_context():
        ejecutar("UPDATE grupos SET codigo_usos = codigo_usos_max WHERE codigo = 'P8T2-46'")
    resp = app_numi.post("/api/app/v1/unirse", json={"uid": "otro-niño", "codigo": "P8T2-46"})
    assert resp.status_code == 409


def test_codigo_vencido(app_numi):
    from app.compartido.base_datos import ejecutar
    with app_numi.application.app_context():
        ejecutar("UPDATE grupos SET codigo_vence = '2026-01-01' WHERE codigo = 'B7C5-64'")
    assert app_numi.post("/api/app/v1/unirse", json={"uid": "n2", "codigo": "B7C5-64"}).status_code == 410


def test_actividad_de_plantilla_llega_con_contenido_y_archivos(app_numi, tmp_path):
    """Lo que necesita la app para jugar una actividad creada en el panel."""
    from app.compartido.base_datos import consultar, ejecutar

    app_numi.application.config["CARPETA_UPLOADS"] = tmp_path
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "banano.png").write_bytes(b"\x89PNG-banano")
    with app_numi.application.app_context():
        recurso_id = ejecutar("INSERT INTO recursos (nombre, tipo, carpeta, archivo) VALUES ('banano.png', 'Imagen', 'actividades/ciencias', 'app/banano.png')")
        contenido = ('{"preguntas": [{"enunciado": "¿Cuál es una fruta?", "audio": null, "opciones": ['
                     f'{{"texto": "Banano", "imagen": {recurso_id}, "correcta": true}}, '
                     '{"texto": "Silla", "imagen": null, "correcta": false}]}]}')
        grupo = consultar("SELECT codigo, grado FROM grupos WHERE codigo_vence >= CURDATE() AND codigo_usos < codigo_usos_max LIMIT 1", uno=True)
        codigo = grupo["codigo"]
        actividad_id = ejecutar("""INSERT INTO actividades (slug, nombre, materia, grado, tipo, estado, en_app, contenido)
                                   VALUES ('toca-las-frutas', 'toca las frutas', 'ciencias', %s, 'Selección múltiple', 'Publicada', FALSE, %s)""",
                                (grupo["grado"], contenido))
        ejecutar("INSERT INTO actividad_recurso VALUES (%s, %s)", (actividad_id, recurso_id))

    app_numi.post("/api/app/v1/unirse", json={"uid": "nino-plantilla", "codigo": codigo})
    datos = app_numi.get("/api/app/v1/actividades?uid=nino-plantilla").get_json()
    frutas = next(a for a in datos["actividades"] if a["id"] == "toca-las-frutas")
    assert frutas["en_app"] is False and frutas["tipo"] == "Selección múltiple"
    assert frutas["contenido"]["preguntas"][0]["opciones"][0]["imagen"] == recurso_id
    assert frutas["recursos"] == [{"id": recurso_id, "nombre": "banano.png", "tipo": "Imagen",
                                   "version_minima": None, "descargable": True}]
    assert frutas["actualizada"]
    numeros = next(a for a in datos["actividades"] if a["id"] == "los-numeros")
    assert numeros["en_app"] is True and numeros["contenido"] is None

    archivo = app_numi.get(f"/api/app/v1/recursos/{recurso_id}")
    assert archivo.status_code == 200 and archivo.data == b"\x89PNG-banano"
    assert app_numi.get("/api/app/v1/recursos/999999").status_code == 404


def test_todas_las_plantillas_llegan_a_la_app_con_su_contenido(app_numi):
    """Cada tipo con plantilla viaja con su propio formato de contenido (ver app/dominios/actividades/plantillas.py)."""
    import json

    from app.compartido.base_datos import consultar, ejecutar

    contenidos = {
        "Arrastrar": {"grupos": [{"nombre": "Vivo", "imagen": None}, {"nombre": "No vivo", "imagen": None}],
                      "elementos": [{"texto": "Perro", "imagen": None, "grupo": 0}, {"texto": "Piedra", "imagen": None, "grupo": 1}]},
        "Arrastrar y soltar": {"parejas": [{"elemento": {"texto": "3", "imagen": None}, "destino": {"texto": "tres", "imagen": None}},
                                           {"elemento": {"texto": "1", "imagen": None}, "destino": {"texto": "uno", "imagen": None}}]},
        "Ordenar sílabas": {"palabras": [{"silabas": ["ga", "to"], "imagen": None, "audio": None}]},
        "Memory match": {"pares": [{"texto": "Dog", "imagen": None}, {"texto": "Cat", "imagen": None}]},
        "Comprensión auditiva": {"preguntas": [{"enunciado": "¿Qué escuchaste?", "audio": None, "opciones": [
            {"texto": "Perro", "imagen": None, "correcta": True}, {"texto": "Gato", "imagen": None, "correcta": False}]}]},
    }
    with app_numi.application.app_context():
        grupo = consultar("SELECT codigo, grado FROM grupos WHERE codigo_vence >= CURDATE() AND codigo_usos < codigo_usos_max LIMIT 1", uno=True)
        codigo = grupo["codigo"]
        for n, (tipo, contenido) in enumerate(contenidos.items()):
            ejecutar("""INSERT INTO actividades (slug, nombre, materia, grado, tipo, estado, en_app, contenido)
                        VALUES (%s, %s, 'ciencias', %s, %s, 'Publicada', FALSE, %s)""",
                     (f"plantilla-{n}", f"Plantilla {n}", grupo["grado"], tipo, json.dumps(contenido, ensure_ascii=False)))

    app_numi.post("/api/app/v1/unirse", json={"uid": "nino-todas", "codigo": codigo})
    datos = app_numi.get("/api/app/v1/actividades?uid=nino-todas").get_json()
    recibidas = {a["tipo"]: a["contenido"] for a in datos["actividades"] if a["id"].startswith("plantilla-")}
    assert recibidas == contenidos


def test_actividad_del_panel_solo_llega_a_los_grupos_de_su_grado(app_numi):
    """El grado que elige el administrador filtra; las pantallas que ya trae la app valen para todos."""
    import json

    from app.compartido.base_datos import consultar, ejecutar

    contenido = json.dumps({"pares": [{"texto": "Dog", "imagen": None}, {"texto": "Cat", "imagen": None}]})
    with app_numi.application.app_context():
        grupo = consultar("SELECT codigo, grado FROM grupos WHERE codigo_vence >= CURDATE() AND codigo_usos < codigo_usos_max LIMIT 1", uno=True)
        otro_grado = 1 if grupo["grado"] != 1 else 2
        for slug, grado in (("memory-del-grado", grupo["grado"]), ("memory-de-otro-grado", otro_grado)):
            ejecutar("""INSERT INTO actividades (slug, nombre, materia, grado, tipo, estado, en_app, contenido)
                        VALUES (%s, %s, 'ingles', %s, 'Memory match', 'Publicada', FALSE, %s)""",
                     (slug, slug, grado, contenido))
        # Un borrador del mismo grado tampoco llega
        ejecutar("""INSERT INTO actividades (slug, nombre, materia, grado, tipo, estado, en_app, contenido)
                    VALUES ('memory-borrador', 'memory-borrador', 'ingles', %s, 'Memory match', 'Borrador', FALSE, %s)""",
                 (grupo["grado"], contenido))

    app_numi.post("/api/app/v1/unirse", json={"uid": "nino-grado", "codigo": grupo["codigo"]})
    ids = {a["id"] for a in app_numi.get("/api/app/v1/actividades?uid=nino-grado").get_json()["actividades"]}
    assert "memory-del-grado" in ids
    assert "memory-de-otro-grado" not in ids and "memory-borrador" not in ids
    assert "los-numeros" in ids  # pantalla propia de la app: la misma para todos los grados


def test_el_docente_solo_ve_las_actividades_del_panel_de_su_grado(docente):
    """Luisa tiene 3° A, 4° B y 5° A: una actividad de 4° aparece solo en 4° B y se puede activar solo ahí."""
    import json

    from app.compartido.base_datos import ejecutar

    contenido = json.dumps({"pares": [{"texto": "Dog", "imagen": None}, {"texto": "Cat", "imagen": None}]})
    with docente.application.app_context():
        ejecutar("""INSERT INTO actividades (slug, nombre, materia, grado, tipo, estado, en_app, contenido)
                    VALUES ('memory-de-cuarto', 'Memory de cuarto', 'ingles', 4, 'Memory match', 'Publicada', FALSE, %s)""",
                 (contenido,))
    grupos = {g["corto"]: g["id"] for g in docente.get("/api/me").get_json()["grupos"]}

    def ids_en(grupo):
        docente.post("/api/grupo-activo", json={"grupo_id": grupos[grupo]})
        return [a["id"] for a in docente.get("/api/actividades").get_json()]

    assert "memory-de-cuarto" not in ids_en("3° A")
    assert docente.patch("/api/actividades/memory-de-cuarto", json={"activa": False}).status_code == 404
    assert "memory-de-cuarto" in ids_en("4° B")
    assert docente.patch("/api/actividades/memory-de-cuarto", json={"activa": False}).status_code == 200
    assert "memory-de-cuarto" not in ids_en("5° A")


def test_recursos_exigen_la_clave(base_de_pruebas, client):
    assert client.get("/api/app/v1/recursos/1").status_code == 401

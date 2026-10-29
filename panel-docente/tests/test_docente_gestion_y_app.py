from servidor_docente import gestion


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
    monkeypatch.setattr(gestion, "version_de_paquetes", lambda base: "2.3.0")
    datos = docente.post("/api/gestion/paquete").get_json()
    assert datos["paquete"] == "v2.3.0 · 340 MB · actualizado hoy"


def test_paquete_con_backend_caido(docente, monkeypatch):
    docente.application.config["APP_API_URL"] = "http://backend-de-prueba"

    def falla(base):
        raise OSError("sin conexión")

    monkeypatch.setattr(gestion, "version_de_paquetes", falla)
    assert docente.post("/api/gestion/paquete").status_code == 502


# ---------- Puente con la app (lo llama el backend de la app) ----------

def test_puente_exige_clave(base_de_pruebas, client):
    assert client.get("/api/app/v1/actividades?uid=x").status_code == 401
    client.environ_base["HTTP_X_API_KEY"] = "otra"
    assert client.get("/api/app/v1/actividades?uid=x").status_code == 401


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


def test_subir_progreso_gana_el_mayor_avance(app_numi):
    def subir(porcentaje, intentos):
        return app_numi.put("/api/app/v1/progreso", json={
            "uid": "firebase-abc", "version_app": "1.4.0", "racha_dias": 3,
            "items": [{"grado": 5, "materia": "espanol", "actividad": "Oraciones", "porcentaje": porcentaje,
                       "intentos": intentos, "ultima_vez": "2026-10-20T15:00:00Z"},
                      {"grado": 9, "materia": "ingles", "actividad": "Parejas", "porcentaje": 50}]}).get_json()

    assert subir(80, 2) == {"guardados": 1, "rechazados": 1}
    subir(40, 5)  # un avance menor no pisa el anterior
    from servidor_docente.db import consultar
    with app_numi.application.app_context():
        fila = consultar("""SELECT p.porcentaje, p.intentos FROM progreso p JOIN estudiantes e ON e.id = p.estudiante_id
                            WHERE e.uid = 'firebase-abc'""", uno=True)
        assert (float(fila["porcentaje"]), fila["intentos"]) == (80.0, 5)


def test_codigo_sin_usos(app_numi):
    from servidor_docente.db import ejecutar
    with app_numi.application.app_context():
        ejecutar("UPDATE grupos SET codigo_usos = codigo_usos_max WHERE codigo = 'P8T2-46'")
    resp = app_numi.post("/api/app/v1/unirse", json={"uid": "otro-niño", "codigo": "P8T2-46"})
    assert resp.status_code == 409


def test_codigo_vencido(app_numi):
    from servidor_docente.db import ejecutar
    with app_numi.application.app_context():
        ejecutar("UPDATE grupos SET codigo_vence = '2026-01-01' WHERE codigo = 'B7C5-64'")
    assert app_numi.post("/api/app/v1/unirse", json={"uid": "n2", "codigo": "B7C5-64"}).status_code == 410


def test_actividad_de_plantilla_llega_con_contenido_y_archivos(app_numi, tmp_path):
    """Lo que necesita la app para jugar una actividad creada en el panel."""
    from servidor_docente.db import consultar, ejecutar

    app_numi.application.config["CARPETA_UPLOADS"] = tmp_path
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "banano.png").write_bytes(b"\x89PNG-banano")
    with app_numi.application.app_context():
        recurso_id = ejecutar("INSERT INTO recursos (nombre, tipo, carpeta, archivo) VALUES ('banano.png', 'Imagen', 'actividades/ciencias', 'app/banano.png')")
        contenido = ('{"preguntas": [{"enunciado": "¿Cuál es una fruta?", "audio": null, "opciones": ['
                     f'{{"texto": "Banano", "imagen": {recurso_id}, "correcta": true}}, '
                     '{"texto": "Silla", "imagen": null, "correcta": false}]}]}')
        actividad_id = ejecutar("""INSERT INTO actividades (slug, nombre, materia, grado, tipo, estado, en_app, contenido)
                                   VALUES ('toca-las-frutas', 'toca las frutas', 'ciencias', 2, 'Selección múltiple', 'Publicada', FALSE, %s)""",
                                (contenido,))
        ejecutar("INSERT INTO actividad_recurso VALUES (%s, %s)", (actividad_id, recurso_id))
        codigo = consultar("SELECT codigo FROM grupos WHERE codigo_vence >= CURDATE() AND codigo_usos < codigo_usos_max LIMIT 1", uno=True)["codigo"]

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


def test_recursos_exigen_la_clave(base_de_pruebas, client):
    assert client.get("/api/app/v1/recursos/1").status_code == 401

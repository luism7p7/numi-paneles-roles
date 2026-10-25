import io

from servidor_admin import monitoreo


def test_inicio(admin):
    datos = admin.get("/api/inicio").get_json()
    assert datos["totales"]["instituciones"] == 7
    assert datos["totales"]["pendientes"] == 4
    assert datos["cobertura"][0]["comuna"] == "San Cristóbal"
    assert datos["servicios_caidos"] == []  # sin APP_API_URL no se revisa nada


def test_monitoreo_sin_configurar(admin):
    datos = admin.get("/api/monitoreo").get_json()
    assert [s["operativo"] for s in datos["servicios"]] == [None, None]
    assert datos["equipos"] == sum(v["equipos"] for v in datos["versiones"])
    assert datos["desactualizados"]["version"] == "1.1.0"


def test_servicio_caido_crea_evento_y_aparece_en_inicio(admin, monkeypatch):
    admin.application.config["APP_API_URL"] = "http://backend-de-prueba"
    monkeypatch.setattr(monitoreo, "responde", lambda url: not url.endswith("/api/paquetes"))
    datos = admin.get("/api/monitoreo").get_json()
    assert [s["operativo"] for s in datos["servicios"]] == [True, False]
    assert datos["eventos"][0] == {"nivel": "Crítico", "mensaje": "RAG API sin respuesta", "fecha": datos["eventos"][0]["fecha"]}
    caidos = admin.get("/api/inicio").get_json()["servicios_caidos"]
    assert [s["clave"] for s in caidos] == ["contenido"]


def test_generar_y_descargar_informe(admin):
    resp = admin.post("/api/informes")
    assert resp.status_code == 201
    informe = admin.get("/api/monitoreo").get_json()["informes"][0]
    assert informe["titulo"].startswith("Sincronización")
    archivo = admin.get(f"/api/informes/{informe['id']}/descargar")
    assert archivo.mimetype == "text/csv"
    assert "attachment" in archivo.headers["Content-Disposition"]
    assert archivo.data.decode("utf-8-sig").startswith("institucion,grupo,estudiante")


def test_recursos_y_compatibilidad(admin):
    datos = admin.get("/api/recursos").get_json()
    ballena = next(r for r in datos["recursos"] if r["nombre"] == "ballena.png")
    assert ballena["compatible"] is False and ballena["equipos_incompatibles"] > 0
    assert datos["equipos_desactualizados"] > 0


def test_subir_recursos(admin):
    datos = {
        "carpeta": "actividades/ciencias",
        "archivos": [(io.BytesIO(b"\x89PNG..."), "Gato Feliz.PNG"), (io.BytesIO(b"MZ"), "virus.exe")],
    }
    resp = admin.post("/api/recursos", data=datos, content_type="multipart/form-data")
    assert resp.status_code == 201
    assert resp.get_json()["subidos"] == ["gato_feliz.png"]
    assert "virus.exe" in resp.get_json()["omitidos"][0]
    assert admin.get("/uploads/actividades/ciencias/gato_feliz.png").status_code == 200
    # repetido
    otra = {"carpeta": "actividades/ciencias", "archivos": [(io.BytesIO(b"x"), "gato_feliz.png")]}
    assert admin.post("/api/recursos", data=otra, content_type="multipart/form-data").status_code == 400
    mala = {"carpeta": "../../etc", "archivos": [(io.BytesIO(b"x"), "a.png")]}
    assert admin.post("/api/recursos", data=mala, content_type="multipart/form-data").status_code == 400

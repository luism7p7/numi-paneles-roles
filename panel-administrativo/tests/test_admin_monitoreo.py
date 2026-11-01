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
    # Cada servicio dice qué es, y sin APP_API_URL explica por qué no se sabe su estado
    assert [s["nombre"] for s in datos["servicios"]] == ["Servidor de la app", "Contenido e IA (RAG)"]
    assert all(s["descripcion"] and "APP_API_URL" in s["detalle"] for s in datos["servicios"])
    assert datos["dias_sin_sincronizar"] == 7 and datos["equipos_registrados"] >= datos["sin_sincronizar"]


def test_servicio_caido_crea_evento_y_aparece_en_inicio(admin, monkeypatch):
    admin.application.config["APP_API_URL"] = "http://backend-de-prueba:8000"
    monkeypatch.setattr(monitoreo, "responde", lambda url: (not url.endswith("/api/paquetes"), "No se pudo conectar"))
    datos = admin.get("/api/monitoreo").get_json()
    assert [s["operativo"] for s in datos["servicios"]] == [True, False]
    assert datos["eventos"][0] == {"nivel": "Crítico", "mensaje": "Contenido e IA (RAG) sin respuesta", "fecha": datos["eventos"][0]["fecha"]}
    caido = datos["servicios"][1]
    assert caido["detalle"] == "No se pudo conectar" and caido["desde_texto"] and caido["direccion"] == "backend-de-prueba:8000"
    caidos = admin.get("/api/inicio").get_json()["servicios_caidos"]
    assert [s["clave"] for s in caidos] == ["contenido"]


def test_volver_a_comprobar_no_espera_un_minuto(admin, monkeypatch):
    admin.application.config["APP_API_URL"] = "http://backend-de-prueba:8000"
    respuestas = iter([(False, "No contestó en 5 segundos")] * 2 + [(True, "Respondió correctamente")] * 2)
    monkeypatch.setattr(monitoreo, "responde", lambda url: next(respuestas))
    admin.get("/api/monitoreo?forzar=1")
    # Sin forzar, la revisión de hace un instante se reutiliza
    assert [s["operativo"] for s in admin.get("/api/monitoreo").get_json()["servicios"]] == [False, False]
    datos = admin.get("/api/monitoreo?forzar=1").get_json()
    assert [s["operativo"] for s in datos["servicios"]] == [True, True]
    assert datos["eventos"][0]["mensaje"].endswith("volvió a responder")
    assert datos["servicios"][0]["desde_texto"] is None


def test_responde_explica_el_motivo(monkeypatch):
    import urllib.error

    def falla(error):
        def abrir(url, timeout):
            raise error
        monkeypatch.setattr(monitoreo.urllib.request, "urlopen", abrir)
        return monitoreo.responde("http://x")

    assert falla(urllib.error.HTTPError("http://x", 404, "nf", {}, None)) == (False, "El servidor contesta, pero no encuentra la aplicación (error 404). ¿Cambió la dirección?")
    assert falla(urllib.error.HTTPError("http://x", 500, "err", {}, None))[1] == "El servidor respondió con un error (500)"
    assert falla(urllib.error.URLError(TimeoutError()))[1] == "No contestó en 5 segundos"
    assert "No se pudo conectar" in falla(urllib.error.URLError(ConnectionRefusedError()))[1]


def test_generar_y_descargar_informe(admin):
    from openpyxl import load_workbook

    resp = admin.post("/api/informes")
    assert resp.status_code == 201
    informe = admin.get("/api/monitoreo").get_json()["informes"][0]
    assert informe["titulo"].startswith("Sincronización de equipos") and informe["formato"] == "XLSX" and informe["fecha"]
    archivo = admin.get(f"/api/informes/{informe['id']}/descargar")
    assert archivo.mimetype == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert 'filename="sincronizacion-de-equipos' in archivo.headers["Content-Disposition"]
    assert archivo.headers["Content-Disposition"].endswith('.xlsx"')

    libro = load_workbook(io.BytesIO(archivo.data))
    assert libro.sheetnames == ["Resumen", "Equipos"]
    resumen = libro["Resumen"]
    assert resumen["A1"].value == "Informe de sincronización de equipos"
    assert "¿Qué muestra este informe?" in [c.value for c in resumen["A"]]
    equipos = libro["Equipos"]
    titulos = [c.value for c in equipos[1]]
    assert titulos[:3] == ["Institución", "Grupo", "Estudiante"] and "Estado" in titulos
    filas = list(equipos.iter_rows(min_row=2, values_only=True))
    assert len(filas) == resumen["B8"].value  # "Equipos registrados" del resumen = filas de la hoja
    estados = [f[titulos.index("Estado")] for f in filas]
    assert set(estados) <= {"Al día", "Atrasado", "Nunca sincronizó"}
    assert estados == sorted(estados, key=["Nunca sincronizó", "Atrasado", "Al día"].index)  # primero los que necesitan atención
    assert resumen["B9"].value + resumen["B10"].value + resumen["B11"].value == len(filas)


def test_informes_antiguos_en_csv_se_siguen_descargando(admin):
    from servidor_admin.db import ejecutar

    with admin.application.app_context():
        nuevo = ejecutar("INSERT INTO informes (titulo, formato, contenido) VALUES ('Viejo', 'CSV', %s)", (b"Grado,Estudiantes\n1,5",))
    archivo = admin.get(f"/api/informes/{nuevo}/descargar")
    assert archivo.mimetype == "text/csv" and archivo.data.startswith(b"Grado,Estudiantes")


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

def test_panel(docente):
    datos = docente.get("/api/panel").get_json()
    assert datos["activos"] + datos["sin_conexion"] == 24
    assert len(datos["materias"]) == 5
    assert 0 <= datos["avance"] <= 100
    assert 1 <= len(datos["atencion"]) <= 3
    assert {a[3] for a in datos["atencion"]} <= {"Inactivo", "Bajo avance", "Sincronizar"}


def test_estudiantes_y_estados(docente):
    alumnos = docente.get("/api/estudiantes").get_json()
    assert len(alumnos) == 24
    samuel = next(a for a in alumnos if a["nombre"] == "Samuel Ríos")
    assert samuel["estado"] == "Inactivo"
    kevin = next(a for a in alumnos if a["nombre"] == "Kevin Zapata")
    assert kevin["estado"] == "Sin sincronizar"


def test_ficha_y_nota(docente):
    mariana = next(a for a in docente.get("/api/estudiantes").get_json() if a["nombre"] == "Mariana Ospina")
    ficha = docente.get(f"/api/estudiantes/{mariana['id']}").get_json()
    assert ficha["iniciales"] == "MO"
    assert len(ficha["evaluacion"]) == 2
    # Las 16 actividades de la app, sin importar el grado (no salen borradores ni desactivadas)
    nombres = [nombre for nombre, _ in ficha["actividades"]]
    assert len(nombres) == 16
    assert {"Detective de Objetos", "Héroes de la Ciudad", "Module 3"} <= set(nombres)
    assert "Los colores" not in nombres and "Escucha y elige" not in nombres

    resp = docente.put(f"/api/estudiantes/{mariana['id']}/nota", json={"nota": "Repasar inglés en casa."})
    assert resp.status_code == 200
    assert docente.get(f"/api/estudiantes/{mariana['id']}").get_json()["nota"] == "Repasar inglés en casa."
    assert docente.put(f"/api/estudiantes/{mariana['id']}/nota", json={"nota": "x" * 2001}).status_code == 400


def test_no_ve_estudiantes_de_otro_grupo(docente):
    otro = docente.get("/api/estudiantes").get_json()[0]["id"]
    grupos = docente.get("/api/me").get_json()["grupos"]
    docente.post("/api/grupo-activo", json={"grupo_id": grupos[1]["id"]})
    assert docente.get(f"/api/estudiantes/{otro}").status_code == 404
    assert docente.put(f"/api/estudiantes/{otro}/nota", json={"nota": "x"}).status_code == 404


def test_descargas_de_estudiantes(docente):
    excel = docente.get("/api/estudiantes/exportar")
    assert excel.status_code == 200 and excel.data[:2] == b"PK"  # un .xlsx es un ZIP
    alumno = docente.get("/api/estudiantes").get_json()[0]["id"]
    pdf = docente.get(f"/api/estudiantes/{alumno}/informe")
    assert pdf.status_code == 200 and pdf.data[:5] == b"%PDF-"


def test_actividades_del_grupo(docente):
    actividades = docente.get("/api/actividades").get_json()
    ids = [a["id"] for a in actividades]
    assert len(ids) == 16  # las mismas para todos los grados
    assert "heroes-de-la-ciudad" in ids and "module-3" in ids
    assert "los-colores" not in ids  # borrador
    assert "escucha-y-elige" not in ids  # desactivada en el catálogo
    assert all(a["activa"] for a in actividades)  # nada desactivado en 3° A
    assert sum(a["mas_errores"] for a in actividades) == 1


def test_actividad_desactivada_por_el_docente_sale_inactiva(docente):
    grupos = docente.get("/api/me").get_json()["grupos"]
    docente.post("/api/grupo-activo", json={"grupo_id": grupos[1]["id"]})  # 4° B
    module_3 = next(a for a in docente.get("/api/actividades").get_json() if a["id"] == "module-3")
    assert module_3["activa"] is False


def test_porcentajes_se_cortan_como_en_la_app(docente):
    """2 de 3 actividades de Español al 100% = 66,67 → la app muestra 66 (toInt), no 67."""
    from app.compartido.base_datos import ejecutar

    alumno = docente.get("/api/estudiantes").get_json()[1]
    with docente.application.app_context():
        ejecutar("DELETE FROM progreso WHERE estudiante_id = %s AND materia = 'español'", (alumno["id"],))
        for actividad in ("Palabra loca", "Oraciones"):
            ejecutar("""INSERT INTO progreso (estudiante_id, grado, materia, actividad, porcentaje, intentos)
                        VALUES (%s, 2, 'español', %s, 100, 1)""", (alumno["id"], actividad))
    ficha = docente.get(f"/api/estudiantes/{alumno['id']}").get_json()
    assert ficha["materias"][2] == 66  # Español es la tercera: Matemáticas, Ciencias, Español, Sociales, Inglés


def test_si_completa_todo_tiene_100(docente):
    """Regla de la app: suma de % ÷ (total × 100), para cualquier grado."""
    from app.compartido.base_datos import consultar, ejecutar

    alumno = docente.get("/api/estudiantes").get_json()[0]
    with docente.application.app_context():
        for a in consultar("SELECT nombre, materia FROM actividades WHERE estado = 'Publicada'"):
            ejecutar(
                """INSERT INTO progreso (estudiante_id, grado, materia, actividad, porcentaje, intentos, ultima_vez)
                   VALUES (%s, 2, %s, %s, 100, 1, NOW())
                   ON DUPLICATE KEY UPDATE porcentaje = 100""",
                (alumno["id"], a["materia"], a["nombre"]),
            )
    ficha = docente.get(f"/api/estudiantes/{alumno['id']}").get_json()
    assert ficha["materias"] == [100, 100, 100, 100, 100]
    assert ficha["avance"] == 100
    assert all(valor == "Completada" for _, valor in ficha["actividades"])


def test_activar_y_desactivar_actividad(docente):
    resp = docente.patch("/api/actividades/los-numeros", json={"activa": False})
    assert resp.get_json()["activa"] is False
    los_numeros = next(a for a in docente.get("/api/actividades").get_json() if a["id"] == "los-numeros")
    assert los_numeros["activa"] is False
    docente.patch("/api/actividades/los-numeros", json={"activa": True})
    assert docente.patch("/api/actividades/los-numeros", json={"activa": "si"}).status_code == 400
    assert docente.patch("/api/actividades/escucha-y-elige", json={"activa": True}).status_code == 404


def test_reportes_por_periodo(docente):
    p1 = docente.get("/api/reportes?periodo=p1").get_json()
    anio = docente.get("/api/reportes?periodo=anio").get_json()
    assert p1["periodo"]["nombre"] == "Periodo 1"
    assert anio["promedio"] >= p1["promedio"]  # en el año entra todo el progreso
    assert anio["minimo_nombre"] in ("Matemáticas", "Español", "Ciencias", "Sociales", "Inglés")
    assert anio["estudiantes"] == sorted(anio["estudiantes"], key=lambda e: -e[1])
    assert docente.get("/api/reportes?periodo=p9").status_code == 404


def test_descargar_reporte(docente):
    base = "/api/reportes/descargar?periodo=s1&desde=2026-01-26&hasta=2026-06-19&estado="
    todo = "&materias=matematicas,español,ciencias,sociales,ingles&incluir=avance,detalle,evaluacion,notas,racha"
    assert docente.get(base + todo + "&formato=pdf").data[:5] == b"%PDF-"
    assert docente.get(base + todo + "&formato=xlsx").data[:2] == b"PK"
    assert docente.get(base + "&materias=&incluir=avance&formato=pdf").status_code == 400
    assert docente.get(base + "&materias=ingles&incluir=&formato=pdf").status_code == 400
    assert docente.get(base + todo + "&formato=doc").status_code == 400
    al_reves = "/api/reportes/descargar?periodo=s1&desde=2026-06-19&hasta=2026-01-26"
    assert docente.get(al_reves + todo + "&formato=pdf").status_code == 400


def test_actividad_del_panel_solo_cuenta_si_es_jugable(docente):
    """Como "toca las frutas": publicada en el panel pero sin preguntas → el niño no la puede jugar."""
    from app.compartido.base_datos import ejecutar

    with docente.application.app_context():
        ejecutar("""INSERT INTO actividades (slug, nombre, materia, grado, tipo, estado, en_app)
                    VALUES ('toca-las-frutas', 'toca las frutas', 'ciencias', 3, 'Selección múltiple', 'Publicada', FALSE)""")  # 3° A: el grupo de Luisa al iniciar sesión
    ids = [a["id"] for a in docente.get("/api/actividades").get_json()]
    assert "toca-las-frutas" not in ids and len(ids) == 16

    with docente.application.app_context():
        ejecutar("""UPDATE actividades SET contenido = '{"preguntas": [{"enunciado": "x", "audio": null, "opciones": []}]}'
                    WHERE slug = 'toca-las-frutas'""")
    ids = [a["id"] for a in docente.get("/api/actividades").get_json()]
    assert "toca-las-frutas" in ids and len(ids) == 17


def test_las_materias_van_en_el_orden_del_menu_de_la_app(docente):
    from app.dominios.seguimiento import repositorios

    with docente.application.app_context():
        assert [m["clave"] for m in repositorios.materias()] == ["matematicas", "ciencias", "español", "sociales", "ingles"]
    reporte = docente.get("/api/reportes?periodo=anio").get_json()
    assert len(reporte["materias"]) == 5


def test_reportes_abre_en_el_periodo_de_hoy(docente, monkeypatch):
    """Antes abría siempre en el Periodo 1: el avance de hoy salía en 0 %."""
    from datetime import date

    from app.dominios.reportes import repositorios as reportes

    def hoy(dia):
        class Fecha(date):
            @classmethod
            def today(cls):
                return dia
        monkeypatch.setattr(reportes, "date", Fecha)

    esperado = {
        date(2026, 2, 10): "p1", date(2026, 5, 4): "p2", date(2026, 8, 3): "p3", date(2026, 11, 2): "p4",
        date(2026, 6, 25): "anio",   # vacaciones de mitad de año: ningún periodo, vale el año completo
        date(2026, 12, 15): "anio",  # después del Periodo 4
        date(2027, 3, 1): "anio",    # año siguiente: el más reciente
    }
    for dia, clave in esperado.items():
        hoy(dia)
        datos = docente.get("/api/reportes").get_json()
        assert datos["periodo"]["clave"] == clave, dia
    assert [p["clave"] for p in datos["periodos"]] == ["p1", "p2", "p3", "p4", "s1", "s2", "anio"]


def test_el_avance_de_hoy_aparece_en_reportes(docente):
    """El avance que el niño hizo hoy se ve en el periodo de hoy y en el año, no en los periodos ya cerrados."""
    from app.compartido.base_datos import ejecutar

    alumno = docente.get("/api/estudiantes").get_json()[0]
    with docente.application.app_context():
        ejecutar("DELETE FROM progreso WHERE estudiante_id = %s", (alumno["id"],))
        ejecutar("""INSERT INTO progreso (estudiante_id, grado, materia, actividad, porcentaje, intentos, ultima_vez)
                    VALUES (%s, 3, 'matematicas', 'Los números', 100, 1, NOW())""", (alumno["id"],))
    ahora = docente.get("/api/reportes").get_json()          # el periodo de hoy
    anio = docente.get("/api/reportes?periodo=anio").get_json()
    p1 = docente.get("/api/reportes?periodo=p1").get_json()
    nombre = next(e for e in docente.get("/api/estudiantes").get_json() if e["id"] == alumno["id"])["nombre"]
    def avance(reporte):
        return dict(map(tuple, reporte["estudiantes"])).get(nombre)

    assert avance(anio) > 0
    assert avance(ahora) == avance(anio)
    assert avance(p1) == 0


def test_el_promedio_del_reporte_es_el_mismo_avance_del_panel(docente):
    """Antes se promediaban porcentajes ya cortados y salía 1 punto menos que el avance de los estudiantes."""
    from app.compartido.base_datos import ejecutar

    with docente.application.app_context():  # otras pruebas dejan avances sin fecha, que un periodo no puede ubicar
        ejecutar("UPDATE progreso SET ultima_vez = NOW() WHERE ultima_vez IS NULL")
    panel = docente.get("/api/panel").get_json()
    anio = docente.get("/api/reportes?periodo=anio").get_json()
    assert anio["promedio"] == panel["avance"]

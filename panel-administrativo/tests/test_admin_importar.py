import io
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "database"))

from database.init_db import conectar  # noqa: E402
from importar_recursos_app import clasificar, es_captura, importar  # noqa: E402

BD_PRUEBAS = "numi_test"


def test_clasifica_por_materia():
    assert clasificar("images/actividades/ciencias_naturales/pantalla 1/perro.png") == ("actividades/ciencias", "pantalla 1/perro.png")
    assert clasificar("Audio/Matematicas/uno.mp3") == ("actividades/matematicas", "uno.mp3")
    assert clasificar("images/areas/ingles/juego_1/imagenes_1/cat.png") == ("actividades/ingles", "juego_1/imagenes_1/cat.png")
    assert clasificar("videos/intro.mp4") == ("app/general", "videos/intro.mp4")


def test_reconoce_capturas_y_no_confunde_recursos():
    assert es_captura("images/actividades/ciencias_naturales/pantalla 3/ciencias naturales p3.png")
    assert es_captura("images/actividades/espanol/juego 1.3  español.png")
    assert es_captura("images/areas/ingles/pantallas guia/juego2/juego 2.1.png")
    assert es_captura("images/actividades/sociales/Mockup final.PNG")
    # Recursos reales que viven en carpetas con nombres parecidos
    assert not es_captura("images/actividades/ciencias_naturales/pantalla 1/cocodrilo.png")
    assert not es_captura("images/areas/ingles/juego_1/imagenes_1/gato.png")
    assert not es_captura("images/actividades/sociales/Completar_rompecabeza.png")


def crear_assets(carpeta):
    archivos = {
        "images/actividades/sociales/bombero.png": b"\x89PNG-1",
        "images/actividades/ciencias_naturales/pantalla 2/flor.png": b"\x89PNG-2",
        "Audio/espanol/silaba.mp3": b"ID3",
        "animations/planta_creciendo.mp4": b"\x00\x00video",
        "images/notas.txt": b"no es un recurso",
        # Capturas de pantalla de la app: no deben aparecer en Recursos
        "images/actividades/espanol/juego 1.1 español.png": b"captura",
        "images/areas/ingles/pantallas guia/juego1/juego 1.1.png": b"captura",
        "images/actividades/sociales/Mockup final.PNG": b"captura",
    }
    for ruta, contenido in archivos.items():
        destino = carpeta / ruta
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(contenido)


def test_importa_copia_y_no_duplica(base_de_pruebas, admin, tmp_path):
    crear_assets(tmp_path / "assets")
    uploads = admin.application.config["CARPETA_UPLOADS"]
    # Una captura que quedó de una importación anterior
    (uploads / "app/images/actividades/ciencias_naturales/pantalla 1").mkdir(parents=True)
    vieja = uploads / "app/images/actividades/ciencias_naturales/pantalla 1/ciencias naturales p1.png"
    vieja.write_bytes(b"captura")
    con = conectar(BD_PRUEBAS)
    try:
        with con.cursor() as cur:
            cur.execute("INSERT INTO recursos (nombre, tipo, carpeta, archivo) VALUES ('pantalla 1/ciencias naturales p1.png', "
                        "'Imagen', 'actividades/ciencias', 'app/images/actividades/ciencias_naturales/pantalla 1/ciencias naturales p1.png')")
            primera = importar(cur, tmp_path / "assets", uploads)
            segunda = importar(cur, tmp_path / "assets", uploads)
        con.commit()
    finally:
        con.close()

    assert primera["nuevos"] == 4 and primera["ejemplos_borrados"] == 21 and primera["capturas_quitadas"] == 1
    assert segunda == {"nuevos": 0, "existentes": 4, "ejemplos_borrados": 0, "capturas_quitadas": 0}
    assert not vieja.exists()
    assert (uploads / "app/images/actividades/ciencias_naturales/pantalla 2/flor.png").read_bytes() == b"\x89PNG-2"

    recursos = {r["nombre"]: r for r in admin.get("/api/recursos").get_json()["recursos"]}
    assert set(recursos) == {"bombero.png", "pantalla 2/flor.png", "silaba.mp3", "animations/planta_creciendo.mp4"}
    flor = recursos["pantalla 2/flor.png"]
    assert flor["carpeta"] == "actividades/ciencias" and flor["compatible"]
    assert flor["url"] == "/uploads/app/images/actividades/ciencias_naturales/pantalla%202/flor.png"
    assert admin.get(flor["url"]).data == b"\x89PNG-2"  # el navegador puede mostrar la miniatura
    assert recursos["animations/planta_creciendo.mp4"]["tipo"] == "Video"


def test_subir_video(admin):
    datos = {"carpeta": "actividades/ciencias", "archivos": [(io.BytesIO(b"\x00video"), "intro.mp4")]}
    resp = admin.post("/api/recursos", data=datos, content_type="multipart/form-data")
    assert resp.status_code == 201
    video = next(r for r in admin.get("/api/recursos").get_json()["recursos"] if r["nombre"] == "intro.mp4")
    assert video["tipo"] == "Video"

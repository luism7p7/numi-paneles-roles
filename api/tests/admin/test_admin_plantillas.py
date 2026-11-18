"""Plantillas de actividad: cada tipo guarda su contenido y solo se publica si está completo."""

import itertools

import pytest


def recurso(admin, nombre):
    recursos = admin.get("/api/recursos").get_json()["recursos"]
    return next(r["id"] for r in recursos if r["nombre"] == nombre)


def pregunta(audio=None):
    return {"enunciado": "¿Cuál es una fruta?", "audio": audio, "opciones": [
        {"texto": "Manzana", "imagen": None, "correcta": True},
        {"texto": "Silla", "imagen": None, "correcta": False},
    ]}

def nueva(**cambios):
    datos = {"nombre": "Prueba", "materia": "Ciencias naturales", "grado": "Grado 2°",
             "tipo": "Selección múltiple", "estado": "Publicada", "recursos": [], "contenido": None}
    return datos | cambios

def clasificar(admin):
    return {"grupos": [{"nombre": "Vivo", "imagen": None}, {"nombre": "No vivo", "imagen": recurso(admin, "piedra.png")}],
            "elementos": [{"texto": "Perro", "imagen": recurso(admin, "perro.png"), "grupo": 0},
                          {"texto": "Piedra", "imagen": None, "grupo": 1}]}

def emparejar(admin):
    return {"parejas": [{"elemento": {"texto": "3", "imagen": None},
                         "destino": {"texto": "", "imagen": recurso(admin, "manzana.png")}},
                        {"elemento": {"texto": "1", "imagen": None},
                         "destino": {"texto": "", "imagen": recurso(admin, "globo.png")}}]}

def silabas(admin):
    return {"palabras": [{"silabas": ["ma", "ri", "po", "sa"], "imagen": recurso(admin, "globo.png"), "audio": None},
                         {"silabas": ["ga", "to"], "imagen": None, "audio": None}]}

def memory(admin):
    return {"pares": [{"texto": "Dog", "imagen": recurso(admin, "perro.png")}, {"texto": "Ball", "imagen": None}]}

def auditiva(admin):
    return {"preguntas": [pregunta(audio=recurso(admin, "contar.mp3"))]}

CONTENIDOS = {
    "Arrastrar": clasificar,
    "Arrastrar y soltar": emparejar,
    "Ordenar sílabas": silabas,
    "Memory match": memory,
    "Comprensión auditiva": auditiva,
}

# Archivos de ejemplo que usa cada contenido de arriba
USADOS = {
    "Arrastrar": {"piedra.png", "perro.png"},
    "Arrastrar y soltar": {"manzana.png", "globo.png"},
    "Ordenar sílabas": {"globo.png"},
    "Memory match": {"perro.png"},
    "Comprensión auditiva": {"contar.mp3"},
}

numero = itertools.count(1)


def publicar(admin, tipo, contenido, **cambios):
    """Crea una actividad con un nombre nuevo (la base se comparte entre las pruebas del archivo)."""
    datos = nueva(nombre=f"Prueba {tipo} {next(numero)}", tipo=tipo, contenido=contenido) | cambios
    return admin.post("/api/actividades", json=datos)

@pytest.mark.parametrize("tipo", CONTENIDOS)
def test_cada_tipo_se_publica_con_su_contenido(admin, tipo):
    contenido = CONTENIDOS[tipo](admin)
    resp = publicar(admin, tipo, contenido)
    assert resp.status_code == 201, resp.get_json()
    detalle = admin.get(f"/api/actividades/{resp.get_json()['id']}").get_json()
    assert detalle["tipo"] == tipo and detalle["estado"] == "Publicada"
    assert detalle["contenido"] == contenido
    assert detalle["en_app"] is False

@pytest.mark.parametrize("tipo", CONTENIDOS)
def test_cada_tipo_vincula_los_recursos_que_usa(admin, tipo):
    slug = publicar(admin, tipo, CONTENIDOS[tipo](admin)).get_json()["id"]
    vinculados = {r["nombre"] for r in admin.get(f"/api/actividades/{slug}").get_json()["recursos"]}
    assert vinculados == USADOS[tipo]

@pytest.mark.parametrize("tipo", CONTENIDOS)
def test_vacio_no_se_publica_pero_si_es_borrador(admin, tipo):
    assert publicar(admin, tipo, None).status_code == 400
    assert publicar(admin, tipo, {}).status_code == 400
    assert publicar(admin, tipo, None, estado="Borrador").status_code == 201

def test_arrastrar_exige_grupos_y_elementos_completos(admin):
    base = clasificar(admin)
    casos = [
        base | {"grupos": base["grupos"][:1]},                                            # un solo grupo
        base | {"grupos": [{"nombre": "", "imagen": None}, base["grupos"][1]]},           # grupo sin nombre
        base | {"elementos": [{"texto": "Perro", "imagen": None, "grupo": 0}]},           # el grupo 2 sin elementos
        base | {"elementos": base["elementos"] + [{"texto": "", "imagen": None, "grupo": 0}]},     # elemento vacío
        base | {"elementos": base["elementos"] + [{"texto": "Sol", "imagen": None, "grupo": None}]},  # sin grupo
        base | {"elementos": base["elementos"] + [{"texto": "Sol", "imagen": None, "grupo": 7}]},     # grupo inexistente
        base | {"grupos": base["grupos"] * 3},                                            # más de 4 grupos
    ]
    # Dos grupos con el mismo nombre (aunque cambie la mayúscula) confunden al niño
    repetidos = base | {"grupos": [{"nombre": "Vivo", "imagen": None}, {"nombre": " vivo ", "imagen": None}],
                        "elementos": [{"texto": "Perro", "imagen": None, "grupo": 0}, {"texto": "Gato", "imagen": None, "grupo": 1}]}
    resp = publicar(admin, "Arrastrar", repetidos)
    assert resp.status_code == 400 and "se llaman igual" in resp.get_json()["error"]
    assert publicar(admin, "Arrastrar", repetidos, estado="Borrador").status_code == 201  # un borrador puede estar a medias
    for contenido in casos:
        assert publicar(admin, "Arrastrar", contenido).status_code == 400, contenido
    # A medias sí se guarda como borrador, pero un grupo inexistente nunca
    assert publicar(admin, "Arrastrar", casos[2], estado="Borrador").status_code == 201
    assert publicar(admin, "Arrastrar", casos[5], estado="Borrador").status_code == 400

def test_arrastrar_y_soltar_exige_parejas_completas(admin):
    base = emparejar(admin)
    sin_destino = {"parejas": [base["parejas"][0], {"elemento": {"texto": "2"}, "destino": {"texto": ""}}]}
    for contenido in ({"parejas": base["parejas"][:1]}, sin_destino, {"parejas": base["parejas"] * 4}, {"parejas": [1, 2]}):
        assert publicar(admin, "Arrastrar y soltar", contenido).status_code == 400, contenido

def test_ordenar_silabas_exige_al_menos_dos_silabas(admin):
    for contenido in ({"palabras": [{"silabas": ["sol"]}]}, {"palabras": [{"silabas": []}]},
                      {"palabras": [{"silabas": list("abcdefg")}]}, {"palabras": []}):
        assert publicar(admin, "Ordenar sílabas", contenido).status_code == 400, contenido
    # Se limpian los espacios y las sílabas vacías
    ok = publicar(admin, "Ordenar sílabas", {"palabras": [{"silabas": [" ma ", "", "no"]}]})
    assert ok.status_code == 201
    palabras = admin.get(f"/api/actividades/{ok.get_json()['id']}").get_json()["contenido"]["palabras"]
    assert palabras[0]["silabas"] == ["ma", "no"]

def test_memory_exige_al_menos_dos_pares_con_algo_que_mostrar(admin):
    for contenido in ({"pares": [{"texto": "Dog"}]}, {"pares": [{"texto": "Dog"}, {"texto": "", "imagen": None}]},
                      {"pares": [{"texto": str(i)} for i in range(9)]}):
        assert publicar(admin, "Memory match", contenido).status_code == 400, contenido

def test_comprension_auditiva_exige_audio_en_cada_pregunta(admin):
    sin_audio = {"preguntas": [pregunta()]}
    resp = publicar(admin, "Comprensión auditiva", sin_audio)
    assert resp.status_code == 400 and "audio" in resp.get_json()["error"].lower()
    assert publicar(admin, "Comprensión auditiva", sin_audio, estado="Borrador").status_code == 201

def test_cada_archivo_debe_ser_del_tipo_que_pide_la_plantilla(admin):
    audio = recurso(admin, "contar.mp3")
    imagen = recurso(admin, "perro.png")
    assert publicar(admin, "Memory match", {"pares": [{"imagen": audio}, {"texto": "Ball"}]}).status_code == 400
    assert publicar(admin, "Ordenar sílabas", {"palabras": [{"silabas": ["ga", "to"], "audio": imagen}]}).status_code == 400
    grupos_con_audio = clasificar(admin) | {"grupos": [{"nombre": "A", "imagen": audio}, {"nombre": "B"}]}
    assert publicar(admin, "Arrastrar", grupos_con_audio).status_code == 400
    # Un mismo archivo no puede ser imagen y audio a la vez
    mezcla = {"palabras": [{"silabas": ["ga", "to"], "imagen": imagen, "audio": imagen}]}
    assert publicar(admin, "Ordenar sílabas", mezcla).status_code == 400

def test_cambiar_el_tipo_de_un_borrador_valida_con_la_plantilla_nueva(admin):
    slug = publicar(admin, "Memory match", None, estado="Borrador").get_json()["id"]
    contenido = clasificar(admin)
    resp = admin.put(f"/api/actividades/{slug}", json=nueva(nombre="Cambio de tipo", tipo="Arrastrar", contenido=contenido))
    assert resp.status_code == 200, resp.get_json()
    assert admin.get(f"/api/actividades/{slug}").get_json()["contenido"] == contenido

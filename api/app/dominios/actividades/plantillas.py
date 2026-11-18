"""Plantillas de actividad: el contenido que arma el administrador y que la app juega.

Cada tipo de actividad tiene su formato de contenido (se guarda en actividades.contenido):

    Selección múltiple    {"preguntas": [{"enunciado", "audio", "opciones": [{"texto", "imagen", "correcta"}]}]}
    Comprensión auditiva  igual que la anterior, pero cada pregunta lleva un audio
    Arrastrar             {"grupos": [{"nombre", "imagen"}],
                           "elementos": [{"texto", "imagen", "grupo": <posición en grupos>}]}
                          el niño arrastra cada elemento al grupo al que pertenece
    Arrastrar y soltar    {"parejas": [{"elemento": {"texto", "imagen"}, "destino": {"texto", "imagen"}}]}
                          el niño arrastra cada elemento a su pareja
    Ordenar sílabas       {"palabras": [{"silabas": ["ma", "ri", "po", "sa"], "imagen", "audio"}]}
                          el niño ordena las sílabas (la app las desordena)
    Memory match          {"pares": [{"texto", "imagen"}]}
                          cada par son dos cartas (imagen y texto, o dos iguales si solo hay una)

Las imágenes y los audios son ids de la tabla `recursos`. Un borrador puede estar
incompleto; para publicar (completo=True) todo debe estar bien.
"""

from app.compartido.validaciones import entero
from app.excepciones import ErrorDeDatos

MAX_PREGUNTAS = 20
MAX_OPCIONES = 4
MAX_GRUPOS = 4
MAX_ELEMENTOS = 12
MAX_PAREJAS = 6
MAX_PALABRAS = 10
MAX_SILABAS = 6
MAX_PARES = 8


def _id_recurso(valor, tipo, usados):
    """Id de un recurso (o None). Anota en `usados` qué tipo de archivo debe ser."""
    if valor in (None, ""):
        return None
    recurso = entero(valor, "el recurso", 1, 10**9)
    if usados.get(recurso, tipo) != tipo:
        raise ErrorDeDatos("Un mismo recurso no puede usarse como imagen y como audio.")
    usados[recurso] = tipo
    return recurso


def _texto(valor, maximo):
    return str(valor or "").strip()[:maximo]


def _lista(valor, mensaje, maximo=None):
    if not isinstance(valor, list) or (maximo is not None and len(valor) > maximo):
        raise ErrorDeDatos(mensaje)
    return valor


def _objeto(valor, mensaje):
    if not isinstance(valor, dict):
        raise ErrorDeDatos(mensaje)
    return valor


def _objetos(lista, mensaje):
    """Recorre la lista dando (posición, objeto); cada elemento debe ser un objeto. `mensaje` lleva {n}."""
    for n, valor in enumerate(lista, start=1):
        yield n, _objeto(valor, mensaje.format(n=n))


def _contenido(contenido, clave, maximo, plural):
    if contenido is None:
        contenido = {clave: []}
    if not isinstance(contenido, dict) or not isinstance(contenido.get(clave), list):
        raise ErrorDeDatos("El contenido de la actividad no es válido.")
    if len(contenido[clave]) > maximo:
        raise ErrorDeDatos(f"Una actividad puede tener máximo {maximo} {plural}.")
    return contenido[clave]


def _preguntas(contenido, completo, audio_obligatorio=False):
    preguntas = _contenido(contenido, "preguntas", MAX_PREGUNTAS, "preguntas")
    if completo and not preguntas:
        raise ErrorDeDatos("Agrega al menos una pregunta antes de publicar.")

    limpias, usados = [], {}
    for n, pregunta in _objetos(preguntas, "La pregunta {n} no es válida."):
        opciones = pregunta.get("opciones")
        if not isinstance(opciones, list) or len(opciones) > MAX_OPCIONES:
            raise ErrorDeDatos(f"La pregunta {n} debe tener máximo {MAX_OPCIONES} opciones.")
        enunciado = str(pregunta.get("enunciado") or "").strip()
        if len(enunciado) > 200:
            raise ErrorDeDatos(f"El enunciado de la pregunta {n} es muy largo (máximo 200 caracteres).")
        audio = _id_recurso(pregunta.get("audio"), "Audio", usados)
        limpias_opciones = []
        for _, opcion in _objetos(opciones, f"Las opciones de la pregunta {n} no son válidas."):
            limpias_opciones.append({
                "texto": _texto(opcion.get("texto"), 60),
                "imagen": _id_recurso(opcion.get("imagen"), "Imagen", usados),
                "correcta": opcion.get("correcta") is True,
            })
        if completo:
            if not enunciado:
                raise ErrorDeDatos(f"Escribe el enunciado de la pregunta {n}.")
            if audio_obligatorio and not audio:
                raise ErrorDeDatos(f"La pregunta {n} necesita un audio: es una actividad de comprensión auditiva.")
            if len(limpias_opciones) < 2:
                raise ErrorDeDatos(f"La pregunta {n} necesita al menos 2 opciones.")
            if any(not o["texto"] and not o["imagen"] for o in limpias_opciones):
                raise ErrorDeDatos(f"Cada opción de la pregunta {n} necesita un texto o una imagen.")
            if sum(o["correcta"] for o in limpias_opciones) != 1:
                raise ErrorDeDatos(f"Marca una sola respuesta correcta en la pregunta {n}.")
        limpias.append({"enunciado": enunciado, "audio": audio, "opciones": limpias_opciones})
    return {"preguntas": limpias}, usados


def _comprension_auditiva(contenido, completo):
    return _preguntas(contenido, completo, audio_obligatorio=True)


def _clasificar(contenido, completo):
    """Arrastrar: elementos que se arrastran al grupo al que pertenecen."""
    if contenido is None:
        contenido = {"grupos": [], "elementos": []}
    contenido = _objeto(contenido, "El contenido de la actividad no es válido.")
    grupos = _lista(contenido.get("grupos"), f"Una actividad puede tener máximo {MAX_GRUPOS} grupos.", MAX_GRUPOS)
    elementos = _lista(contenido.get("elementos"),
                       f"Una actividad puede tener máximo {MAX_ELEMENTOS} elementos.", MAX_ELEMENTOS)

    usados = {}
    limpios_grupos = []
    for _, grupo in _objetos(grupos, "El grupo {n} no es válido."):
        limpios_grupos.append({"nombre": _texto(grupo.get("nombre"), 40),
                               "imagen": _id_recurso(grupo.get("imagen"), "Imagen", usados)})

    limpios = []
    for n, elemento in _objetos(elementos, "El elemento {n} no es válido."):
        grupo = elemento.get("grupo")
        if grupo is not None:
            grupo = entero(grupo, "el grupo del elemento", 0, 10**6)
            if grupo >= len(limpios_grupos):
                raise ErrorDeDatos(f"El elemento {n} apunta a un grupo que no existe.")
        limpios.append({"texto": _texto(elemento.get("texto"), 40),
                        "imagen": _id_recurso(elemento.get("imagen"), "Imagen", usados),
                        "grupo": grupo})

    if completo:
        if len(limpios_grupos) < 2:
            raise ErrorDeDatos("Agrega al menos 2 grupos antes de publicar.")
        vistos = {}
        for n, grupo in enumerate(limpios_grupos, start=1):
            if not grupo["nombre"]:
                raise ErrorDeDatos(f"Escribe el nombre del grupo {n}.")
            clave = grupo["nombre"].casefold()
            if clave in vistos:
                raise ErrorDeDatos(f"Los grupos {vistos[clave]} y {n} se llaman igual («{grupo['nombre']}»): "
                                   "el niño no podría saber cuál elegir. Cambia el nombre o quita uno.")
            vistos[clave] = n
        if len(limpios) < len(limpios_grupos):
            raise ErrorDeDatos("Agrega al menos un elemento por cada grupo.")
        for n, elemento in enumerate(limpios, start=1):
            if not elemento["texto"] and not elemento["imagen"]:
                raise ErrorDeDatos(f"El elemento {n} necesita un texto o una imagen.")
            if elemento["grupo"] is None:
                raise ErrorDeDatos(f"Elige el grupo del elemento {n}.")
        vacios = set(range(len(limpios_grupos))) - {e["grupo"] for e in limpios}
        if vacios:
            raise ErrorDeDatos(f"El grupo «{limpios_grupos[min(vacios)]['nombre']}» no tiene ningún elemento.")
    return {"grupos": limpios_grupos, "elementos": limpios}, usados


def _lado(valor, mensaje, usados):
    valor = _objeto(valor, mensaje)
    return {"texto": _texto(valor.get("texto"), 40), "imagen": _id_recurso(valor.get("imagen"), "Imagen", usados)}


def _emparejar(contenido, completo):
    """Arrastrar y soltar: cada elemento se arrastra a su pareja."""
    parejas = _contenido(contenido, "parejas", MAX_PAREJAS, "parejas")
    if completo and len(parejas) < 2:
        raise ErrorDeDatos("Agrega al menos 2 parejas antes de publicar.")

    usados, limpias = {}, []
    for n, pareja in _objetos(parejas, "La pareja {n} no es válida."):
        mensaje = f"La pareja {n} no es válida."
        elemento = _lado(pareja.get("elemento", {}), mensaje, usados)
        destino = _lado(pareja.get("destino", {}), mensaje, usados)
        if completo:
            for nombre, lado in (("el elemento", elemento), ("el destino", destino)):
                if not lado["texto"] and not lado["imagen"]:
                    raise ErrorDeDatos(f"En la pareja {n}, {nombre} necesita un texto o una imagen.")
        limpias.append({"elemento": elemento, "destino": destino})
    return {"parejas": limpias}, usados


def _silabas(contenido, completo):
    """Ordenar sílabas: el niño arma cada palabra con sus sílabas."""
    palabras = _contenido(contenido, "palabras", MAX_PALABRAS, "palabras")
    if completo and not palabras:
        raise ErrorDeDatos("Agrega al menos una palabra antes de publicar.")

    usados, limpias = {}, []
    for n, palabra in _objetos(palabras, "La palabra {n} no es válida."):
        silabas = _lista(palabra.get("silabas"), f"La palabra {n} debe tener máximo {MAX_SILABAS} sílabas.", MAX_SILABAS)
        silabas = [_texto(s, 12) for s in silabas if isinstance(s, str)]
        limpias.append({"silabas": [s for s in silabas if s],
                        "imagen": _id_recurso(palabra.get("imagen"), "Imagen", usados),
                        "audio": _id_recurso(palabra.get("audio"), "Audio", usados)})
        if completo and len(limpias[-1]["silabas"]) < 2:
            raise ErrorDeDatos(f"La palabra {n} necesita al menos 2 sílabas.")
    return {"palabras": limpias}, usados


def _memory(contenido, completo):
    """Memory match: cada par genera dos cartas."""
    pares = _contenido(contenido, "pares", MAX_PARES, "pares")
    if completo and len(pares) < 2:
        raise ErrorDeDatos("Agrega al menos 2 pares antes de publicar.")

    usados, limpios = {}, []
    for n, par in _objetos(pares, "El par {n} no es válido."):
        limpio = {"texto": _texto(par.get("texto"), 30), "imagen": _id_recurso(par.get("imagen"), "Imagen", usados)}
        if completo and not limpio["texto"] and not limpio["imagen"]:
            raise ErrorDeDatos(f"El par {n} necesita un texto o una imagen.")
        limpios.append(limpio)
    return {"pares": limpios}, usados


# Tipo de actividad → validador. Un tipo que no está aquí solo existe como pantalla programada en la app.
VALIDADORES = {
    "Selección múltiple": _preguntas,
    "Comprensión auditiva": _comprension_auditiva,
    "Arrastrar": _clasificar,
    "Arrastrar y soltar": _emparejar,
    "Ordenar sílabas": _silabas,
    "Memory match": _memory,
}
PLANTILLAS = set(VALIDADORES)


def validar_contenido(tipo, contenido, completo):
    """Devuelve (contenido_limpio, {id_recurso: tipo_de_archivo_esperado})."""
    return VALIDADORES[tipo](contenido, completo)

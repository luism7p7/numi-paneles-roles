"""Reglas de las actividades: borrador o publicada, validación del contenido y registro de cada cambio."""

import json

from app.compartido.base_datos import confirmar
from app.compartido.fechas import fecha_corta
from app.compartido.textos import slug as hacer_slug
from app.dominios.recursos import servicios as recursos
from app.excepciones import Conflicto, ErrorDeDatos, NoEncontrado

from . import plantillas
from . import repositorios as repo


def _actividad_json(fila):
    return {
        "id": fila["slug"],
        "nombre": fila["nombre"],
        "materia": fila["materia"],
        "grado": f"{fila['grado']}°",
        "tipo": fila["tipo"],
        "descripcion": fila["descripcion"],
        "estado": fila["estado"],
        "resuelta": str(int(fila["resuelta"])) if fila["resuelta"] else "Sin uso registrado",
        "en_app": bool(fila["en_app"]),
        "contenido": json.loads(fila["contenido"]) if fila["contenido"] else None,
    }


def _buscar(slug):
    fila = repo.por_slug(slug)
    if fila is None:
        raise NoEncontrado("La actividad no existe o fue eliminada.")
    return fila


def _slug_libre(nombre):
    base = hacer_slug(nombre)
    candidato, n = base, 2
    while repo.slug_existe(candidato):
        candidato, n = f"{base}-{n}", n + 1
    return candidato


def _validar(datos, actual=None):
    """Reglas que dependen de la base: nombre único, materia, plantilla del tipo y recursos compatibles."""
    nombre = datos["nombre"]
    if repo.nombre_repetido(nombre, actual["id"] if actual else 0):
        raise Conflicto(f"Ya existe una actividad llamada «{nombre}».")
    materia = repo.materia_por_nombre_o_clave(datos["materia"].strip())
    if materia is None:
        raise ErrorDeDatos("Elige una materia válida.")

    tipo, estado = datos["tipo"], datos["estado"]
    # Una actividad creada en el panel solo llega al celular si su tipo tiene plantilla en la app
    en_app = bool(actual and actual["en_app"])
    contenido, usados = None, {}
    if tipo in plantillas.PLANTILLAS and not en_app:
        contenido, usados = plantillas.validar_contenido(tipo, datos["contenido"], completo=estado == "Publicada")
    elif estado == "Publicada" and not en_app:
        raise ErrorDeDatos(f"La app todavía no tiene plantilla para «{tipo}». Guárdala como borrador.")

    # Recursos: los marcados en la cuadrícula + los que usan las preguntas
    ids = set(datos["recursos"]) | set(usados)
    elegidos = recursos.elegidos(ids)
    for r, info in elegidos:
        if r["id"] in usados and r["tipo"] != usados[r["id"]]:
            raise ErrorDeDatos(f"{r['nombre']} no es un recurso de tipo {usados[r['id']].lower()}.")
        if not info["compatible"]:
            raise ErrorDeDatos(f"{r['nombre']} requiere la v{r['version_minima']} y hay equipos con versiones anteriores.")

    return {
        "nombre": nombre,
        "materia": materia,
        "grado": datos["grado"],
        "tipo": tipo,
        "estado": estado,
        "descripcion": datos["descripcion"],
        "recursos": {r["id"]: r["nombre"] for r, _ in elegidos},
        "contenido": json.dumps(contenido, ensure_ascii=False) if contenido else None,
    }


def listar():
    return [_actividad_json(f) for f in repo.listar()]


def detalle(slug):
    fila = _buscar(slug)
    return _actividad_json(fila) | {"recursos": repo.recursos_de(fila["id"])}


def crear(datos, usuario_id):
    v = _validar(datos)
    nuevo_slug = _slug_libre(v["nombre"])
    actividad_id = repo.crear(nuevo_slug, v)
    repo.guardar_recursos(actividad_id, v["recursos"])
    if v["estado"] == "Publicada":
        repo.registrar_cambio(actividad_id, v["nombre"], "Actividad publicada", "Publicada", usuario_id)
    else:
        repo.registrar_cambio(actividad_id, v["nombre"], "Guardada como borrador", "Borrador", usuario_id)
    confirmar()
    return {"id": nuevo_slug, "estado": v["estado"]}


def editar(slug, datos, usuario_id):
    actual = _buscar(slug)
    v = _validar(datos, actual)
    antes = {r["id"]: r["nombre"] for r in repo.recursos_de(actual["id"])}

    repo.actualizar(actual["id"], v)
    repo.guardar_recursos(actual["id"], v["recursos"])

    # Historial: una fila por cada cambio, como en la pantalla Historial
    nombre = v["nombre"]
    if v["estado"] == "Borrador":
        repo.registrar_cambio(actual["id"], nombre, "Guardada como borrador", "Borrador", usuario_id)
    elif actual["estado"] != "Publicada":
        repo.registrar_cambio(actual["id"], nombre, "Actividad publicada", "Publicada", usuario_id)
    cambios = [f"{antes[i]} retirado" for i in antes if i not in v["recursos"]]
    cambios += [f"{v['recursos'][i]} agregado" for i in v["recursos"] if i not in antes]
    for campo, etiqueta in (("nombre", "Nombre"), ("materia", "Materia"), ("grado", "Grado"), ("tipo", "Tipo")):
        if str(actual["clave_materia" if campo == "materia" else campo]) != str(v[campo]):
            cambios.append(f"{etiqueta} cambiado")
    # Se comparan los datos y no el texto: MySQL reordena los espacios del JSON al guardarlo
    contenido_antes = json.loads(actual["contenido"]) if actual["contenido"] else None
    contenido_ahora = json.loads(v["contenido"]) if v["contenido"] else None
    if contenido_antes != contenido_ahora:
        cambios.append("Contenido actualizado")
    if v["estado"] == "Publicada" and actual["estado"] == "Publicada":
        for cambio in cambios:
            repo.registrar_cambio(actual["id"], nombre, cambio, "Editada", usuario_id)
    confirmar()
    return {"id": actual["slug"], "estado": v["estado"], "antes": actual["estado"]}


def eliminar(slug, usuario_id):
    """No se borra de verdad: se marca como eliminada para conservar el historial."""
    actual = _buscar(slug)
    repo.marcar_eliminada(actual["id"])
    repo.registrar_cambio(actual["id"], actual["nombre"], "Actividad eliminada", "Eliminada", usuario_id)
    confirmar()
    return {"nombre": actual["nombre"]}


def historial():
    return [
        {
            "fecha": fecha_corta(f["fecha"]),
            "dia": f["fecha"].date().isoformat(),  # para los filtros Desde / Hasta
            "actividad": f["actividad_nombre"],
            "cambio": f["cambio"],
            "tipo": f["tipo"],
            "hecho_por": f["hecho_por"],
        }
        for f in repo.historial()
    ]

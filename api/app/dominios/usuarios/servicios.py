"""Reglas de las cuentas: solo se crean docentes, nacen pendientes y se activan con contraseña temporal."""

import csv
import io
import json

from werkzeug.security import generate_password_hash

from app.compartido.base_datos import confirmar
from app.compartido.codigos import password_temporal
from app.compartido.fechas import fecha_corta
from app.compartido.textos import iniciales
from app.compartido.validaciones import CORREO_VALIDO
from app.dominios.grupos import repositorios as grupos
from app.dominios.grupos.servicios import grupos_por_docente
from app.dominios.instituciones import repositorios as instituciones
from app.excepciones import Conflicto, ErrorDeDatos, NoEncontrado

from . import repositorios as usuarios

# Las cuentas de administrador no se crean desde el panel: solo se pueden crear docentes
MENSAJE_SOLO_DOCENTES = "Solo se pueden crear cuentas de docente. Las de administrador no se crean desde el panel."
MAX_FILAS_IMPORTACION = 1000


def usuario_json(fila, grupos_del_docente=None):
    if grupos_del_docente is None:
        grupos_del_docente = grupos_por_docente()
    return {
        "grupos": grupos_del_docente.get(fila["id"], []),  # grupos que maneja el docente
        "id": fila["id"],
        "nombre": fila["nombre"],
        "apellido": fila["apellido"],
        "nombre_completo": f"{fila['nombre']} {fila['apellido']}",
        "iniciales": iniciales(f"{fila['nombre']} {fila['apellido']}"),
        "correo": fila["correo"],
        "rol": fila["rol"],
        "institucion": fila["institucion"] or ("Todas" if fila["rol"] == "Administrador" else "Sin asignar"),
        "estado": fila["estado"],
        "ultimo_acceso": fecha_corta(fila["ultimo_acceso"]),
    }


def _buscar(usuario_id):
    fila = usuarios.obtener(usuario_id)
    if fila is None:
        raise NoEncontrado("El usuario no existe.")
    return fila


def _institucion_id(nombre, rol):
    """'Todas' (o vacío) solo vale para administradores."""
    if nombre in (None, "", "Todas"):
        if rol == "Docente":
            raise ErrorDeDatos("Un docente debe pertenecer a una institución.")
        return None
    institucion_id = instituciones.id_por_nombre(nombre)
    if institucion_id is None:
        raise ErrorDeDatos("La institución elegida no existe.")
    return institucion_id


def _validar(datos, usuario_id=None):
    """Reglas que dependen de la base: institución, correo único y grupos de esa institución."""
    valores = dict(datos, institucion_id=_institucion_id(datos["institucion"], datos["rol"]))
    if usuarios.correo_existe(valores["correo"], usuario_id or 0):
        raise Conflicto("Ya existe una cuenta con ese correo.")

    # Grupos a cargo (solo docentes). Si no vienen en la petición, no se tocan.
    if datos["grupos"] is not None:
        ids = sorted(set(datos["grupos"])) if datos["rol"] == "Docente" else []
        if ids and len(grupos.ids_de_la_institucion(valores["institucion_id"], ids)) != len(ids):
            raise ErrorDeDatos("Uno de los grupos elegidos no es de la institución del docente.")
        valores["grupos"] = ids
    return valores


def _guardar_grupos(usuario_id, ids):
    """El docente queda a cargo exactamente de estos grupos (un grupo tiene un solo docente)."""
    if ids is None:
        return
    grupos.quitar_docente(usuario_id)
    if ids:
        grupos.asignar_docente(usuario_id, ids)


def listar():
    por_docente = grupos_por_docente()
    return [usuario_json(f, por_docente) for f in usuarios.listar()]


def crear(datos):
    v = _validar(datos)
    if v["rol"] != "Docente":
        raise ErrorDeDatos(MENSAJE_SOLO_DOCENTES)
    nuevo_id = usuarios.crear(v["nombre"], v["apellido"], v["correo"], v["rol"], v["institucion_id"])
    _guardar_grupos(nuevo_id, v["grupos"])
    confirmar()
    return usuario_json(_buscar(nuevo_id))


def editar(usuario_id, datos):
    actual = _buscar(usuario_id)
    v = _validar(datos, usuario_id)
    if v["rol"] != actual["rol"]:
        raise ErrorDeDatos("El rol de una cuenta no se puede cambiar.")
    usuarios.actualizar(usuario_id, v["nombre"], v["apellido"], v["correo"], v["rol"], v["institucion_id"])
    # Un administrador o un docente que cambió de institución deja sus grupos anteriores
    if v["grupos"] is None and v["rol"] != "Docente":
        v["grupos"] = []
    _guardar_grupos(usuario_id, v["grupos"])
    confirmar()
    return usuario_json(_buscar(usuario_id))


def cambiar_estado(usuario_id, nuevo, administrador_id):
    """Activa o desactiva una cuenta. Al activar una que nunca tuvo contraseña, genera una temporal."""
    actual = _buscar(usuario_id)
    if usuario_id == administrador_id and nuevo == "Inactivo":
        raise ErrorDeDatos("No puedes desactivar tu propia cuenta.")

    temporal = None
    if nuevo == "Activo" and not actual["password_hash"]:
        temporal = password_temporal()
        usuarios.guardar_password_hash(usuario_id, generate_password_hash(temporal), guardar=False)
    usuarios.cambiar_estado(usuario_id, nuevo)
    confirmar()
    return {"usuario": usuario_json(_buscar(usuario_id)), "password_temporal": temporal}


def eliminar(usuario_id, administrador_id):
    """Borra la cuenta de un docente. Sus grupos quedan sin docente."""
    actual = _buscar(usuario_id)
    if usuario_id == administrador_id:
        raise ErrorDeDatos("No puedes eliminar tu propia cuenta.")
    if actual["rol"] != "Docente":
        raise ErrorDeDatos("Las cuentas de administrador no se eliminan desde el panel.")
    usuarios.eliminar(usuario_id)
    confirmar()
    return {"nombre": f"{actual['nombre']} {actual['apellido']}"}


def restablecer_password(usuario_id):
    """La contraseña guardada es un hash y no se puede leer: se reemplaza por una temporal nueva."""
    actual = _buscar(usuario_id)
    if actual["estado"] != "Activo":
        raise ErrorDeDatos("Activa la cuenta primero; al activarla se genera la contraseña temporal.")
    temporal = password_temporal()
    usuarios.guardar_password_hash(usuario_id, generate_password_hash(temporal))
    return {"password_temporal": temporal}


def solicitar_cuenta(datos):
    """Solicitud desde la pantalla pública: queda pendiente de aprobación."""
    if usuarios.correo_existe(datos["correo"]):
        raise Conflicto("Ya existe una cuenta con ese correo.")
    usuarios.crear(datos["nombre"], datos["apellido"], datos["correo"], "Docente", None, guardar=True)
    return "Solicitud enviada. Un administrador revisará tu cuenta."


def _leer_filas(archivo):
    """Devuelve una lista de diccionarios con nombre, apellido y correo_institucional."""
    contenido = archivo.read().decode("utf-8-sig", errors="replace")
    if archivo.filename.lower().endswith(".json"):
        try:
            datos = json.loads(contenido)
        except json.JSONDecodeError:
            raise ErrorDeDatos("El archivo JSON no es válido.") from None
        if not isinstance(datos, list) or not all(isinstance(d, dict) for d in datos):
            raise ErrorDeDatos("El JSON debe ser una lista de objetos con nombre, apellido y correo_institucional.")
        return datos

    primera = contenido.splitlines()[0] if contenido.strip() else ""
    separador = ";" if primera.count(";") > primera.count(",") else ","  # Excel en español usa ;
    filas = [f for f in csv.reader(io.StringIO(contenido), delimiter=separador) if any(c.strip() for c in f)]
    if filas and filas[0][0].strip().lower() == "nombre":
        filas = filas[1:]  # el archivo trae encabezado
    columnas = ("nombre", "apellido", "correo_institucional")
    return [dict(zip(columnas, (c.strip() for c in f), strict=False)) for f in filas]  # sobran o faltan columnas: se valida después


def importar(archivo, rol, institucion):
    """Crea muchos docentes de una vez desde un .csv o .json. Devuelve cuántos creó y cuáles omitió."""
    if archivo is None or not archivo.filename:
        raise ErrorDeDatos("Selecciona un archivo .csv o .json.")
    if not archivo.filename.lower().endswith((".csv", ".json")):
        raise ErrorDeDatos("El archivo debe ser .csv o .json.")
    rol = rol or "Docente"
    if rol != "Docente":
        raise ErrorDeDatos(MENSAJE_SOLO_DOCENTES)
    institucion_id = _institucion_id(institucion, rol)

    filas = _leer_filas(archivo)
    if not filas:
        raise ErrorDeDatos("El archivo no tiene filas para importar.")
    if len(filas) > MAX_FILAS_IMPORTACION:
        raise ErrorDeDatos(f"El archivo tiene más de {MAX_FILAS_IMPORTACION} filas.")

    creados, omitidos, vistos = 0, [], set()
    for numero, fila in enumerate(filas, start=1):
        nombre = str(fila.get("nombre") or "").strip()[:60]
        apellido = str(fila.get("apellido") or "").strip()[:60]
        correo = str(fila.get("correo_institucional") or fila.get("correo") or "").strip().lower()
        if not nombre or not apellido or not CORREO_VALIDO.match(correo) or len(correo) > 120:
            omitidos.append(f"Fila {numero}: datos incompletos o correo inválido")
        elif correo in vistos or usuarios.correo_existe(correo):
            omitidos.append(f"Fila {numero}: {correo} ya tiene cuenta")
        else:
            usuarios.crear(nombre, apellido, correo, rol, institucion_id)
            creados += 1
        vistos.add(correo)
    confirmar()
    return {"creados": creados, "omitidos": omitidos}

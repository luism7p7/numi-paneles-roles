"""Monitoreo técnico: servicios de la app, equipos, versiones, eventos e informes."""

import io
import socket
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from urllib.parse import urlsplit

from flask import Blueprint, Response, abort, current_app, jsonify, request, session
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from . import recursos
from .db import confirmar, consultar, ejecutar
from .utilidades import MESES_LARGOS, fecha_corta, slug, tamano_legible, version

bp = Blueprint("monitoreo", __name__)

# Los dos servicios del backend de la app que se vigilan: qué son y qué ruta se consulta para saber si responden.
# Ojo: se comprueba que el servidor conteste, no el estado de su base de datos.
SERVICIOS = {
    "datos": {
        "nombre": "Servidor de la app",
        "ruta": "/salud",
        "descripcion": "El servidor al que se conecta la app: recibe el progreso de los niños y entrega las actividades.",
        "afecta": "La app no puede sincronizar el progreso",
    },
    "contenido": {
        "nombre": "Contenido e IA (RAG)",
        "ruta": "/api/paquetes",
        "descripcion": "Los paquetes de conocimiento y el asistente de IA que consultan los niños.",
        "afecta": "Asistente de IA afectado",
    },
}
SEGUNDOS_ENTRE_REVISIONES = 60
DIAS_SIN_SINCRONIZAR = 7

FORMATOS_INFORME = {
    "CSV": ("csv", "text/csv"),
    "PDF": ("pdf", "application/pdf"),
    "XLSX": ("xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
}


def responde(url):
    """(funciona, detalle): si la URL contesta 200 en menos de 5 segundos y, si no, por qué."""
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            if resp.status == 200:
                return True, "Respondió correctamente"
            return False, f"Respondió con el código {resp.status}"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False, "El servidor contesta, pero no encuentra la aplicación (error 404). ¿Cambió la dirección?"
        return False, f"El servidor respondió con un error ({e.code})"
    except urllib.error.URLError as e:
        if isinstance(e.reason, (socket.timeout, TimeoutError)):
            return False, "No contestó en 5 segundos"
        return False, "No se pudo conectar con el servidor (apagado o sin internet)"
    except Exception:
        return False, "No se pudo comprobar"


def revisar_servicios(forzar=False):
    """Consulta el backend de la app (como mucho una vez por minuto) y guarda el resultado.

    Si un servicio cambia de estado se registra un evento. Sin APP_API_URL en el .env
    los servicios quedan "sin configurar" (operativo = NULL). `forzar` ignora el límite de un minuto.
    """
    base = current_app.config["APP_API_URL"]
    ahora = datetime.now()
    for s in consultar("SELECT * FROM servicios"):
        if not base:
            continue
        if not forzar and s["revisado_en"] and ahora - s["revisado_en"] < timedelta(seconds=SEGUNDOS_ENTRE_REVISIONES):
            continue
        operativo, detalle = responde(base + SERVICIOS[s["clave"]]["ruta"])
        # MySQL devuelve BOOLEAN como 0/1 (o None si nunca se revisó)
        estaba_caido = s["operativo"] is not None and not s["operativo"]
        caido_desde = None if operativo else (s["caido_desde"] or ahora)
        ejecutar(
            "UPDATE servicios SET operativo = %s, caido_desde = %s, revisado_en = %s, detalle = %s WHERE clave = %s",
            (operativo, caido_desde, ahora, detalle, s["clave"]),
            guardar=False,
        )
        nombre = SERVICIOS[s["clave"]]["nombre"]
        if not operativo and not estaba_caido:
            ejecutar("INSERT INTO eventos (nivel, mensaje) VALUES ('Crítico', %s)", (f"{nombre} sin respuesta",), guardar=False)
        elif operativo and estaba_caido:
            ejecutar("INSERT INTO eventos (nivel, mensaje) VALUES ('Info', %s)", (f"{nombre} volvió a responder",), guardar=False)
    confirmar()
    return consultar("SELECT * FROM servicios ORDER BY FIELD(clave, 'datos', 'contenido')")


def contar_sin_sincronizar():
    fila = consultar(
        """SELECT COUNT(*) AS n FROM estudiantes
           WHERE ultima_sincronizacion IS NULL OR ultima_sincronizacion < NOW() - INTERVAL %s DAY""",
        (DIAS_SIN_SINCRONIZAR,),
        uno=True,
    )
    return fila["n"]


def servicio_json(s):
    info = SERVICIOS[s["clave"]]
    base = current_app.config["APP_API_URL"]
    return {
        "clave": s["clave"],
        "nombre": info["nombre"],
        "descripcion": info["descripcion"],
        "afecta": info["afecta"],
        "operativo": None if s["operativo"] is None else bool(s["operativo"]),
        "desde": f"{s['caido_desde']:%H:%M}" if s["caido_desde"] else None,
        "desde_texto": fecha_corta(s["caido_desde"]) if s["caido_desde"] else None,
        "detalle": s.get("detalle") or ("Falta APP_API_URL en el .env: no se sabe a dónde preguntar" if not base else None),
        "revisado": fecha_corta(s["revisado_en"]) if s["revisado_en"] else None,
        # Solo el servidor (sin ruta ni claves) para que el administrador sepa qué dirección se está consultando
        "direccion": urlsplit(base).netloc if base else None,
    }


@bp.get("/api/monitoreo")
def resumen():
    servicios = revisar_servicios(forzar=request.args.get("forzar") == "1")
    versiones = recursos.versiones_en_uso()
    total_equipos = sum(versiones.values())
    minima = current_app.config["VERSION_MINIMA_ACTIVIDADES"]
    viejas = sorted((v for v in versiones if version(v) < version(minima)), key=version)
    informes = consultar(
        "SELECT id, titulo, formato, creado_en, LENGTH(contenido) AS bytes FROM informes ORDER BY creado_en DESC LIMIT 5"
    )
    eventos = consultar("SELECT nivel, mensaje, fecha FROM eventos ORDER BY fecha DESC, id DESC LIMIT 8")
    errores = consultar(
        "SELECT COUNT(*) AS n FROM eventos WHERE nivel IN ('Crítico', 'Alerta') AND fecha >= NOW() - INTERVAL 1 DAY",
        uno=True,
    )
    sin_sincronizar = contar_sin_sincronizar()
    return jsonify(
        actualizado=f"{datetime.now():%H:%M}",
        servicios=[servicio_json(s) for s in servicios],
        sin_sincronizar=sin_sincronizar,
        dias_sin_sincronizar=DIAS_SIN_SINCRONIZAR,
        errores_24h=errores["n"],
        equipos=total_equipos,
        equipos_registrados=consultar("SELECT COUNT(*) AS n FROM estudiantes", uno=True)["n"],
        versiones=[
            {"version": v, "equipos": n, "porcentaje": round(n * 100 / total_equipos) if total_equipos else 0,
             "desactualizada": version(v) < version(minima)}
            for v, n in sorted(versiones.items(), key=lambda par: version(par[0]), reverse=True)
        ],
        desactualizados={"equipos": recursos.equipos_por_debajo_de(minima, versiones),
                         "version": viejas[0] if viejas else None},
        informes=[{"id": i["id"], "titulo": i["titulo"], "formato": i["formato"], "fecha": fecha_corta(i["creado_en"]),
                   "tamano": tamano_legible(i["bytes"])} for i in informes],
        eventos=[{"nivel": e["nivel"], "mensaje": e["mensaje"], "fecha": fecha_corta(e["fecha"])} for e in eventos],
    )


# ---------- Informe de sincronización (Excel) ----------

VERDE, AMARILLO, ROJO, TURQUESA = "C6EFCE", "FFEB9C", "FFC7CE", "0D9488"
COLOR_ESTADO = {"Al día": VERDE, "Atrasado": AMARILLO, "Nunca sincronizó": ROJO}


def estado_del_equipo(atrasado, dias):
    if dias is None:
        return "Nunca sincronizó"
    return "Atrasado" if atrasado else "Al día"


def encabezado(hoja, fila, titulos):
    for columna, titulo in enumerate(titulos, start=1):
        celda = hoja.cell(row=fila, column=columna, value=titulo)
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill("solid", fgColor=TURQUESA)
        celda.alignment = Alignment(vertical="center", wrap_text=True)


def construir_excel(equipos, generado_por, minima):
    """Libro con la hoja «Resumen» (qué es y los totales) y la hoja «Equipos» (una fila por equipo)."""
    hoy = datetime.now()
    libro = Workbook()
    resumen_hoja = libro.active
    resumen_hoja.title = "Resumen"

    totales = {"Al día": 0, "Atrasado": 0, "Nunca sincronizó": 0}
    desactualizados = 0
    por_institucion = {}
    for e in equipos:
        totales[e["estado"]] += 1
        desactualizados += e["desactualizada"]
        fila = por_institucion.setdefault(e["institucion"], {"Al día": 0, "Atrasado": 0, "Nunca sincronizó": 0})
        fila[e["estado"]] += 1

    resumen_hoja["A1"] = "Informe de sincronización de equipos"
    resumen_hoja["A1"].font = Font(bold=True, size=16)
    resumen_hoja["A2"] = f"Generado el {hoy:%d/%m/%Y a las %H:%M} por {generado_por}"
    resumen_hoja["A2"].font = Font(italic=True, color="64748B")
    resumen_hoja["A4"] = "¿Qué muestra este informe?"
    resumen_hoja["A4"].font = Font(bold=True)
    resumen_hoja["A5"] = (
        "Cada equipo es el celular o la tableta de un estudiante. Un equipo «sincroniza» cuando envía su progreso al "
        f"servidor; si pasan más de {DIAS_SIN_SINCRONIZAR} días sin hacerlo, el docente ve su avance desactualizado. "
        "La hoja «Equipos» lista uno por fila, con los que más atención necesitan arriba."
    )
    resumen_hoja["A5"].alignment = Alignment(wrap_text=True, vertical="top")
    resumen_hoja.merge_cells("A5:F5")
    resumen_hoja.row_dimensions[5].height = 62

    resumen_hoja["A7"] = "Totales"
    resumen_hoja["A7"].font = Font(bold=True, size=12)
    filas = [
        ("Equipos registrados", len(equipos), None),
        (f"Al día (sincronizaron en los últimos {DIAS_SIN_SINCRONIZAR} días)", totales["Al día"], VERDE),
        (f"Atrasados (más de {DIAS_SIN_SINCRONIZAR} días sin sincronizar)", totales["Atrasado"], AMARILLO),
        ("Nunca sincronizaron", totales["Nunca sincronizó"], ROJO),
        (f"Con una versión de la app anterior a la {minima} (no reciben actividades nuevas)", desactualizados, AMARILLO),
    ]
    for n, (texto, valor, color) in enumerate(filas, start=8):
        resumen_hoja.cell(row=n, column=1, value=texto)
        celda = resumen_hoja.cell(row=n, column=2, value=valor)
        celda.font = Font(bold=True)
        celda.alignment = Alignment(horizontal="center")
        if color and valor:
            celda.fill = PatternFill("solid", fgColor=color)

    inicio = 8 + len(filas) + 1
    resumen_hoja.cell(row=inicio, column=1, value="Por institución").font = Font(bold=True, size=12)
    encabezado(resumen_hoja, inicio + 1, ["Institución", "Equipos", "Al día", "Atrasados", "Nunca sincronizaron", "% al día"])
    for n, (nombre, cuenta) in enumerate(sorted(por_institucion.items()), start=inicio + 2):
        total = sum(cuenta.values())
        valores = [nombre, total, cuenta["Al día"], cuenta["Atrasado"], cuenta["Nunca sincronizó"], cuenta["Al día"] / total]
        for columna, valor in enumerate(valores, start=1):
            celda = resumen_hoja.cell(row=n, column=columna, value=valor)
            if columna > 1:
                celda.alignment = Alignment(horizontal="center")
        resumen_hoja.cell(row=n, column=6).number_format = "0%"
    resumen_hoja.column_dimensions["A"].width = 70
    for columna in "BCDEF":
        resumen_hoja.column_dimensions[columna].width = 18

    hoja = libro.create_sheet("Equipos")
    titulos = ["Institución", "Grupo", "Estudiante", "Versión de la app", "Última sincronización",
               "Días sin sincronizar", "Estado", f"¿Versión anterior a la {minima}?"]
    encabezado(hoja, 1, titulos)
    for n, e in enumerate(equipos, start=2):
        valores = [e["institucion"], e["grupo"], e["nombre"], e["version"], e["ultima"], e["dias"], e["estado"],
                   "Sí" if e["desactualizada"] else "No"]
        for columna, valor in enumerate(valores, start=1):
            hoja.cell(row=n, column=columna, value=valor)
        hoja.cell(row=n, column=5).number_format = "dd/mm/yyyy hh:mm"
        hoja.cell(row=n, column=7).fill = PatternFill("solid", fgColor=COLOR_ESTADO[e["estado"]])
    for columna, ancho in enumerate([30, 10, 28, 18, 22, 20, 18, 24], start=1):
        hoja.column_dimensions[get_column_letter(columna)].width = ancho
    hoja.row_dimensions[1].height = 32
    hoja.freeze_panes = "A2"
    hoja.auto_filter.ref = f"A1:{get_column_letter(len(titulos))}{max(len(equipos) + 1, 2)}"

    salida = io.BytesIO()
    libro.save(salida)
    return salida.getvalue()


@bp.post("/api/informes")
def generar_informe():
    """Informe de sincronización en Excel: un resumen y una fila por equipo (estudiante)."""
    filas = consultar(
        """SELECT i.nombre AS institucion, g.grado, g.letra, e.nombre, e.version_app, e.ultima_sincronizacion,
                  DATEDIFF(NOW(), e.ultima_sincronizacion) AS dias,
                  (e.ultima_sincronizacion IS NULL OR e.ultima_sincronizacion < NOW() - INTERVAL %s DAY) AS atrasado
           FROM estudiantes e
           LEFT JOIN grupos g ON g.id = e.grupo_id
           LEFT JOIN instituciones i ON i.id = g.institucion_id
           ORDER BY i.nombre, g.grado, g.letra, e.nombre""",
        (DIAS_SIN_SINCRONIZAR,),
    )
    minima = current_app.config["VERSION_MINIMA_ACTIVIDADES"]
    equipos = [
        {
            "institucion": f["institucion"] or "Sin grupo",
            "grupo": f"{f['grado']}° {f['letra']}" if f["grado"] else "—",
            "nombre": f["nombre"],
            "version": f["version_app"] or "Sin dato",
            "ultima": f["ultima_sincronizacion"] if f["ultima_sincronizacion"] else "Nunca",
            "dias": f["dias"] if f["dias"] is not None else "—",
            "estado": estado_del_equipo(f["atrasado"], f["dias"]),
            "desactualizada": bool(f["version_app"] and version(f["version_app"]) < version(minima)),
        }
        for f in filas
    ]
    # Los que más atención necesitan, primero (conserva el orden por institución dentro de cada estado)
    prioridad = {"Nunca sincronizó": 0, "Atrasado": 1, "Al día": 2}
    equipos.sort(key=lambda e: prioridad[e["estado"]])

    usuario = consultar("SELECT nombre, apellido FROM usuarios WHERE id = %s", (session["usuario_id"],), uno=True)
    quien = f"{usuario['nombre']} {usuario['apellido']}" if usuario else "el administrador"
    hoy = datetime.now()
    titulo = f"Sincronización de equipos · {MESES_LARGOS[hoy.month - 1]} {hoy.year}"
    nuevo_id = ejecutar("INSERT INTO informes (titulo, formato, contenido) VALUES (%s, 'XLSX', %s)",
                        (titulo, construir_excel(equipos, quien, minima)))
    return jsonify(id=nuevo_id, titulo=titulo), 201


@bp.get("/api/informes/<int:informe_id>/descargar")
def descargar_informe(informe_id):
    informe = consultar("SELECT * FROM informes WHERE id = %s", (informe_id,), uno=True)
    if informe is None:
        abort(404, "El informe no existe.")
    extension, tipo = FORMATOS_INFORME[informe["formato"]]
    return Response(
        informe["contenido"],
        mimetype=tipo,
        headers={"Content-Disposition": f'attachment; filename="{slug(informe["titulo"])}.{extension}"'},
    )

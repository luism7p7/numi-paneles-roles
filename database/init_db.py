"""Crea la base de datos de Numi: tablas (schema.sql) + datos de ejemplo.

Uso, desde la raíz del proyecto:
    python database/init_db.py              # crea la base si todavía no existe
    python database/init_db.py --reiniciar  # la borra y la crea de nuevo (pierdes los datos)
"""

import argparse
import csv
import io
import os
import random
import re
from datetime import date, datetime, timedelta
from pathlib import Path

import pymysql
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

CARPETA = Path(__file__).resolve().parent
load_dotenv(CARPETA.parent / ".env")

# Contraseña de todas las cuentas activas de ejemplo (solo para desarrollo).
PASSWORD_DEMO = "Numi2026"

# (clave usada por la app, nombre, nombre corto, carpeta de recursos, orden)
MATERIAS = [
    ("matematicas", "Matemáticas", "Matemáticas", "matematicas", 1),
    ("español", "Español", "Español", "espanol", 2),
    ("ciencias", "Ciencias naturales", "Ciencias", "ciencias", 3),
    ("sociales", "Sociales", "Sociales", "sociales", 4),
    ("ingles", "Inglés", "Inglés", "ingles", 5),
]

# (nombre, comuna o corregimiento, sedes, estado)
INSTITUCIONES = [
    ("IE Rural La Aldea", "San Cristóbal", 2, "Activa"),
    ("IE Palmitas", "Palmitas", 1, "Activa"),
    ("IE Santa Elena", "Santa Elena", 3, "Activa"),
    ("IE San Antonio de Prado", "San Antonio de Prado", 2, "Activa"),
    ("IE Altavista", "Altavista", 1, "Activa"),
    ("IE El Llano", "San Cristóbal", 1, "Activa"),
    ("IE Mazo", "Santa Elena", 1, "Inactiva"),
]

# (nombre, apellido, correo, rol, institución o None si es de todas, estado, documento)
USUARIOS = [
    ("Carolina", "Vélez", "cvelez@medellin.gov.co", "Administrador", None, "Activo", "43123456"),
    ("Luisa", "Muñoz", "luisa.munoz@ielaaldea.edu.co", "Docente", "IE Rural La Aldea", "Activo", "1036654321"),
    ("Andrés", "Gaviria", "agaviria@iepalmitas.edu.co", "Docente", "IE Palmitas", "Pendiente", None),
    ("Marta", "Ríos", "mrios@iesantaelena.edu.co", "Docente", "IE Santa Elena", "Activo", "43987654"),
    ("Pedro", "Cano", "pcano@iesantaelena.edu.co", "Docente", "IE Santa Elena", "Activo", "71234987"),
    ("Jhon", "Quintero", "jquintero@iesanantonio.edu.co", "Docente", "IE San Antonio de Prado", "Inactivo", "98765432"),
    ("Sandra", "Arango", "sarango@iealtavista.edu.co", "Docente", "IE Altavista", "Pendiente", None),
    ("Felipe", "Ortiz", "fortiz@iesantaelena.edu.co", "Docente", "IE Santa Elena", "Pendiente", None),
    ("Diana", "Restrepo", "drestrepo@ielaaldea.edu.co", "Docente", "IE Rural La Aldea", "Pendiente", None),
]

# (institución, grado, letra, correo del docente o None, cantidad de estudiantes, código)
GRUPOS = [
    ("IE Rural La Aldea", 3, "A", "luisa.munoz@ielaaldea.edu.co", 24, "7K4M-92"),
    ("IE Rural La Aldea", 4, "B", "luisa.munoz@ielaaldea.edu.co", 21, "P8T2-46"),
    ("IE Rural La Aldea", 5, "A", "luisa.munoz@ielaaldea.edu.co", 19, "R5Q7-13"),
    ("IE Rural La Aldea", 5, "B", None, 17, "H3N8-25"),
    ("IE Palmitas", 2, "A", "agaviria@iepalmitas.edu.co", 18, "M6W4-81"),
    ("IE Palmitas", 4, "A", None, 15, "T9D2-37"),
    ("IE Santa Elena", 1, "A", "mrios@iesantaelena.edu.co", 22, "B7C5-64"),
    ("IE Santa Elena", 3, "B", "pcano@iesantaelena.edu.co", 20, "Y2F8-59"),
    ("IE San Antonio de Prado", 5, "A", "jquintero@iesanantonio.edu.co", 19, "K4R6-18"),
    ("IE Altavista", 2, "B", None, 16, "W8E3-72"),
    ("IE El Llano", 4, "A", None, 14, "D5J9-40"),
]

# Estudiantes con datos fijos (los del prototipo): avance objetivo por materia
# en el orden de MATERIAS, racha y estado.
ESTUDIANTES_FIJOS = {
    ("IE Rural La Aldea", 3, "A"): [
        ("Mariana Ospina", [84, 79, 71, 66, 18], 6, "Al día"),
        ("Samuel Ríos", [32, 28, 19, 22, 11], 0, "Inactivo"),
        ("Kevin Zapata", [68, 72, 64, 58, 44], 3, "Sin sincronizar"),
        ("Valentina Cano", [91, 88, 85, 80, 76], 11, "Al día"),
        ("Juan David Mesa", [55, 61, 49, 52, 38], 2, "Al día"),
        ("Sofía Restrepo", [77, 70, 73, 69, 51], 5, "Al día"),
    ],
    ("IE Rural La Aldea", 4, "B"): [
        ("Laura Betancur", [70, 68, 72, 65, 24], 4, "Al día"),
        ("Andrés Quintero", [40, 38, 36, 33, 28], 0, "Inactivo"),
        ("Emanuel Duque", [62, 60, 58, 55, 45], 2, "Sin sincronizar"),
        ("Camila Herrera", [85, 82, 80, 76, 70], 9, "Al día"),
        ("Tomás Álvarez", [58, 55, 52, 50, 44], 3, "Al día"),
    ],
    ("IE Rural La Aldea", 5, "A"): [
        ("Isabela Torres", [66, 62, 60, 58, 16], 4, "Al día"),
        ("Brayan Muñoz", [32, 30, 28, 25, 20], 0, "Inactivo"),
        ("Sara Gómez", [55, 54, 50, 48, 40], 2, "Sin sincronizar"),
        ("Mateo Arango", [78, 75, 72, 70, 64], 8, "Al día"),
        ("Daniela Ruiz", [52, 50, 49, 47, 40], 3, "Al día"),
    ],
}

NOMBRES = ["Santiago", "Valeria", "Matías", "Luciana", "Emiliano", "Salomé", "Jerónimo", "Antonella",
           "Samuel", "Isabella", "Martín", "Mariana", "Simón", "Gabriela", "Thiago", "Manuela",
           "Juan José", "Sara", "Miguel Ángel", "Daniela", "Alejandro", "Paulina", "Nicolás", "Juliana"]
APELLIDOS = ["García", "Rodríguez", "López", "Martínez", "Gómez", "Hernández", "Díaz", "Moreno",
             "Jaramillo", "Restrepo", "Vásquez", "Correa", "Londoño", "Montoya", "Zuluaga", "Henao",
             "Giraldo", "Osorio", "Arango", "Mejía", "Cardona", "Ospina", "Valencia", "Agudelo"]

# (slug, nombre EXACTO con que la app guarda el progreso, materia, grado, tipo, descripción, estado)
# Las 16 publicadas son las de la app (frontend/lib/ui/viewmodels/*_view_model.dart): las mismas
# para todos los grados, por eso todas son "desde 1°". Las 2 últimas no están en la app: son
# ejemplos de borrador y de actividad retirada para las pantallas del panel administrativo.
ACTIVIDADES = [
    ("los-numeros", "Los números", "matematicas", 1, "Arrastrar y soltar", "Reconocer del 1 al 20.", "Publicada"),
    ("quien-tiene-mas", "Quien tiene más", "matematicas", 1, "Selección múltiple", "Comparar cantidades.", "Publicada"),
    ("sumar", "Sumar", "matematicas", 1, "Arrastrar y soltar", "Sumas con objetos del entorno.", "Publicada"),
    ("palabra-loca", "Palabra loca", "español", 1, "Ordenar sílabas", "Encontrar la palabra escondida.", "Publicada"),
    ("arma-la-palabra", "Arma la palabra", "español", 1, "Ordenar sílabas", "Ordenar sílabas para formar palabras.", "Publicada"),
    ("oraciones", "Oraciones", "español", 1, "Ordenar sílabas", "Construir frases con sentido.", "Publicada"),
    ("vivo-o-no-vivo", "¿Vivo o no Vivo?", "ciencias", 1, "Arrastrar", "Clasificar seres vivos y no vivos.", "Publicada"),
    ("las-plantas", "Las plantas", "ciencias", 1, "Arrastrar y soltar", "Partes y funciones de las plantas.", "Publicada"),
    ("cuerpo-humano", "Cuerpo humano", "ciencias", 1, "Arrastrar", "Identificar las partes del cuerpo.", "Publicada"),
    ("animales", "Animales", "ciencias", 1, "Arrastrar", "Clasificar animales por su hábitat.", "Publicada"),
    ("heroes-de-la-ciudad", "Héroes de la Ciudad", "sociales", 1, "Selección múltiple", "Oficios que cuidan la ciudad.", "Publicada"),
    ("detective-de-objetos", "Detective de Objetos", "sociales", 1, "Selección múltiple", "Objetos de antes y de ahora.", "Publicada"),
    ("pasado-y-presente", "Pasado y Presente", "sociales", 1, "Memory match", "Historia de Medellín.", "Publicada"),
    ("module-1", "Module 1", "ingles", 1, "Memory match", "Vocabulario básico en parejas.", "Publicada"),
    ("module-2", "Module 2", "ingles", 1, "Comprensión auditiva", "Escuchar y elegir la palabra correcta.", "Publicada"),
    ("module-3", "Module 3", "ingles", 1, "Selección múltiple", "Tarjetas de vocabulario.", "Publicada"),
    ("los-colores", "Los colores", "ingles", 1, "Memory match", "Colores en inglés (en preparación).", "Borrador"),
    ("escucha-y-elige", "Escucha y elige", "ingles", 5, "Comprensión auditiva", "Retirada de la app.", "Desactivada"),
]

# (nombre, tipo, carpeta, emoji, versión mínima de la app o None)
RECURSOS = [
    ("perro.png", "Imagen", "actividades/ciencias", "🐶", None),
    ("arbol.png", "Imagen", "actividades/ciencias", "🌳", None),
    ("piedra.png", "Imagen", "actividades/ciencias", "🪨", None),
    ("silla.png", "Imagen", "actividades/ciencias", "🪑", None),
    ("ballena.png", "Imagen", "actividades/ciencias", "🐋", "1.4.0"),
    ("flor.png", "Imagen", "actividades/ciencias", "🌼", None),
    ("inst_vivo.mp3", "Audio", "actividades/ciencias", None, None),
    ("manzana.png", "Imagen", "actividades/matematicas", "🍎", None),
    ("globo.png", "Imagen", "actividades/matematicas", "🎈", None),
    ("banano.png", "Imagen", "actividades/matematicas", "🍌", None),
    ("balon.png", "Imagen", "actividades/matematicas", "⚽", "1.4.0"),
    ("contar.mp3", "Audio", "actividades/matematicas", None, None),
    ("casa.png", "Imagen", "actividades/espanol", "🏠", None),
    ("sol.png", "Imagen", "actividades/espanol", "☀️", None),
    ("luna.png", "Imagen", "actividades/espanol", "🌙", None),
    ("silabas.mp3", "Audio", "actividades/espanol", None, None),
    ("almohada.png", "Imagen", "actividades/sociales", "🛏️", None),
    ("tuerca.png", "Imagen", "actividades/sociales", "🔩", None),
    ("bombero.png", "Imagen", "actividades/sociales", "🚒", None),
    ("gato.png", "Imagen", "actividades/ingles", "🐱", None),
    ("cat.mp3", "Audio", "actividades/ingles", None, None),
]

# Recursos asignados a cada actividad
ACTIVIDAD_RECURSOS = {
    "los-numeros": ["manzana.png", "globo.png", "contar.mp3"],
    "quien-tiene-mas": ["banano.png", "manzana.png"],
    "animales": ["perro.png", "gato.png"],
    "las-plantas": ["arbol.png", "flor.png"],
    "arma-la-palabra": ["casa.png", "sol.png", "silabas.mp3"],
    "detective-de-objetos": ["almohada.png", "tuerca.png"],
    "module-1": ["gato.png", "cat.mp3"],
}

# (clave, nombre, desde, hasta, orden)
PERIODOS = [
    ("p1", "Periodo 1", date(2026, 1, 26), date(2026, 4, 3), 1),
    ("p2", "Periodo 2", date(2026, 4, 6), date(2026, 6, 19), 2),
    ("s1", "Semestre 1", date(2026, 1, 26), date(2026, 6, 19), 3),
    ("anio", "Año 2026", date(2026, 1, 1), date(2026, 12, 31), 4),
]

DIAS_SIN_SINCRONIZAR = {"Al día": (0, 1), "Sin sincronizar": (2, 5), "Inactivo": (8, 16)}


def conectar(base=None):
    return pymysql.connect(
        host=os.environ.get("DB_HOST", "127.0.0.1"),
        port=int(os.environ.get("DB_PORT", "3306")),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=base,
        charset="utf8mb4",
    )


def leer_sentencias(archivo):
    """Divide un .sql en sentencias, quitando los comentarios de línea (--)."""
    lineas = archivo.read_text(encoding="utf-8").splitlines()
    sin_comentarios = "\n".join(re.sub(r"--.*$", "", linea) for linea in lineas)
    return [s.strip() for s in sin_comentarios.split(";") if s.strip()]


def id_por(cur, tabla, columna, valor):
    cur.execute(f"SELECT id FROM {tabla} WHERE {columna} = %s", (valor,))
    fila = cur.fetchone()
    return fila[0] if fila else None


def insertar_catalogos(cur):
    cur.executemany("INSERT INTO materias VALUES (%s, %s, %s, %s, %s)", MATERIAS)
    cur.executemany("INSERT INTO periodos VALUES (%s, %s, %s, %s, %s)", PERIODOS)
    cur.executemany(
        "INSERT INTO instituciones (nombre, comuna, sedes, estado) VALUES (%s, %s, %s, %s)",
        INSTITUCIONES,
    )
    password_hash = generate_password_hash(PASSWORD_DEMO)
    for nombre, apellido, correo, rol, institucion, estado, documento in USUARIOS:
        cur.execute(
            """INSERT INTO usuarios (nombre, apellido, correo, password_hash, rol, institucion_id, estado,
                                     documento, ultimo_acceso)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (nombre, apellido, correo, password_hash if estado == "Activo" else None, rol,
             id_por(cur, "instituciones", "nombre", institucion), estado, documento,
             datetime.now() - timedelta(days=1, hours=3) if estado == "Activo" else None),
        )
    cur.executemany(
        "INSERT INTO recursos (nombre, tipo, carpeta, emoji, version_minima) VALUES (%s, %s, %s, %s, %s)",
        RECURSOS,
    )


def hace(dias):
    return datetime.now() - timedelta(days=dias)


def insertar_actividades(cur, admin_id):
    for i, (slug, nombre, materia, grado, tipo, descripcion, estado) in enumerate(ACTIVIDADES):
        creada = hace(200 - i * 9)
        cur.execute(
            """INSERT INTO actividades (slug, nombre, materia, grado, tipo, descripcion, estado, creada_en)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (slug, nombre, materia, grado, tipo, descripcion, estado, creada),
        )
        actividad_id = cur.lastrowid
        for recurso in ACTIVIDAD_RECURSOS.get(slug, []):
            cur.execute(
                "INSERT INTO actividad_recurso VALUES (%s, (SELECT id FROM recursos WHERE nombre = %s))",
                (actividad_id, recurso),
            )
        historial = [("Publicada" if estado != "Borrador" else "Borrador",
                      "Actividad publicada" if estado != "Borrador" else "Guardada como borrador", creada)]
        if estado == "Desactivada":
            historial.append(("Desactivada", "Actividad desactivada", hace(130)))
        if slug in ("las-plantas", "arma-la-palabra"):
            historial.append(("Editada", f"{ACTIVIDAD_RECURSOS[slug][0]} agregado", hace(3)))
        for tipo_cambio, cambio, fecha in historial:
            cur.execute(
                """INSERT INTO historial (actividad_id, actividad_nombre, cambio, tipo, usuario_id, fecha)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (actividad_id, nombre, cambio, tipo_cambio, admin_id, fecha),
            )


def insertar_grupos_y_estudiantes(cur, azar):
    hoy = date.today()
    cur.execute("SELECT nombre, materia FROM actividades WHERE estado = 'Publicada'")
    publicadas = cur.fetchall()
    materias = [m[0] for m in MATERIAS]
    contador_uid = 0

    for institucion, grado, letra, docente, cantidad, codigo in GRUPOS:
        cur.execute(
            """INSERT INTO grupos (institucion_id, grado, letra, docente_id, codigo, codigo_vence,
                                   codigo_usos, paquete_actualizado)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (id_por(cur, "instituciones", "nombre", institucion), grado, letra,
             id_por(cur, "usuarios", "correo", docente), codigo, hoy + timedelta(days=22),
             cantidad, hoy - timedelta(days=73)),  # cada estudiante usó el código una vez
        )
        grupo_id = cur.lastrowid

        fijos = ESTUDIANTES_FIJOS.get((institucion, grado, letra), [])
        alumnos = list(fijos)
        while len(alumnos) < cantidad:
            nivel = azar.randint(35, 88)
            objetivo = [max(5, min(98, nivel + azar.randint(-12, 12))) for _ in materias]
            objetivo[4] = max(5, objetivo[4] - 18)  # inglés suele ir más atrás
            estado = azar.choices(["Al día", "Sin sincronizar", "Inactivo"], [75, 12, 13])[0]
            nombre = f"{azar.choice(NOMBRES)} {azar.choice(APELLIDOS)}"
            racha = 0 if estado == "Inactivo" else azar.randint(1, 12)
            alumnos.append((nombre, objetivo, racha, estado))

        for nombre, objetivo, racha, estado in alumnos:
            contador_uid += 1
            dias = azar.randint(*DIAS_SIN_SINCRONIZAR[estado])
            sincronizado = datetime.now() - timedelta(days=dias, hours=azar.randint(0, 8))
            version = azar.choices(["1.4.0", "1.3.2", "1.1.0"], [74, 19, 7])[0]
            cur.execute(
                """INSERT INTO estudiantes (uid, nombre, grupo_id, racha_dias, version_app, ultima_sincronizacion)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (f"demo-uid-{contador_uid:04d}", nombre, grupo_id, racha, version, sincronizado),
            )
            estudiante_id = cur.lastrowid
            insertar_progreso(cur, azar, estudiante_id, grado, objetivo, publicadas, materias, sincronizado)
            for materia in azar.sample(materias, 2):
                nivel = objetivo[materias.index(materia)]
                correctas = max(0, min(10, round(nivel / 10) + azar.randint(-1, 1)))
                cur.execute(
                    "INSERT INTO evaluaciones (estudiante_id, materia, correctas, total, fecha) VALUES (%s, %s, %s, 10, %s)",
                    (estudiante_id, materia, correctas, sincronizado - timedelta(days=azar.randint(1, 60))),
                )


def insertar_progreso(cur, azar, estudiante_id, grado, objetivo, publicadas, materias, hasta):
    desde = datetime(2026, 2, 2)
    rango = max(1, int((hasta - desde).total_seconds()))
    for nombre, materia in publicadas:  # las mismas actividades para cualquier grado
        porcentaje = objetivo[materias.index(materia)] + azar.randint(-18, 18)
        if porcentaje < 8:
            continue  # "Sin empezar": la app no guarda nada
        porcentaje = 100 if porcentaje > 92 else porcentaje
        cur.execute(
            """INSERT INTO progreso (estudiante_id, grado, materia, actividad, porcentaje, intentos, ultima_vez)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (estudiante_id, grado, materia, nombre, porcentaje, azar.randint(1, 6) + (4 if porcentaje == 100 else 0),
             desde + timedelta(seconds=azar.randint(0, rango))),
        )


def insertar_monitoreo(cur):
    ahora = datetime.now()
    cur.executemany(
        "INSERT INTO servicios (clave, nombre) VALUES (%s, %s)",
        [("datos", "Backend de datos de la app"), ("contenido", "RAG API")],
    )
    cur.executemany(
        "INSERT INTO eventos (nivel, mensaje, fecha) VALUES (%s, %s, %s)",
        [
            ("Info", "Paquete de conocimiento v2.1 publicado", ahora - timedelta(hours=5)),
            ("Alerta", "Conflicto de progreso resuelto por mayor avance", ahora - timedelta(hours=3, minutes=40)),
            ("Alerta", "Descarga de Gemma 2B fallida · 9 equipos", ahora - timedelta(hours=2, minutes=10)),
        ],
    )
    # Un informe de ejemplo con datos reales de la base recién creada
    cur.execute(
        """SELECT g.grado, COUNT(DISTINCT e.id), COALESCE(SUM(p.intentos), 0)
           FROM grupos g JOIN estudiantes e ON e.grupo_id = g.id
           LEFT JOIN progreso p ON p.estudiante_id = e.id
           GROUP BY g.grado ORDER BY g.grado"""
    )
    salida = io.StringIO()
    escritor = csv.writer(salida)
    escritor.writerow(["grado", "estudiantes", "actividades_resueltas"])
    escritor.writerows(cur.fetchall())
    cur.execute(
        "INSERT INTO informes (titulo, formato, contenido, creado_en) VALUES (%s, 'CSV', %s, %s)",
        ("Uso por grado · septiembre 2026", salida.getvalue().encode("utf-8"), ahora - timedelta(days=24)),
    )


def insertar_datos(cur):
    azar = random.Random(2026)  # misma semilla = mismos datos cada vez
    insertar_catalogos(cur)
    insertar_actividades(cur, id_por(cur, "usuarios", "correo", "cvelez@medellin.gov.co"))
    insertar_grupos_y_estudiantes(cur, azar)
    # Ejemplo: en 4° B la docente desactivó "Module 3" para el grupo
    cur.execute(
        """INSERT INTO grupo_actividad
           SELECT g.id, a.id, FALSE FROM grupos g, actividades a
           WHERE g.codigo = 'P8T2-46' AND a.slug = 'module-3'"""
    )
    insertar_monitoreo(cur)


def crear_base(nombre, reiniciar=False):
    # El nombre de una base no se puede pasar como parámetro (%s), así que se valida aquí.
    if not re.fullmatch(r"[A-Za-z0-9_]+", nombre):
        raise ValueError(f"Nombre de base de datos no válido: {nombre!r}")

    con = conectar()
    try:
        with con.cursor() as cur:
            cur.execute("SELECT 1 FROM information_schema.schemata WHERE schema_name = %s", (nombre,))
            if cur.fetchone():
                if not reiniciar:
                    raise RuntimeError(f"La base `{nombre}` ya existe. Usa --reiniciar para borrarla y crearla de nuevo.")
                cur.execute(f"DROP DATABASE `{nombre}`")
            cur.execute(f"CREATE DATABASE `{nombre}` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci")
            cur.execute(f"USE `{nombre}`")
            for sentencia in leer_sentencias(CARPETA / "schema.sql"):
                cur.execute(sentencia)
            insertar_datos(cur)
        con.commit()
    finally:
        con.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crea la base de datos de los paneles de Numi.")
    parser.add_argument("--reiniciar", action="store_true", help="borra la base si ya existe")
    args = parser.parse_args()
    nombre = os.environ.get("DB_NAME", "numi")
    try:
        crear_base(nombre, args.reiniciar)
    except RuntimeError as error:
        raise SystemExit(str(error))
    print(f"Base `{nombre}` lista.")
    print(f"  Panel administrativo: cvelez@medellin.gov.co / {PASSWORD_DEMO}")
    print(f"  Panel docente:        luisa.munoz@ielaaldea.edu.co / {PASSWORD_DEMO}")

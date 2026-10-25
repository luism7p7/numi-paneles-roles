# Numi · Paneles administrativo y docente

Paneles web de **Numi**, la app educativa para niños de 1° a 5° de las instituciones rurales de Medellín
([repositorio de la app](https://github.com/geminitodo5-sketch/app-educativa-medellin)).

- **Panel administrativo** (puerto 5000): actividades y borradores, constructor, recursos, instituciones,
  usuarios y monitoreo técnico.
- **Panel docente** (puerto 5001): avance del grupo, estudiantes, actividades por grupo, reportes en
  Excel/PDF y código del grupo.

## Tecnologías

| Capa | Tecnología |
|------|------------|
| Backend | Python 3 + Flask 3 (un servidor por panel) |
| Base de datos | MySQL 8 con PyMySQL y SQL escrito a mano |
| Front-end | HTML, Bootstrap 5 y JavaScript (`fetch` a la API de Flask) |
| Archivos | openpyxl (Excel) y fpdf2 (PDF) |
| Pruebas | pytest (63 pruebas) |

## Cómo funciona

```
Navegador ──► Flask (panel-administrativo, :5000) ──┐
          ──► Flask (panel-docente, :5001) ─────────┼──► MySQL `numi` (una base para los dos)
                                                    │
Backend de la app (FastAPI) ──► /api/app/v1/... ────┘   (puente con la app, con clave)
Panel administrativo ──► APP_API_URL /salud y /api/paquetes (monitoreo)
```

- El front-end (HTML y CSS) es el original, **sin cambios**. Flask sirve esos mismos archivos y
  `js/app.js` pide los datos a la API (`/api/...`) en lugar de usar datos fijos.
- Cada panel protege sus páginas con sesión. "Cerrar sesión" lleva a `index.html`, y abrir esa
  página cierra la sesión.
- La tabla `progreso` tiene la misma forma que el progreso de la app (`grado`, `materia`, `actividad`,
  `porcentaje`, `intentos`, `ultima_vez`) y la misma regla: **gana el mayor avance**.

## Estructura

```
├── database/
│   ├── schema.sql              # 16 tablas (las comparten los dos paneles)
│   └── init_db.py              # crea la base y carga datos de ejemplo
├── panel-administrativo/
│   ├── *.html, css/, js/, img/ # front-end original
│   ├── app.py                  # python app.py → http://localhost:5000
│   ├── servidor_admin/         # auth, inicio, actividades, recursos, instituciones, usuarios, monitoreo
│   └── tests/
├── panel-docente/
│   ├── *.html, css/, js/, img/ # front-end original
│   ├── app.py                  # python app.py → http://localhost:5001
│   ├── servidor_docente/       # auth, seguimiento, reportes, gestion, puente_app
│   └── tests/
├── requirements.txt
└── .env.example
```

## Cómo ejecutarlo (Windows / PowerShell)

```powershell
# 1. Entorno virtual y dependencias (desde la raíz del proyecto)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Configuración: copia la plantilla y escribe tu contraseña de MySQL en DB_PASSWORD
Copy-Item .env.example .env

# 3. Crear la base de datos `numi` con datos de ejemplo
python database/init_db.py              # --reiniciar para borrarla y crearla de nuevo

# 4. Cada panel en su propia terminal
cd panel-administrativo; python app.py  # http://localhost:5000
cd panel-docente;        python app.py  # http://localhost:5001
```

> Abre los paneles con la URL de Flask (`http://localhost:5000`), **no** con Live Server: Live Server
> solo muestra el HTML y no tiene la API, así que los datos no cargan.
>
> En VS Code elige el intérprete del proyecto: `Ctrl+Shift+P` → *Python: Select Interpreter* → `.venv`.

Cuentas de ejemplo (contraseña `Numi2026`):

| Correo | Rol | Panel |
|--------|-----|-------|
| cvelez@medellin.gov.co | Administrador | Administrativo |
| luisa.munoz@ielaaldea.edu.co | Docente (3° A, 4° B y 5° A) | Docente |

## Servicios de la API

**Panel administrativo**

| Pantalla | Endpoints |
|----------|-----------|
| Login / Crear usuario | `POST /api/login`, `POST /api/registro` |
| Inicio | `GET /api/inicio` |
| Actividades, detalle, borradores | `GET /api/actividades`, `GET/PUT/DELETE /api/actividades/<id>` |
| Constructor | `POST /api/actividades` (Publicada o Borrador), `GET /api/recursos` |
| Historial | `GET /api/historial` |
| Recursos | `GET /api/recursos`, `POST /api/recursos` (subir PNG/JPG/MP3) |
| Instituciones | `GET/POST /api/instituciones`, `GET /api/instituciones/<id>` |
| Usuarios | `GET/POST /api/usuarios`, `PUT /api/usuarios/<id>`, `PATCH /api/usuarios/<id>/estado`, `POST /api/usuarios/importar` |
| Monitoreo técnico | `GET /api/monitoreo`, `POST /api/informes`, `GET /api/informes/<id>/descargar` |

**Panel docente**

| Pantalla | Endpoints |
|----------|-----------|
| Login, perfil, Mis datos | `POST /api/login`, `GET /api/me`, `POST /api/grupo-activo` |
| Panel | `GET /api/panel` |
| Estudiantes | `GET /api/estudiantes`, `GET /api/estudiantes/<id>`, `PUT /api/estudiantes/<id>/nota`, `GET /api/estudiantes/exportar`, `GET /api/estudiantes/<id>/informe` |
| Actividades | `GET /api/actividades`, `PATCH /api/actividades/<id>` |
| Reportes | `GET /api/reportes?periodo=`, `GET /api/reportes/descargar` |
| Gestión | `GET /api/gestion`, `POST /api/gestion/codigo`, `PATCH /api/gestion/ia`, `POST /api/gestion/paquete` |

**Puente con la app** (cabecera `X-Api-Key: <APP_API_KEY>`, lo llama el backend de la app, nunca el celular)

| Método | URL | Qué hace |
|--------|-----|----------|
| POST | `/api/app/v1/unirse` | `{uid, nombre, codigo}`: el niño entra al grupo con el código del docente |
| GET | `/api/app/v1/actividades?uid=` | Actividades publicadas y activas para el grupo del niño |
| PUT | `/api/app/v1/progreso` | `{uid, version_app, racha_dias, items[]}`: mismo formato que `/api/v1/me/progreso` de la app |

## Pruebas

```powershell
python -m pytest        # desde la raíz: corre las pruebas de los dos paneles
```

Usan una base aparte (`numi_test`) que se crea de nuevo en cada archivo de pruebas, así que no tocan tus datos.

## Capturas

_Pendiente: agrega aquí capturas del panel administrativo y del panel docente con datos reales._

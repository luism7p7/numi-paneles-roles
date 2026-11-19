# Numi · API y paneles administrativo y docente

Paneles web de **Numi**, la app educativa para niños de 1° a 5° de las instituciones rurales de Medellín
([repositorio de la app](https://github.com/geminitodo5-sketch/app-educativa-medellin)).

- **Panel administrativo** (http://localhost:5173): actividades y borradores, constructor, recursos,
  instituciones, usuarios y monitoreo técnico.
- **Panel docente** (http://localhost:5174): avance del grupo, estudiantes, actividades por grupo, reportes en
  Excel/PDF y código del grupo.
- **API** (http://localhost:5001/api/v1): un solo backend que usan los dos paneles y la app del celular.

## Repositorios del proyecto

Numi se entrega en dos repositorios públicos que trabajan juntos:

| Parte | Repositorio | Carpeta |
| :-- | :-- | :-- |
| **Frontend web**: panel administrativo y panel docente | [numi-paneles-roles](https://github.com/luism7p7/numi-paneles-roles) (este) | `frontend-admin/` y `frontend-docente/` |
| **Backend web**: API de los paneles (Flask + MySQL) | [numi-paneles-roles](https://github.com/luism7p7/numi-paneles-roles) (este) | `api/` |
| **Frontend móvil**: app del estudiante (Flutter) | [app-educativa-medellin](https://github.com/geminitodo5-sketch/app-educativa-medellin) | `frontend/` |
| **Backend de la app** (FastAPI) | [app-educativa-medellin](https://github.com/geminitodo5-sketch/app-educativa-medellin) | `backend/` |

El celular habla con el backend de la app, y este con la API de los paneles (ver «Conectar con la app del celular»).

## Tecnologías

| Capa | Tecnología |
|------|------------|
| API | Python 3 + Flask 3, organizada por dominios (controladores, servicios, repositorios y DTOs) |
| Validación | Marshmallow (los DTOs) |
| Sesión | Tokens JWT (PyJWT) con roles `Administrador` y `Docente` |
| Base de datos | MySQL 8 con PyMySQL y SQL escrito a mano |
| Paneles | Dos SPAs con Vite, Bootstrap 5 y JavaScript (`fetch` a la API) |
| Archivos | openpyxl (Excel) y fpdf2 (PDF) |
| Pruebas | pytest (126 pruebas) |
| Calidad | ruff (`python -m ruff check .`) |

## Cómo funciona

```
Navegador ──► frontend-admin   (Vite, :5173) ──┐
Navegador ──► frontend-docente (Vite, :5174) ──┼──► API Flask (:5001, /api/v1) ──► MySQL `numi`
                                               │         ▲
Backend de la app (FastAPI) ──► /api/app/v1/... ─────────┘   (puente con la app, con clave)
API ──► APP_API_URL /salud y /api/paquetes (monitoreo y paquete de contenido)
```

- Cada panel es una página (`index.html`) que dibuja sus pantallas con JavaScript y pide los datos a la API.
  Todo lo que sale hacia la API pasa por un solo archivo (`src/js/api/http.js`).
- El inicio de sesión devuelve un **token JWT**; el panel lo guarda y lo envía en cada pedido
  (`Authorization: Bearer <token>`). La API revisa el rol: lo de `/admin/...` es solo del administrador y lo de
  `/docente/...` solo del docente.
- Las respuestas siguen siempre el mismo formato: `{"success": true, "data": ...}` o
  `{"success": false, "error": {"message": "...", "details": ...}}`. El puente con la app es la excepción: es un
  contrato propio y responde JSON sin envoltorio.
- La tabla `progreso` tiene la misma forma que el progreso de la app (`grado`, `materia`, `actividad`,
  `porcentaje`, `intentos`, `ultima_vez`) y la misma regla: **gana el mayor avance**.

### Cómo está organizada la API

Cada tema (usuarios, actividades, recursos…) es un **dominio** con sus propias capas, y cada capa hace una sola cosa:

```
controladores.py   las rutas: reciben la petición y responden
dtos.py            validan lo que llega (Marshmallow)
servicios.py       las reglas de negocio
repositorios.py    el SQL: lo único que habla con la base de datos
```

Una petición recorre siempre el mismo camino: **controlador → DTO → servicio → repositorio → MySQL**.

## Estructura

```
├── api/
│   ├── app.py                       # python app.py → http://localhost:5001
│   ├── app/
│   │   ├── __init__.py              # crear_app(): une los dominios y los manejadores de error
│   │   ├── config.py                # lee el .env
│   │   ├── seguridad.py             # JWT: requiere_admin y requiere_docente
│   │   ├── respuestas.py            # formato {success, data} / {success, error}
│   │   ├── excepciones.py           # errores de negocio (400, 401, 403, 404, 409)
│   │   ├── compartido/              # base de datos, textos, fechas, códigos, validaciones, Excel y PDF
│   │   ├── integraciones/           # lo único que se le pide al backend de la app (backend_app.py)
│   │   └── dominios/
│   │       ├── autenticacion/       # login y solicitud de cuenta
│   │       ├── usuarios/            # cuentas, estados, contraseñas temporales, importación
│   │       ├── instituciones/       # instituciones y creación de grupos
│   │       ├── grupos/              # grupos, código de ingreso y grupo activo del docente
│   │       ├── actividades/         # catálogo, constructor, plantillas, historial
│   │       ├── recursos/            # imágenes, audios y videos
│   │       ├── inicio/, monitoreo/  # resumen del administrador, servicios de la app e informes
│   │       ├── docente/             # perfil del docente y cambio de grupo
│   │       ├── seguimiento/         # panel, estudiantes, fichas y actividades por grupo
│   │       ├── reportes/, gestion/  # reportes por periodo, código del grupo, asistente de IA
│   │       └── puente_app/          # lo que consume el backend de la app (/api/app/v1)
│   ├── tests/                       # pruebas (admin/, docente/ y el contrato de la API)
│   ├── uploads/                     # archivos subidos (no se sube a git)
│   └── requirements.txt
├── frontend-admin/                  # panel administrativo (Vite)
├── frontend-docente/                # panel docente (Vite)
│   └── src/js/
│       ├── api/                     # un archivo por recurso; http.js es el único cliente
│       ├── auth/                    # token y sesión
│       ├── router/                  # rutas y guards
│       ├── components/              # barra lateral, selector de recursos, editor de contenido…
│       ├── pages/                   # una pantalla por archivo (HTML + lo que hace)
│       └── utils/
├── database/
│   ├── schema.sql                   # 16 tablas
│   ├── init_db.py                   # crea la base y carga datos de ejemplo (--migrar actualiza una existente)
│   └── importar_recursos_app.py     # trae las imágenes y audios de la app
├── ruff.toml, pytest.ini
└── .env.example
```

## Cómo ejecutarlo (Windows / PowerShell)

```powershell
# 1. API: entorno virtual y dependencias (desde la raíz del proyecto)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r api/requirements.txt

# 2. Configuración: copia la plantilla y completa tus datos (ver «Configuración» más abajo)
Copy-Item .env.example .env

# 3. Crear la base de datos `numi` con datos de ejemplo
python database/init_db.py              # --reiniciar para borrarla y crearla de nuevo
                                        # --migrar para actualizar una base que ya tenías, sin borrar nada

# 4. Cada parte en su propia terminal
cd api;               python app.py     # API        → http://localhost:5001/api/v1/salud
cd frontend-admin;    npm install; npm run dev   # Administrativo → http://localhost:5173
cd frontend-docente;  npm install; npm run dev   # Docente        → http://localhost:5174
```

> Los paneles necesitan **Node.js** (para Vite) y la API encendida. Si la API está en otra dirección, crea un
> `.env` dentro de cada frontend con `VITE_API_URL=http://<dirección>/api/v1` (ver `.env.example` de cada uno).
>
> En VS Code elige el intérprete del proyecto: `Ctrl+Shift+P` → *Python: Select Interpreter* → `.venv`.

Cuentas de ejemplo (contraseña `Numi2026`):

| Correo | Rol | Panel |
|--------|-----|-------|
| cvelez@medellin.gov.co | Administrador | Administrativo |
| luisa.munoz@ielaaldea.edu.co | Docente (3° A, 4° B y 5° A) | Docente |

## Configuración (`.env`, en la raíz)

| Variable | Para qué sirve |
|----------|----------------|
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` | Conexión a MySQL. |
| `SECRET_KEY` | Firma los tokens de inicio de sesión (también se acepta `ADMIN_SECRET_KEY`, el nombre anterior). |
| `JWT_EXP_MINUTES` | Cuánto dura una sesión (por defecto 480 minutos). |
| `CORS_ALLOWED_ORIGINS` | Direcciones de los paneles que pueden llamar a la API. Vacío = `localhost` y `127.0.0.1` en los puertos 5173 y 5174. |
| `APP_API_URL` | Dirección del backend de la app (por ejemplo `http://127.0.0.1:8000`). El monitoreo comprueba `/salud` y `/api/paquetes`. |
| `APP_API_KEY` | Clave del puente con la app. Tiene que ser **la misma** que `PANEL_API_KEY` en el `.env` del backend de la app; vacía, el puente queda apagado y las actividades no llegan al celular. |
| `UPLOADS_DIR` | Carpeta de los archivos subidos (por defecto `api/uploads`). |

Si cambias el `.env`, reinicia la API: solo se lee al arrancar.

## Conectar con la app del celular

1. En el backend de la app: `PANEL_API_URL=http://127.0.0.1:5001` (la API) y `PANEL_API_KEY` igual a `APP_API_KEY`.
2. El niño entra a un grupo con el código del docente (Configuración → «Unirme a un grupo»).
3. Una actividad publicada llega a los grupos **del grado que se eligió al crearla**; las pantallas que ya trae
   la app valen para todos los grados. El docente puede desactivar cada actividad en su grupo.
4. La app se sincroniza al abrir el menú, al tocar «Volver» y con los botones del menú (no al tocar una actividad).

## Rutas de la API

Todas empiezan por `/api/v1` y piden `Authorization: Bearer <token>`, salvo el acceso y los archivos subidos.

**Acceso y archivos**

| Método | Ruta | Qué hace |
|--------|------|----------|
| POST | `/auth/login` | `{correo, password, rol}` → token. Cada panel entra con su rol |
| POST | `/auth/registro` | Solicitud de cuenta: queda pendiente hasta que un administrador la apruebe |
| GET | `/archivos/<ruta>` | Imágenes y audios subidos (públicos: `<img>` y `<audio>` no pueden enviar el token) |
| GET | `/salud` | La API responde |

**Administrador** (`/admin/...`)

| Pantalla | Rutas |
|----------|-------|
| Inicio | `GET /admin/inicio` |
| Actividades, detalle, borradores | `GET /admin/actividades`, `GET/PUT/DELETE /admin/actividades/<id>` |
| Constructor | `POST /admin/actividades` (Publicada o Borrador), `GET /admin/recursos` |
| Historial | `GET /admin/historial` |
| Recursos | `GET /admin/recursos`, `POST /admin/recursos` (subir PNG/JPG/MP3/MP4) |
| Instituciones | `GET/POST /admin/instituciones`, `GET /admin/instituciones/<id>`, `POST /admin/instituciones/<id>/grupos` |
| Usuarios | `GET/POST /admin/usuarios`, `PUT /admin/usuarios/<id>`, `DELETE /admin/usuarios/<id>`, `PATCH /admin/usuarios/<id>/estado`, `POST /admin/usuarios/<id>/password-temporal`, `POST /admin/usuarios/importar` |
| Monitoreo técnico | `GET /admin/monitoreo`, `POST /admin/informes`, `GET /admin/informes/<id>/descargar` |

**Docente** (`/docente/...`; el grupo con el que trabaja viaja en la cabecera `X-Grupo-Id`)

| Pantalla | Rutas |
|----------|-------|
| Perfil, Mis datos | `GET /docente/me`, `POST /docente/grupo-activo` |
| Panel | `GET /docente/panel` |
| Estudiantes | `GET /docente/estudiantes`, `GET /docente/estudiantes/<id>`, `PUT /docente/estudiantes/<id>/nota`, `GET /docente/estudiantes/exportar`, `GET /docente/estudiantes/<id>/informe` |
| Actividades | `GET /docente/actividades`, `PATCH /docente/actividades/<id>` |
| Reportes | `GET /docente/reportes?periodo=`, `GET /docente/reportes/descargar` |
| Gestión | `GET /docente/gestion`, `POST /docente/gestion/codigo`, `PATCH /docente/gestion/ia`, `POST /docente/gestion/paquete` |

Reportes abre en el periodo que contiene la fecha de hoy; los periodos (cuatro periodos, dos semestres y el
año) están en la tabla `periodos`.

**Puente con la app** (`/api/app/v1`, cabecera `X-Api-Key: <APP_API_KEY>`, lo llama el backend de la app, nunca el celular)

| Método | URL | Qué hace |
|--------|-----|----------|
| POST | `/api/app/v1/unirse` | `{uid, nombre, codigo}`: el niño entra al grupo con el código del docente |
| GET | `/api/app/v1/actividades?uid=` | Actividades publicadas y activas para el grupo del niño |
| GET | `/api/app/v1/recursos/<id>` | Archivo de una imagen, audio o video de una actividad |
| PUT | `/api/app/v1/progreso` | `{uid, version_app, racha_dias, items[]}`: mismo formato que `/api/v1/me/progreso` de la app |

## Tipos de actividad que se arman en el panel

El constructor crea actividades de seis tipos. La app las juega con una plantilla de su tipo, sin
programar pantallas nuevas (el formato de cada contenido está en `api/app/dominios/actividades/plantillas.py`):

| Tipo | El niño... | Contenido |
|------|-----------|-----------|
| Selección múltiple | elige la respuesta correcta | `preguntas` |
| Comprensión auditiva | escucha un audio y elige la respuesta | `preguntas` (cada una con audio) |
| Arrastrar | arrastra cada elemento al grupo al que pertenece | `grupos` + `elementos` |
| Arrastrar y soltar | arrastra cada elemento hasta su pareja | `parejas` |
| Ordenar sílabas | ordena las sílabas de una palabra | `palabras` |
| Memory match | encuentra los pares de cartas | `pares` |

Un borrador puede estar incompleto; para publicar, el contenido se valida completo (por ejemplo, en «Arrastrar»
dos grupos no pueden llamarse igual). Las imágenes y audios se eligen con un buscador que abarca todo el catálogo.

## Usuarios

Desde el panel solo se crean (a mano o importando un archivo) cuentas de **docente**. Las de administrador no se
crean desde el panel y el rol de una cuenta no se puede cambiar.

## Recursos de la app

Las imágenes y audios del constructor son los de la app. `api/uploads/` no se sube a git, así que en un equipo
nuevo hay que importarlos (se puede repetir sin duplicar):

```powershell
.\.venv\Scripts\python.exe database/importar_recursos_app.py   # lee ~/Documents/app-educativa-medellin/frontend
.\.venv\Scripts\python.exe database/importar_recursos_app.py --app "C:/ruta/a/app-educativa-medellin/frontend"
```

## Pruebas y calidad del código

```powershell
python -m pytest        # desde la raíz: corre las pruebas de la API
python -m ruff check .  # errores, código sin usar e imports (pip install ruff)
```

Las pruebas usan una base aparte (`numi_test`) que se crea de nuevo en cada archivo de pruebas, así que no tocan
tus datos. Hay pruebas de cada pantalla (`api/tests/admin`, `api/tests/docente`) y del contrato de la API
(`api/tests/test_contrato_api.py`: formato de respuestas, tokens, roles, grupo activo y CORS).

## Equipo

Proyecto hecho en equipo como parte de Numi, la aplicación educativa offline para niños de zonas rurales.

| Integrante | Enlaces |
| :-- | :-- |
| **Luis Miguel Muñoz Rendón** | [GitHub](https://github.com/luism7p7) · [Portafolio](https://luism7p7.github.io) |
| **Alexander Mejía Ospina** | [GitHub](https://github.com/AlexanderM-Code) · [Portafolio](https://alexanderm-code.github.io) |
| **Santiago Mayorga Hueso** | [GitHub](https://github.com/qxsantx) |
| **Santiago Rodríguez** | |

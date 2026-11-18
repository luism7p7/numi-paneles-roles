"""Configuración de la API, leída de variables de entorno (.env)."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Carpeta `api/` y raíz del proyecto (donde vive el .env)
CARPETA_API = Path(__file__).resolve().parent.parent
RAIZ = CARPETA_API.parent

load_dotenv(RAIZ / ".env")


def _lista(valor, por_defecto):
    items = [o.strip() for o in (valor or "").split(",") if o.strip()]
    return items or por_defecto


class Config:
    # Clave con la que se firman los tokens JWT. Se aceptan los nombres del .env anterior.
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.environ.get("ADMIN_SECRET_KEY") or "solo-para-desarrollo"
    JWT_EXP_MINUTES = int(os.environ.get("JWT_EXP_MINUTES", "480"))

    DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.environ.get("DB_PORT", "3306"))
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_NAME = os.environ.get("DB_NAME", "numi")

    # Los dos frontends (admin y docente) viven en otros puertos: se permiten sus orígenes
    CORS_ALLOWED_ORIGINS = _lista(
        os.environ.get("CORS_ALLOWED_ORIGINS"),
        [f"http://{host}:{puerto}" for host in ("localhost", "127.0.0.1") for puerto in (5173, 5174)],
    )

    # Backend de la app Numi (FastAPI): de aquí sale el estado de los servicios y la versión del paquete
    APP_API_URL = os.environ.get("APP_API_URL", "").rstrip("/")
    # Clave que debe enviar el backend de la app para usar /api/app/v1/...
    APP_API_KEY = os.environ.get("APP_API_KEY", "")

    # Imágenes, audios y videos que sube o importa el administrador (se los entrega a la app)
    CARPETA_UPLOADS = Path(os.environ.get("UPLOADS_DIR") or CARPETA_API / "uploads")
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB por envío

    # Los equipos con una versión anterior a esta no reciben actividades nuevas
    VERSION_MINIMA_ACTIVIDADES = "1.2.0"

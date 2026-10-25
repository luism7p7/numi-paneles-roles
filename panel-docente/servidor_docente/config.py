"""Configuración del panel docente, leída de variables de entorno (.env)."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Carpeta del panel (donde están los .html, css/, js/ e img/)
CARPETA_PANEL = Path(__file__).resolve().parent.parent

# El .env está en la raíz del proyecto y lo comparten los dos paneles.
load_dotenv(CARPETA_PANEL.parent / ".env")


class Config:
    SECRET_KEY = os.environ.get("DOCENTE_SECRET_KEY") or "solo-para-desarrollo-docente"

    # Cookie distinta a la del panel administrativo (ver servidor_admin/config.py)
    SESSION_COOKIE_NAME = "numi_docente_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.environ.get("DB_PORT", "3306"))
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_NAME = os.environ.get("DB_NAME", "numi")

    # Backend de la app Numi: de aquí sale la versión del paquete de conocimiento
    APP_API_URL = os.environ.get("APP_API_URL", "").rstrip("/")
    # Clave que debe enviar el backend de la app para usar /api/app/v1/...
    APP_API_KEY = os.environ.get("APP_API_KEY", "")

    # Imágenes, audios y videos que sube o importa el panel administrativo (se los entrega a la app)
    CARPETA_UPLOADS = Path(os.environ.get("UPLOADS_DIR") or CARPETA_PANEL.parent / "panel-administrativo" / "uploads")

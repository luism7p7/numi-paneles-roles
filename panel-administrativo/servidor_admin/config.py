"""Configuración del panel administrativo, leída de variables de entorno (.env)."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Carpeta del panel (donde están los .html, css/, js/ e img/)
CARPETA_PANEL = Path(__file__).resolve().parent.parent

# El .env está en la raíz del proyecto y lo comparten los dos paneles.
load_dotenv(CARPETA_PANEL.parent / ".env")


class Config:
    SECRET_KEY = os.environ.get("ADMIN_SECRET_KEY") or "solo-para-desarrollo-admin"

    # Los dos paneles corren en localhost (puertos 5000 y 5001) y el navegador
    # comparte cookies entre puertos: cada panel usa un nombre de cookie propio.
    SESSION_COOKIE_NAME = "numi_admin_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.environ.get("DB_PORT", "3306"))
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_NAME = os.environ.get("DB_NAME", "numi")

    # Backend de la app Numi (FastAPI). Monitoreo técnico revisa que responda.
    APP_API_URL = os.environ.get("APP_API_URL", "").rstrip("/")

    # Archivos que se suben desde Recursos
    CARPETA_UPLOADS = CARPETA_PANEL / "uploads"
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB por envío

    # Los equipos con una versión anterior a esta no reciben actividades nuevas
    VERSION_MINIMA_ACTIVIDADES = "1.2.0"

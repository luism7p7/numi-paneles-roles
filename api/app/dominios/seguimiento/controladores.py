"""Rutas del seguimiento del grupo (solo docente): panel, estudiantes y actividades."""

from flask import Blueprint, request

from app.compartido.archivos import TIPO_XLSX, enviar
from app.compartido.validaciones import cargar
from app.dominios.grupos.contexto import con_grupo_activo
from app.respuestas import exito
from app.seguridad import requiere_docente

from . import servicios
from .dtos import ActividadActivaDTO, NotaDTO

seguimiento_bp = Blueprint("seguimiento", __name__)


@seguimiento_bp.get("/panel")
@requiere_docente
@con_grupo_activo
def panel(usuario_id, grupo):
    return exito(servicios.panel(grupo))


@seguimiento_bp.get("/estudiantes")
@requiere_docente
@con_grupo_activo
def listar_estudiantes(usuario_id, grupo):
    return exito(servicios.listar_estudiantes(grupo))


@seguimiento_bp.get("/estudiantes/exportar")
@requiere_docente
@con_grupo_activo
def exportar_estudiantes(usuario_id, grupo):
    contenido, nombre = servicios.exportar_estudiantes(grupo)
    return enviar(contenido, nombre, TIPO_XLSX)


@seguimiento_bp.get("/estudiantes/<int:estudiante_id>")
@requiere_docente
@con_grupo_activo
def ficha(usuario_id, grupo, estudiante_id):
    return exito(servicios.ficha(grupo, estudiante_id))


@seguimiento_bp.put("/estudiantes/<int:estudiante_id>/nota")
@requiere_docente
@con_grupo_activo
def guardar_nota(usuario_id, grupo, estudiante_id):
    datos = cargar(NotaDTO(), request.get_json(silent=True))
    return exito(servicios.guardar_nota(grupo, estudiante_id, datos["nota"]))


@seguimiento_bp.get("/estudiantes/<int:estudiante_id>/informe")
@requiere_docente
@con_grupo_activo
def informe_estudiante(usuario_id, grupo, estudiante_id):
    contenido, nombre = servicios.informe_estudiante(grupo, estudiante_id)
    return enviar(contenido, nombre, "application/pdf")


@seguimiento_bp.get("/actividades")
@requiere_docente
@con_grupo_activo
def listar_actividades(usuario_id, grupo):
    return exito(servicios.listar_actividades(grupo))


@seguimiento_bp.patch("/actividades/<slug>")
@requiere_docente
@con_grupo_activo
def activar_actividad(usuario_id, grupo, slug):
    datos = cargar(ActividadActivaDTO(), request.get_json(silent=True))
    return exito(servicios.activar_actividad(grupo, slug, datos["activa"]))

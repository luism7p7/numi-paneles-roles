"""Validación de lo que llega al guardar una nota o activar una actividad."""

from app.compartido.validaciones import Booleano, Esquema, Texto


class NotaDTO(Esquema):
    nota = Texto("la nota", 2000, obligatorio=False)


class ActividadActivaDTO(Esquema):
    activa = Booleano("Indica si la actividad queda activa (true) o inactiva (false).")

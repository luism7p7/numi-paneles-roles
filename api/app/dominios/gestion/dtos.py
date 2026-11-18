"""Validación de lo que llega al activar o desactivar el asistente de IA."""

from app.compartido.validaciones import Booleano, Esquema


class AsistenteIaDTO(Esquema):
    activada = Booleano("Indica si el asistente queda activado (true) o desactivado (false).")

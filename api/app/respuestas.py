"""Formato único de las respuestas JSON de la API (igual que el ejemplo de referencia).

    éxito:  {"success": true,  "message": "...", "data": ...}
    error:  {"success": false, "error": {"message": "...", "details": ...}}
"""

from flask import jsonify


def exito(data=None, mensaje=None, codigo=200):
    cuerpo = {"success": True}
    if mensaje:
        cuerpo["message"] = mensaje
    cuerpo["data"] = data
    return jsonify(cuerpo), codigo


def fallo(mensaje, codigo=400, detalles=None):
    error = {"message": mensaje}
    if detalles:
        error["details"] = detalles
    return jsonify({"success": False, "error": error}), codigo

"""El docente: su perfil y el grupo con el que trabaja."""

from app.compartido.textos import iniciales, nombre_grupo
from app.dominios.grupos import servicios as grupos
from app.dominios.seguimiento import calculos
from app.dominios.usuarios import repositorios as usuarios
from app.excepciones import PermisoDenegado


def _grupo_json(g):
    resumen = calculos.resumen_grupo(g)
    return {
        "id": g["id"],
        "grado": f"{g['grado']}°",
        "corto": f"{g['grado']}° {g['letra']}",
        "nombre": nombre_grupo(g["grado"], g["letra"]),
        "estudiantes": len(resumen["estudiantes"]),
        "codigo": g["codigo"],
        "avance": resumen["avance"],
        "activos": resumen["activos"],
    }


def perfil(docente_id, grupo_pedido):
    u = usuarios.perfil_del_docente(docente_id)
    del_docente = grupos.del_docente(docente_id)
    activo = grupos.grupo_activo(docente_id, grupo_pedido)["id"] if del_docente else None
    documento = u["documento"] or ""
    return {
        "nombre": u["nombre"],
        "apellido": u["apellido"],
        "nombre_completo": f"Prof. {u['nombre']} {u['apellido']}",
        "iniciales": iniciales(f"{u['nombre']} {u['apellido']}"),
        "correo": u["correo"],
        "documento": f"C.C. {'•' * max(0, len(documento) - 4)}{documento[-4:]}" if documento else "Sin registrar",
        "rol": u["rol"],
        "institucion": u["institucion"] or "Sin institución asignada",
        "sede": u["sede"],
        "comuna": u["comuna"] or "—",
        "grupos": [_grupo_json(g) for g in del_docente],
        "grupo_activo": activo,
    }


def cambiar_grupo(docente_id, grupo_id):
    """Confirma que el grupo es del docente. La pantalla lo recuerda y lo manda en `X-Grupo-Id`."""
    if not any(g["id"] == grupo_id for g in grupos.del_docente(docente_id)):
        raise PermisoDenegado("Ese grupo no está a tu cargo.")
    return {"grupo_activo": grupo_id}

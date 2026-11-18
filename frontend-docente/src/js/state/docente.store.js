// Lo que la pantalla sabe del docente: su perfil, sus grupos y con cuál está trabajando.
import { cambiarGrupo as cambiarGrupoApi, getPerfil } from '../api/docente.api.js';
import { getGrupoActivo, saveGrupoActivo } from '../auth/session.service.js';

export const estado = {
  yo: null, // perfil del docente (/docente/me)
  grupos: {}, // grupos a cargo, por id
  activo: null, // id del grupo activo
  estudiantes: null, // lista del grupo activo (se pide una vez y se filtra en la pantalla)
};

export const grupo = () => estado.grupos[estado.activo];

export async function cargarPerfil() {
  const datos = await getPerfil();
  estado.yo = datos;
  estado.grupos = Object.fromEntries(datos.grupos.map((g) => [g.id, g]));
  // Se respeta el grupo que el docente eligió, si sigue siendo suyo
  const recordado = getGrupoActivo();
  estado.activo = estado.grupos[recordado] ? recordado : datos.grupo_activo;
  saveGrupoActivo(estado.activo);
}

export async function elegirGrupo(id) {
  await cambiarGrupoApi(id);
  estado.activo = id;
  estado.estudiantes = null;
  saveGrupoActivo(id);
}

export function limpiarEstado() {
  estado.yo = null;
  estado.grupos = {};
  estado.activo = null;
  estado.estudiantes = null;
}

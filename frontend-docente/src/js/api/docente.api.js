import { request } from './http.js';

export function getPerfil() {
  return request('/docente/me');
}

export function cambiarGrupo(grupoId) {
  return request('/docente/grupo-activo', { method: 'POST', body: { grupo_id: grupoId } });
}

// Sesión del docente: el token de la API y el grupo con el que está trabajando.
import { getItem, removeItem, saveItem } from '../utils/storage.js';

const TOKEN_KEY = 'numi_docente_token';
const GRUPO_KEY = 'numi_docente_grupo';

export function saveToken(token) {
  saveItem(TOKEN_KEY, token);
}

export function getToken() {
  return getItem(TOKEN_KEY);
}

export function hasSession() {
  return Boolean(getToken());
}

export function saveGrupoActivo(id) {
  saveItem(GRUPO_KEY, id);
}

export function getGrupoActivo() {
  return getItem(GRUPO_KEY);
}

export function clearSession() {
  removeItem(TOKEN_KEY);
  removeItem(GRUPO_KEY);
}

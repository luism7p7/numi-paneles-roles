// Sesión del administrador: el token de la API.
import { getItem, removeItem, saveItem } from '../utils/storage.js';

const TOKEN_KEY = 'numi_admin_token';

export function saveToken(token) {
  saveItem(TOKEN_KEY, token);
}

export function getToken() {
  return getItem(TOKEN_KEY);
}

export function hasSession() {
  return Boolean(getToken());
}

export function clearSession() {
  removeItem(TOKEN_KEY);
}

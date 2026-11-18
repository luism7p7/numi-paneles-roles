import { request } from './http.js';

export function login(correo, password) {
  return request('/auth/login', { method: 'POST', body: { correo, password, rol: 'Docente' } });
}

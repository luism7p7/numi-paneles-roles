import { request } from './http.js';

export function login(correo, password) {
  return request('/auth/login', { method: 'POST', body: { correo, password, rol: 'Administrador' } });
}

export function solicitarCuenta(datos) {
  return request('/auth/registro', { method: 'POST', body: datos });
}

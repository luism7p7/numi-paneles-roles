import { request } from './http.js';

export const getUsuarios = () => request('/admin/usuarios');
export const crearUsuario = (cuerpo) => request('/admin/usuarios', { method: 'POST', body: cuerpo });
export const editarUsuario = (id, cuerpo) => request(`/admin/usuarios/${id}`, { method: 'PUT', body: cuerpo });
export const eliminarUsuario = (id) => request(`/admin/usuarios/${id}`, { method: 'DELETE' });
export const cambiarEstado = (id, estado) => request(`/admin/usuarios/${id}/estado`, { method: 'PATCH', body: { estado } });
export const restablecerPassword = (id) => request(`/admin/usuarios/${id}/password-temporal`, { method: 'POST' });
export const importarUsuarios = (formulario) => request('/admin/usuarios/importar', { method: 'POST', formulario });

import { request } from './http.js';

const ruta = (id) => `/admin/actividades/${encodeURIComponent(id)}`;

export const getActividades = () => request('/admin/actividades');
export const getActividad = (id) => request(ruta(id));
export const crearActividad = (cuerpo) => request('/admin/actividades', { method: 'POST', body: cuerpo });
export const editarActividad = (id, cuerpo) => request(ruta(id), { method: 'PUT', body: cuerpo });
export const eliminarActividad = (id) => request(ruta(id), { method: 'DELETE' });
export const getHistorial = () => request('/admin/historial');

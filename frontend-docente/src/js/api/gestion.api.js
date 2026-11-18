import { request } from './http.js';

export const getGestion = () => request('/docente/gestion');
export const nuevoCodigo = () => request('/docente/gestion/codigo', { method: 'POST' });
export const cambiarIa = (activada) => request('/docente/gestion/ia', { method: 'PATCH', body: { activada } });
export const actualizarPaquete = () => request('/docente/gestion/paquete', { method: 'POST' });

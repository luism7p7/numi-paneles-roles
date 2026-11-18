import { request } from './http.js';

export const getInstituciones = () => request('/admin/instituciones');
export const getInstitucion = (id) => request(`/admin/instituciones/${id}`);
export const crearInstitucion = (cuerpo) => request('/admin/instituciones', { method: 'POST', body: cuerpo });
export const crearGrupo = (institucionId, cuerpo) =>
  request(`/admin/instituciones/${institucionId}/grupos`, { method: 'POST', body: cuerpo });

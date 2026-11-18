import { download, request } from './http.js';

export const getPanel = () => request('/docente/panel');
export const getEstudiantes = () => request('/docente/estudiantes');
export const getFicha = (id) => request(`/docente/estudiantes/${id}`);
export const guardarNota = (id, nota) => request(`/docente/estudiantes/${id}/nota`, { method: 'PUT', body: { nota } });
export const exportarEstudiantes = () => download('/docente/estudiantes/exportar');
export const informeDeEstudiante = (id) => download(`/docente/estudiantes/${id}/informe`);

export const getActividades = () => request('/docente/actividades');
export const activarActividad = (id, activa) =>
  request(`/docente/actividades/${encodeURIComponent(id)}`, { method: 'PATCH', body: { activa } });

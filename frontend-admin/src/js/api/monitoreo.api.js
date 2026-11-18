import { download, request } from './http.js';

export const getMonitoreo = () => request('/admin/monitoreo');
export const generarInforme = () => request('/admin/informes', { method: 'POST' });
export const descargarInforme = (id) => download(`/admin/informes/${id}/descargar`);

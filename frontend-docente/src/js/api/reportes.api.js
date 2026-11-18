import { download, request } from './http.js';

export const getReporte = (periodo) =>
  request(`/docente/reportes${periodo ? `?periodo=${encodeURIComponent(periodo)}` : ''}`);

export const descargarReporte = (consulta) => download(`/docente/reportes/descargar?${consulta}`);

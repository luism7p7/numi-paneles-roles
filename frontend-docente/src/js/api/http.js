// Cliente HTTP único: todo lo que sale hacia la API pasa por aquí.
// Agrega el token y el grupo activo, desenvuelve {success, data} y normaliza los errores.
import { clearSession, getGrupoActivo, getToken } from '../auth/session.service.js';

const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:5001/api/v1').replace(/\/$/, '');
const SIN_CONEXION = 'No hay conexión con el servidor. Revisa que la API esté encendida (python app.py en api/).';

export class ApiError extends Error {
  constructor({ status, message, details = null }) {
    super(message);
    this.status = status;
    this.details = details;
  }
}

function cabeceras(extra = {}) {
  const headers = { ...extra };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  const grupo = getGrupoActivo();
  if (grupo) headers['X-Grupo-Id'] = String(grupo);
  return headers;
}

async function enviar(path, options) {
  try {
    return await fetch(`${API_URL}${path}`, options);
  } catch {
    throw new ApiError({ status: 0, message: SIN_CONEXION });
  }
}

async function errorDe(response) {
  const cuerpo = await response.json().catch(() => null);
  const error = new ApiError({
    status: response.status,
    message: cuerpo?.error?.message ?? 'Ocurrió un error inesperado.',
    details: cuerpo?.error?.details ?? null,
  });
  // Un 401 fuera del login quiere decir que la sesión terminó: la pantalla vuelve al login
  if (response.status === 401 && !response.url.endsWith('/auth/login')) {
    clearSession();
    window.dispatchEvent(new Event('sesion-terminada'));
  }
  return error;
}

export async function request(path, { method = 'GET', body } = {}) {
  const headers = cabeceras(body !== undefined ? { 'Content-Type': 'application/json' } : {});
  const response = await enviar(path, { method, headers, body: body !== undefined ? JSON.stringify(body) : undefined });
  if (!response.ok) throw await errorDe(response);
  if (response.status === 204) return null;
  return (await response.json()).data;
}

// Descarga de archivos (Excel o PDF): devuelve el contenido y el nombre que sugiere el servidor.
export async function download(path) {
  const response = await enviar(path, { headers: cabeceras() });
  if (!response.ok) throw await errorDe(response);
  const nombre = /filename="?([^";]+)"?/.exec(response.headers.get('Content-Disposition') || '')?.[1] || 'numi';
  return { blob: await response.blob(), nombre };
}

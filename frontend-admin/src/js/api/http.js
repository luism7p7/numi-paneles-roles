// Cliente HTTP único: todo lo que sale hacia la API pasa por aquí.
// Agrega el token, desenvuelve {success, data} y normaliza los errores.
import { clearSession, getToken } from '../auth/session.service.js';

const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:5001/api/v1').replace(/\/$/, '');
const SIN_CONEXION = 'No hay conexión con el servidor. Revisa que la API esté encendida (python app.py en api/).';
const PAGINAS_PUBLICAS = ['/auth/login', '/auth/registro'];

export class ApiError extends Error {
  constructor({ status, message, details = null }) {
    super(message);
    this.status = status;
    this.details = details;
  }
}

// Los archivos subidos (imágenes, audios) se piden directo a la API, sin token: <img> y <audio> no pueden enviarlo
export function urlDeArchivo(ruta) {
  return ruta ? new URL(ruta, API_URL).href : null;
}

function cabeceras(extra = {}) {
  const headers = { ...extra };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

async function enviar(path, options) {
  try {
    return await fetch(`${API_URL}${path}`, options);
  } catch {
    throw new ApiError({ status: 0, message: SIN_CONEXION });
  }
}

async function errorDe(response, path) {
  const cuerpo = await response.json().catch(() => null);
  const error = new ApiError({
    status: response.status,
    message: cuerpo?.error?.message ?? 'Ocurrió un error inesperado.',
    details: cuerpo?.error?.details ?? null,
  });
  // Un 401 fuera del login quiere decir que la sesión terminó: la pantalla vuelve al login
  if (response.status === 401 && !PAGINAS_PUBLICAS.includes(path)) {
    clearSession();
    window.dispatchEvent(new Event('sesion-terminada'));
  }
  return error;
}

// `formulario` (FormData) sirve para subir archivos; `body` es JSON.
export async function request(path, { method = 'GET', body, formulario } = {}) {
  const headers = cabeceras(body !== undefined ? { 'Content-Type': 'application/json' } : {});
  const response = await enviar(path, {
    method,
    headers,
    body: formulario ?? (body !== undefined ? JSON.stringify(body) : undefined),
  });
  if (!response.ok) throw await errorDe(response, path);
  if (response.status === 204) return null;
  return (await response.json()).data;
}

// Descarga de archivos (CSV): devuelve el contenido y el nombre que sugiere el servidor.
export async function download(path) {
  const response = await enviar(path, { headers: cabeceras() });
  if (!response.ok) throw await errorDe(response, path);
  const nombre = /filename="?([^";]+)"?/.exec(response.headers.get('Content-Disposition') || '')?.[1] || 'numi';
  return { blob: await response.blob(), nombre };
}

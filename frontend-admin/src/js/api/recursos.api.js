import { request, urlDeArchivo } from './http.js';

// La dirección de cada archivo se completa con la de la API (la pantalla vive en otro puerto)
export async function getRecursos() {
  const datos = await request('/admin/recursos');
  return { ...datos, recursos: datos.recursos.map((r) => ({ ...r, url: urlDeArchivo(r.url) })) };
}

export const subirRecursos = (formulario) => request('/admin/recursos', { method: 'POST', formulario });

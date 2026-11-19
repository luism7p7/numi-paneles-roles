// Atajos para buscar y crear elementos de la página.
export const $ = (sel, ctx = document) => ctx.querySelector(sel);
export const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));

export function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

export function icono(clases) {
  return el('i', `bi ${clases}`);
}

// Botón de detalle: un ojo, con el texto solo para lectores de pantalla y como ayuda al pasar el mouse.
export function botonVer(etiqueta = 'Ver') {
  const boton = el('button', 'btn btn-sm btn-soft btn-icon');
  boton.type = 'button';
  boton.title = etiqueta;
  boton.setAttribute('aria-label', etiqueta);
  boton.appendChild(icono('bi-eye'));
  return boton;
}

export function iniciales(nombre) {
  return nombre.split(' ').filter(Boolean).slice(0, 2).map((p) => p[0]).join('').toUpperCase();
}

export function escapeHtml(texto) {
  return String(texto ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
}

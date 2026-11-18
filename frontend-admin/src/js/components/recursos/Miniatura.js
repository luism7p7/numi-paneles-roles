import { el, icono } from '../../utils/dom.js';

// Dibuja el recurso en un cuadro pequeño: la imagen completa, o el ícono de audio o de video.
export function miniatura(recurso, clase) {
  const nodo = el(clase === 'thumb' ? 'div' : 'span', clase);
  if (recurso.tipo === 'Audio') {
    nodo.appendChild(icono('bi-music-note-beamed'));
  } else if (recurso.tipo === 'Video') {
    nodo.appendChild(icono('bi-film'));
  } else if (recurso.url) {
    // Imagen real de la app: cabe dentro del mismo cuadro que tenía el emoji
    // (.thumb mide 64px de alto y .thumb-sm 40px; sin este límite la imagen se sale)
    const alto = clase === 'thumb' ? '64px' : '40px';
    const img = el('img');
    img.src = recurso.url;
    img.alt = recurso.nombre;
    img.loading = 'lazy';
    Object.assign(img.style, { maxWidth: '100%', maxHeight: alto, objectFit: 'contain' });
    nodo.style.overflow = 'hidden';
    nodo.appendChild(img);
  } else {
    nodo.textContent = recurso.emoji || '🖼️';
  }
  return nodo;
}

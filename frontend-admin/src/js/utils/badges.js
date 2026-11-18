import { el } from './dom.js';

const STATUS_CLASS = {
  Publicada: 'status-success',
  Activa: 'status-success',
  Activo: 'status-success',
  Borrador: 'status-warning',
  Pendiente: 'status-warning',
  Desactivada: 'status-muted',
  Inactivo: 'status-muted',
  Inactiva: 'status-muted',
  Editada: 'status-info',
  Eliminada: 'status-danger',
  Crítico: 'status-danger',
  Alerta: 'status-warning',
  Info: 'status-info',
  'Todas las versiones': 'status-success',
};

export function setStatus(node, estado) {
  node.className = `status ${STATUS_CLASS[estado] || 'status-muted'}`;
  node.textContent = estado;
}

export function statusSpan(estado) {
  const span = el('span');
  setStatus(span, estado);
  return span;
}

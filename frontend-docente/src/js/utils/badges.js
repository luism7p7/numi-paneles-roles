import { ESTADO_CLASS } from './constantes.js';
import { el } from './dom.js';

export function statusBadge(estadoTexto) {
  return el('span', `status ${ESTADO_CLASS[estadoTexto] || 'status-muted'}`, estadoTexto);
}

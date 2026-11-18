// Avisos: emergentes (toast), fijos en la página (flash) y mensajes de error.
import { Toast } from 'bootstrap';

import { $, el } from './dom.js';

export function showToast(message) {
  let area = $('#toastArea');
  if (!area) {
    area = el('div', 'toast-container position-fixed bottom-0 end-0 p-3');
    area.id = 'toastArea';
    document.body.appendChild(area);
  }
  const toast = el('div', 'toast align-items-center text-bg-dark border-0');
  toast.setAttribute('role', 'status');
  toast.innerHTML =
    '<div class="d-flex"><div class="toast-body"></div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Cerrar"></button></div>';
  $('.toast-body', toast).textContent = message;
  area.appendChild(toast);
  new Toast(toast, { delay: 4500 }).show();
  toast.addEventListener('hidden.bs.toast', () => toast.remove());
}

export function showFlash(message, type = 'success') {
  const flash = $('#flash');
  if (!flash) {
    showToast(message);
    return;
  }
  const alerta = el('div', `alert alert-${type} alert-dismissible fade show d-flex align-items-center gap-2`);
  alerta.setAttribute('role', 'alert');
  const icono = type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-triangle-fill';
  alerta.innerHTML = `<i class="bi ${icono}"></i><span></span><button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>`;
  $('span', alerta).textContent = message;
  flash.replaceChildren(alerta);
}

export function mostrarError(error) {
  showToast(error?.message || 'Ocurrió un error inesperado.');
}

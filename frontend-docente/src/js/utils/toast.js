// Avisos emergentes (toasts) y mensajes de error.
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
  new Toast(toast, { delay: 3500 }).show();
  toast.addEventListener('hidden.bs.toast', () => toast.remove());
}

export function mostrarError(error) {
  showToast(error?.message || 'Ocurrió un error inesperado.');
}

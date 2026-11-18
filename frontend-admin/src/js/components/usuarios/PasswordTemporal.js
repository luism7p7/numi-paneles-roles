import { Modal } from 'bootstrap';

import { $ } from '../../utils/dom.js';
import { showToast } from '../../utils/toast.js';

// Ventana con la contraseña temporal: se muestra una sola vez y se puede copiar
export function mostrarPasswordTemporal(nombre, password) {
  let modal = $('#modalPasswordTemporal');
  if (!modal) {
    document.body.insertAdjacentHTML(
      'beforeend',
      `
      <div class="modal fade" id="modalPasswordTemporal" tabindex="-1" aria-labelledby="passwordTemporalTitulo" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-body text-center p-4">
              <div class="danger-icon bg-success-subtle text-success"><i class="bi bi-key"></i></div>
              <h2 class="h5 fw-bold" id="passwordTemporalTitulo"></h2>
              <p class="text-secondary">Compártela solo con esa persona. Por seguridad <strong>no se volverá a mostrar</strong>.</p>
              <div class="border rounded-3 p-3 fs-3 fw-bold font-monospace mb-3" data-password></div>
              <button type="button" class="btn btn-primary" data-copiar><i class="bi bi-clipboard me-1"></i> Copiar contraseña</button>
            </div>
            <div class="modal-footer justify-content-center border-0 pt-0 pb-4">
              <button type="button" class="btn btn-light" data-bs-dismiss="modal">Listo, ya la guardé</button>
            </div>
          </div>
        </div>
      </div>`,
    );
    modal = $('#modalPasswordTemporal');
    $('[data-copiar]', modal).addEventListener('click', () => {
      const texto = $('[data-password]', modal).textContent;
      const listo = () => showToast('Contraseña copiada.');
      if (navigator.clipboard) navigator.clipboard.writeText(texto).then(listo, listo);
      else listo();
    });
  }
  $('#passwordTemporalTitulo', modal).textContent = `Contraseña temporal de ${nombre}`;
  $('[data-password]', modal).textContent = password;
  Modal.getOrCreateInstance(modal).show();
}

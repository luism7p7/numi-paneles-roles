import logoUrl from '../../img/logo-numi.png';
import { solicitarCuenta } from '../api/auth.api.js';
import { $, el, icono } from '../utils/dom.js';

export function RegistroPage() {
  return `<main class="auth-wrapper">
    <div class="card auth-card">
      <div class="row g-0">
        <div class="col-md-5 auth-aside">
          <div class="brand">
            <img src="${logoUrl}" alt="Numi" class="brand-logo">
            <span>
              <span class="brand-name d-block">Numi</span>
              <span class="brand-sub">Panel administrativo</span>
            </span>
          </div>
          <div>
            <h1 class="mb-3">Registro cerrado</h1>
            <p class="mb-0">Solo un administrador puede crear usuarios. No hay registro abierto.</p>
          </div>
          <a href="#/login" class="btn btn-outline-light align-self-start"><i class="bi bi-arrow-left me-1"></i> Volver</a>
        </div>

        <div class="col-md-7 auth-form bg-white">
          <h2 class="fw-bold mb-1">Crear usuario</h2>
          <p class="text-secondary mb-4">La cuenta queda pendiente hasta que un administrador la apruebe.</p>

          <form>
            <div class="row g-3">
              <div class="col-sm-6">
                <label for="nombre" class="form-label">Nombre</label>
                <input type="text" class="form-control" id="nombre" required>
              </div>
              <div class="col-sm-6">
                <label for="apellido" class="form-label">Apellido</label>
                <input type="text" class="form-control" id="apellido" required>
              </div>
              <div class="col-12">
                <label for="correo" class="form-label">Correo institucional</label>
                <input type="email" class="form-control" id="correo" placeholder="nombre@ie.edu.co" required>
              </div>
            </div>
            <button type="submit" class="btn btn-primary w-100 py-2 mt-4">Crear cuenta</button>
          </form>
        </div>
      </div>
    </div>
  </main>`;
}

// Solicitud de cuenta: no pide sesión, la cuenta queda pendiente hasta que un administrador la apruebe
export function mountRegistroPage() {
  const form = $('form');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const boton = $('button[type="submit"]', form);
    boton.disabled = true;
    let ok = true;
    let mensaje;
    try {
      await solicitarCuenta({ nombre: $('#nombre').value, apellido: $('#apellido').value, correo: $('#correo').value });
      mensaje = 'Solicitud enviada. Un administrador revisará tu cuenta.';
    } catch (error) {
      ok = false;
      mensaje = error.message || 'No se pudo enviar la solicitud.';
    }
    $('#avisoRegistro')?.remove();
    const aviso = el('div', `alert alert-${ok ? 'success' : 'danger'} d-flex align-items-center gap-2`);
    aviso.id = 'avisoRegistro';
    aviso.setAttribute('role', 'alert');
    aviso.append(icono(ok ? 'bi-check-circle-fill' : 'bi-exclamation-triangle-fill'), el('span', '', mensaje));
    form.before(aviso);
    if (ok) form.reset();
    boton.disabled = false;
  });
}

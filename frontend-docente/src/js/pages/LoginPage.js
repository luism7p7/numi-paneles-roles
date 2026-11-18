import logoUrl from '../../img/logo-numi.png';
import { login } from '../api/auth.api.js';
import { saveToken } from '../auth/session.service.js';
import { $, el } from '../utils/dom.js';
import { showToast } from '../utils/toast.js';

export function LoginPage() {
  return `<main class="auth-wrapper">
    <div class="card auth-card">
      <div class="row g-0">
        <!-- Lado de marca -->
        <div class="col-md-5 auth-aside">
          <div class="brand">
            <img src="${logoUrl}" alt="Numi" class="brand-logo">
            <span>
              <span class="brand-name d-block">Numi</span>
              <span class="brand-sub">Panel para docentes</span>
            </span>
          </div>
          <div>
            <h1 class="mb-3">Seguimiento del aula</h1>
            <p class="mb-0">Aquí no hay contenido para niños. Es la herramienta de seguimiento del aula.</p>
          </div>
          <ul class="list-unstyled small mb-0 d-grid gap-2">
            <li><i class="bi bi-graph-up-arrow me-2"></i>Avance de cada estudiante</li>
            <li><i class="bi bi-toggles me-2"></i>Actividades activas por grupo</li>
            <li><i class="bi bi-file-earmark-bar-graph me-2"></i>Reportes por periodo</li>
          </ul>
        </div>

        <!-- Formulario -->
        <div class="col-md-7 auth-form bg-white">
          <h2 class="fw-bold mb-1">Entrar al panel</h2>
          <p class="text-secondary mb-4">Usa el correo institucional que te entregó tu sede.</p>

          <form id="loginForm" novalidate>
            <div class="mb-3">
              <label for="email" class="form-label">Correo institucional</label>
              <div class="input-group">
                <span class="input-group-text bg-white"><i class="bi bi-envelope"></i></span>
                <input type="email" class="form-control" id="email" placeholder="nombre@ielaaldea.edu.co" required>
                <div class="invalid-feedback">Escribe un correo válido.</div>
              </div>
            </div>
            <div class="mb-2">
              <label for="password" class="form-label">Contraseña</label>
              <div class="input-group">
                <span class="input-group-text bg-white"><i class="bi bi-lock"></i></span>
                <input type="password" class="form-control" id="password" placeholder="••••••••" required>
                <button class="btn btn-outline-secondary" type="button" id="togglePassword" aria-label="Mostrar contraseña"><i class="bi bi-eye"></i></button>
                <div class="invalid-feedback">Escribe tu contraseña.</div>
              </div>
            </div>
            <div class="text-end mb-4">
              <a href="#" class="small fw-bold text-decoration-none">Olvidé mi contraseña</a>
            </div>
            <button type="submit" class="btn btn-primary w-100 py-2">Entrar</button>
          </form>

          <div class="notice mt-4 mb-0">
            <i class="bi bi-building"></i>
            <div>Acceso entregado por la coordinación de tu sede.</div>
          </div>
        </div>
      </div>
    </div>
  </main>`;
}

export function mountLoginPage({ navigate }) {
  const form = $('#loginForm');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    $('#loginError')?.remove();
    if (!form.checkValidity()) {
      form.classList.add('was-validated');
      return;
    }
    const boton = $('button[type="submit"]', form);
    boton.disabled = true;
    try {
      const datos = await login($('#email').value.trim(), $('#password').value);
      saveToken(datos.access_token);
      navigate('panel');
    } catch (error) {
      const aviso = el('div', 'alert alert-danger d-flex align-items-center gap-2');
      aviso.id = 'loginError';
      aviso.setAttribute('role', 'alert');
      aviso.append(el('i', 'bi bi-shield-lock'), el('span', '', error.message || 'No se pudo iniciar sesión.'));
      form.before(aviso);
      boton.disabled = false;
    }
  });

  $('#togglePassword').addEventListener('click', (e) => {
    const input = $('#password');
    const visible = input.type === 'text';
    input.type = visible ? 'password' : 'text';
    e.currentTarget.innerHTML = visible ? '<i class="bi bi-eye"></i>' : '<i class="bi bi-eye-slash"></i>';
  });

  $('a[href="#"]').addEventListener('click', (e) => {
    e.preventDefault();
    showToast('Pide a la coordinación de tu sede que active de nuevo tu cuenta: recibirás una contraseña temporal.');
  });
}

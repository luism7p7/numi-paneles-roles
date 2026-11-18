import logoUrl from '../../img/logo-numi.png';
import { login } from '../api/auth.api.js';
import { saveToken } from '../auth/session.service.js';
import { $, $$ } from '../utils/dom.js';
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
              <span class="brand-sub">Panel administrativo</span>
            </span>
          </div>
          <div>
            <h1 class="mb-3">Gestión central de Numi</h1>
            <p class="mb-0">Acceso restringido. Solo cuentas con rol de administrador.</p>
          </div>
          <ul class="list-unstyled small mb-0 d-grid gap-2">
            <li><i class="bi bi-check2-circle me-2"></i>Contenido educativo y recursos</li>
            <li><i class="bi bi-check2-circle me-2"></i>Instituciones, grupos y usuarios</li>
            <li><i class="bi bi-check2-circle me-2"></i>Monitoreo técnico de la plataforma</li>
          </ul>
        </div>

        <!-- Formulario -->
        <div class="col-md-7 auth-form bg-white">
          <h2 class="fw-bold mb-1">Iniciar sesión</h2>
          <p class="text-secondary mb-4">Ingresa con tu cuenta institucional de administrador.</p>

          <div class="alert alert-danger d-none d-flex align-items-center gap-2" id="loginError" role="alert">
            <i class="bi bi-shield-lock"></i>
            <span>Esta cuenta no tiene permisos de administrador.</span>
          </div>

          <form id="loginForm" novalidate>
            <div class="mb-3">
              <label for="email" class="form-label">Correo institucional</label>
              <div class="input-group">
                <span class="input-group-text bg-white"><i class="bi bi-envelope"></i></span>
                <input type="email" class="form-control" id="email" placeholder="nombre@medellin.gov.co" required>
              </div>
            </div>
            <div class="mb-2">
              <label for="password" class="form-label">Contraseña</label>
              <div class="input-group">
                <span class="input-group-text bg-white"><i class="bi bi-lock"></i></span>
                <input type="password" class="form-control" id="password" placeholder="••••••••" required>
              </div>
            </div>
            <div class="text-end mb-4">
              <a href="#" class="small fw-semibold text-decoration-none">Olvidé mi contraseña</a>
            </div>
            <button type="submit" class="btn btn-primary w-100 py-2">Entrar</button>
          </form>

          <hr class="my-4">
          <p class="small text-secondary mb-0 text-center">
            ¿Necesitas una cuenta nueva? <a href="#/crear-usuario" class="fw-semibold text-decoration-none">Crear usuario</a>
          </p>
          <p class="small text-secondary text-center mt-2 mb-0">
            Prueba: un correo con <strong>@medellin.gov.co</strong> entra al panel; otro dominio muestra el error de permisos.
          </p>
        </div>
      </div>
    </div>
  </main>`;
}

export function mountLoginPage({ navigate }) {
  const form = $('#loginForm');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const error = $('#loginError');
    error.classList.add('d-none');
    if (!form.checkValidity()) {
      form.classList.add('was-validated');
      return;
    }
    const boton = $('button[type="submit"]', form);
    boton.disabled = true;
    try {
      const datos = await login($('#email').value.trim(), $('#password').value);
      saveToken(datos.access_token);
      navigate('inicio');
    } catch (fallo) {
      $('span', error).textContent = fallo.message || 'No se pudo iniciar sesión.';
      error.classList.remove('d-none');
      boton.disabled = false;
    }
  });

  const olvide = $$('a[href="#"]').find((a) => a.textContent.includes('Olvidé'));
  olvide?.addEventListener('click', (e) => {
    e.preventDefault();
    showToast('Pide a otro administrador que active de nuevo tu cuenta: recibirás una contraseña temporal.');
  });
}

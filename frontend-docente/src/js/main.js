import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import '../css/main.css';

import { clearSession } from './auth/session.service.js';
import { Layout, mountLayout, pintarGrupo } from './components/layout/Layout.js';
import { requireAuth } from './router/guards.js';
import { getRoute, leerRuta } from './router/routes.js';
import { cargarPerfil, estado, limpiarEstado } from './state/docente.store.js';
import { mostrarError } from './utils/toast.js';

const app = document.querySelector('#app');

function navigate(view) {
  const destino = `#/${view}`;
  if (window.location.hash === destino) render();
  else window.location.hash = destino; // el cambio de hash dispara render()
}

// Al cambiar de pantalla no deben quedar ventanas ni fondos oscuros de la anterior
function limpiarVentanas() {
  document.querySelectorAll('.modal-backdrop').forEach((n) => n.remove());
  document.body.classList.remove('modal-open');
  document.body.style.removeProperty('overflow');
  document.body.style.removeProperty('padding-right');
}

function renderSinGrupos() {
  app.innerHTML = `
    <main class="auth-wrapper">
      <div class="card auth-card p-5 text-center">
        <h1 class="h4 mb-3">No tienes grupos asignados</h1>
        <p class="text-secondary mb-4">La coordinación de tu sede los habilita. Cuando los tengas, vuelve a entrar.</p>
        <a href="#/login" class="btn btn-primary" data-action="logout">Cerrar sesión</a>
      </div>
    </main>`;
}

async function render() {
  const { view, query } = leerRuta();
  const route = getRoute(view);
  if (!route) return navigate('panel');
  if (route.requiresAuth && !requireAuth(navigate)) return;

  limpiarVentanas();
  const contexto = { navigate, recargar: render, query };

  if (route.conLayout === false) {
    clearSession(); // abrir el login cierra la sesión
    limpiarEstado();
    app.innerHTML = route.page();
    return route.mount?.(contexto);
  }

  try {
    if (!estado.yo) await cargarPerfil();
  } catch (error) {
    return mostrarError(error); // si fue un 401, ya se mandó al login
  }
  if (!estado.activo) return renderSinGrupos();

  app.innerHTML = Layout(route.path, route.page());
  mountLayout(contexto);
  await route.mount?.(contexto);
  pintarGrupo();
}

app.addEventListener('click', (event) => {
  if (event.target.closest('[data-action="logout"]')) {
    clearSession();
    limpiarEstado();
  }
});

window.addEventListener('hashchange', render);
window.addEventListener('sesion-terminada', () => {
  limpiarEstado();
  navigate('login');
});

if (!window.location.hash) window.location.hash = '#/panel';
else render();

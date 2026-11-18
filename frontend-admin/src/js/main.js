import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import '../css/main.css';

import { clearSession } from './auth/session.service.js';
import { Layout } from './components/layout/Layout.js';
import { activarFiltrosDeTablas } from './components/tablas/filtros.js';
import { requireAuth } from './router/guards.js';
import { getRoute, leerRuta } from './router/routes.js';

const app = document.querySelector('#app');
let alSalir = null; // lo que la pantalla anterior pidió limpiar al irse (ventanas que viven en <body>, etc.)

// `view` puede traer datos para la pantalla: navigate('actividades?msg=publicada')
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

async function render() {
  const { view, query } = leerRuta();
  const route = getRoute(view);
  if (!route) return navigate('inicio');
  if (route.requiresAuth && !requireAuth(navigate)) return;

  alSalir?.();
  alSalir = null;
  limpiarVentanas();
  const contexto = { navigate, recargar: render, query };

  if (route.conLayout === false) {
    if (route.path === 'login') clearSession(); // abrir el login cierra la sesión
    app.innerHTML = route.page();
  } else {
    app.innerHTML = Layout(route.menu, route.page());
  }
  activarFiltrosDeTablas();
  const limpieza = await route.mount?.(contexto);
  if (typeof limpieza === 'function') alSalir = limpieza;
}

app.addEventListener('click', (event) => {
  if (event.target.closest('[data-action="logout"]')) clearSession();
});

window.addEventListener('hashchange', render);
window.addEventListener('sesion-terminada', () => navigate('login'));

if (!window.location.hash) window.location.hash = '#/inicio';
else render();

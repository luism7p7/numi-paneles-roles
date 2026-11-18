// Estructura común de las pantallas del administrador: la barra lateral y el lugar donde va cada página.
import logoUrl from '../../../img/logo-numi.png';

const MENU = [
  ['inicio', 'Inicio', 'bi-house-door'],
  ['actividades', 'Actividades', 'bi-puzzle'],
  ['recursos', 'Recursos', 'bi-images'],
  ['instituciones', 'Instituciones', 'bi-building'],
  ['usuarios', 'Usuarios', 'bi-people'],
  ['monitoreo', 'Monitoreo técnico', 'bi-activity'],
];

function Sidebar(activo) {
  const enlaces = MENU.map(
    ([ruta, texto, icono]) => `<a class="nav-link${ruta === activo ? ' active' : ''}" href="#/${ruta}"><i class="bi ${icono}"></i> ${texto}</a>`,
  ).join('');

  return `
    <aside class="sidebar offcanvas-lg offcanvas-start" tabindex="-1" id="sidebar" aria-label="Menú principal">
      <div class="sidebar-inner">
        <div class="d-flex align-items-center justify-content-between">
          <a href="#/inicio" class="brand">
            <img src="${logoUrl}" alt="Numi" class="brand-logo">
            <span><span class="brand-name d-block">Numi</span><span class="brand-sub">Panel administrativo</span></span>
          </a>
          <button type="button" class="btn-close d-lg-none" data-bs-dismiss="offcanvas" data-bs-target="#sidebar" aria-label="Cerrar menú"></button>
        </div>
        <p class="sidebar-label">Administración</p>
        <nav class="nav flex-column sidebar-nav">${enlaces}</nav>
        <div class="sidebar-footer sidebar-nav">
          <a class="nav-link" href="#/login" data-action="logout"><i class="bi bi-box-arrow-left"></i> Cerrar sesión</a>
        </div>
      </div>
    </aside>`;
}

// `activo` es la opción del menú que se marca; `pagina` trae la barra superior, el contenido y las ventanas de la pantalla
export function Layout(activo, pagina) {
  return `
    <div class="app">
      ${Sidebar(activo)}
      <div class="app-main">
        ${pagina}
      </div>
    </div>
    <div class="toast-container position-fixed bottom-0 end-0 p-3" id="toastArea"></div>`;
}

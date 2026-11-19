// Estructura común de todas las pantallas: barra lateral, grupo activo y las ventanas de perfil y cambio de grupo.
import { Modal } from 'bootstrap';

import logoUrl from '../../../img/logo-numi.png';
import { elegirGrupo, cargarPerfil, estado, grupo } from '../../state/docente.store.js';
import { $, $$, el, escapeHtml } from '../../utils/dom.js';
import { mostrarError, showToast } from '../../utils/toast.js';

const MENU = [
  ['panel', 'Panel', 'bi-grid-1x2'],
  ['estudiantes', 'Estudiantes', 'bi-people'],
  ['actividades', 'Actividades', 'bi-puzzle'],
  ['reportes', 'Reportes', 'bi-bar-chart-line'],
  ['gestion', 'Gestión', 'bi-gear'],
];

function Sidebar(vista) {
  const yo = estado.yo;
  const g = grupo();
  const enlaces = MENU.map(
    ([ruta, texto, icono]) =>
      `<a class="nav-link${ruta === vista ? ' active' : ''}" href="#/${ruta}"><i class="bi ${icono}"></i> ${texto}</a>`,
  ).join('');

  return `
    <aside class="sidebar offcanvas-lg offcanvas-start" tabindex="-1" id="sidebar" aria-label="Menú principal">
      <div class="sidebar-inner">
        <div class="d-flex align-items-center justify-content-between">
          <a href="#/panel" class="brand">
            <img src="${logoUrl}" alt="Numi" class="brand-logo">
            <span><span class="brand-name d-block">Numi</span><span class="brand-sub">Panel docente</span></span>
          </a>
          <button type="button" class="btn-close d-lg-none" data-bs-dismiss="offcanvas" data-bs-target="#sidebar" aria-label="Cerrar menú"></button>
        </div>
        <button type="button" class="teacher-card" data-bs-toggle="modal" data-bs-target="#modalPerfil">
          <span class="avatar">${escapeHtml(yo.iniciales)}</span>
          <span class="lh-sm">
            <span class="d-block fw-bold">${escapeHtml(yo.nombre_completo)}</span>
            <span class="small text-secondary"><span data-group="corto">${escapeHtml(g.corto)}</span> · ${escapeHtml(yo.institucion)}</span>
          </span>
        </button>
        <nav class="nav flex-column sidebar-nav">${enlaces}</nav>
        <div class="sidebar-footer sidebar-nav">
          <a class="nav-link" href="#/login" data-action="logout"><i class="bi bi-box-arrow-left"></i> Cerrar sesión</a>
        </div>
      </div>
    </aside>`;
}

// Solo en celular: en pantalla grande el grupo se ve en la tarjeta del profesor y esta barra no hace falta,
// pero en celular aquí vive el botón que abre el menú.
function BarraDelGrupo() {
  const g = grupo();
  return `
    <header class="group-bar d-lg-none">
      <button class="btn btn-switch d-lg-none ms-0" type="button" data-bs-toggle="offcanvas" data-bs-target="#sidebar" aria-controls="sidebar" aria-label="Abrir menú"><i class="bi bi-list"></i></button>
      <span class="group-badge" data-group="grado">${escapeHtml(g.grado)}</span>
      <div>
        <h1 class="group-name" data-group="nombre">${escapeHtml(g.nombre)}</h1>
        <div class="group-meta"><span data-group="estudiantes">${g.estudiantes}</span> estudiantes vinculados</div>
      </div>
    </header>`;
}

function ModalPerfil() {
  const yo = estado.yo;
  const g = grupo();
  return `
    <div class="modal fade" id="modalPerfil" tabindex="-1" aria-labelledby="perfilTitulo" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered modal-sm">
        <div class="modal-content">
          <div class="modal-body p-4 text-center">
            <button type="button" class="btn-close position-absolute top-0 end-0 m-3" data-bs-dismiss="modal" aria-label="Cerrar"></button>
            <span class="avatar avatar-lg mx-auto mb-2" style="background: var(--numi-primary); color: #fff;">${escapeHtml(yo.iniciales)}</span>
            <h2 class="h6 fw-bold mb-0" id="perfilTitulo">${escapeHtml(yo.nombre_completo)}</h2>
            <p class="small text-secondary mb-1">${escapeHtml(yo.correo)}</p>
            <p class="small text-secondary">${escapeHtml(yo.sede)} · ${escapeHtml(yo.comuna)}</p>
            <div class="text-start border rounded-4 p-3 mb-3" style="background: var(--numi-primary-soft)">
              <div class="small fw-bold text-uppercase text-secondary mb-1" style="font-size: .7rem; letter-spacing: .08em">Grupo activo</div>
              <div class="fw-bold" data-group="nombre">${escapeHtml(g.nombre)}</div>
              <div class="small text-secondary"><span data-group="estudiantes">${g.estudiantes}</span> estudiantes · código <span data-group="codigo">${escapeHtml(g.codigo)}</span></div>
              <button type="button" class="btn btn-soft btn-sm w-100 mt-2" id="btnCambiarGrupo">Cambiar de grupo <i class="bi bi-chevron-double-right"></i></button>
            </div>
            <a href="#/mis-datos" class="d-flex justify-content-between align-items-center text-start border rounded-4 p-3 mb-2 text-decoration-none text-body">
              <span><span class="fw-bold d-block">Mis datos</span><span class="small text-secondary">Nombre, correo institucional y documento.</span></span>
              <i class="bi bi-chevron-double-right text-primary"></i>
            </a>
            <div class="text-start border rounded-4 p-3 mb-3">
              <span class="fw-bold d-block">Institución</span><span class="small text-secondary">${escapeHtml(yo.institucion)} · solo lectura.</span>
            </div>
            <a href="#/login" class="btn btn-outline-danger w-100" data-action="logout"><i class="bi bi-box-arrow-left me-1"></i> Cerrar sesión</a>
          </div>
        </div>
      </div>
    </div>`;
}

function ModalGrupo() {
  return `
    <div class="modal fade" id="modalGrupo" tabindex="-1" aria-labelledby="grupoTitulo" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <div>
              <h2 class="modal-title fs-5" id="grupoTitulo">Cambiar de grupo</h2>
              <p class="small text-secondary mb-0">El panel, los estudiantes, las actividades y los reportes pasan al grupo que elijas.</p>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
          </div>
          <div class="modal-body" id="listaGrupos"></div>
          <div class="modal-footer justify-content-start small text-secondary">
            <i class="bi bi-question-circle"></i> ¿Falta un grupo? La coordinación de la sede lo habilita con el código de la institución.
          </div>
        </div>
      </div>
    </div>`;
}

export function Layout(vista, pagina) {
  return `
    <div class="app">
      ${Sidebar(vista)}
      <div class="app-main">
        ${BarraDelGrupo()}
        ${pagina}
      </div>
    </div>
    <div class="toast-container position-fixed bottom-0 end-0 p-3" id="toastArea"></div>
    ${ModalPerfil()}
    ${ModalGrupo()}`;
}

function pintarListaDeGrupos(recargar) {
  const lista = $('#listaGrupos');
  lista.replaceChildren();

  Object.values(estado.grupos).forEach((g) => {
    const actual = g.id === estado.activo;
    const fila = el('div', `group-option${actual ? ' is-current' : ''}`);
    const info = el('div', 'flex-grow-1');
    info.append(
      el('div', 'fw-bold', g.nombre),
      el('div', 'small text-secondary', `${g.estudiantes} estudiantes · avance ${g.avance}% · ${g.activos} activos · código ${g.codigo}`),
    );
    fila.append(el('span', 'group-badge', g.grado), info);

    if (actual) {
      fila.append(el('span', 'status status-success', 'Grupo actual'));
    } else {
      const boton = el('button', 'btn btn-primary btn-sm', 'Entrar');
      boton.type = 'button';
      boton.addEventListener('click', async () => {
        try {
          await elegirGrupo(g.id);
          await cargarPerfil();
        } catch (error) {
          return mostrarError(error);
        }
        Modal.getInstance($('#modalGrupo'))?.hide();
        await recargar();
        showToast(`Ahora ves ${g.nombre}.`);
      });
      fila.append(boton);
    }
    lista.appendChild(fila);
  });
}

// `recargar` vuelve a dibujar la pantalla actual (con el grupo nuevo)
export function mountLayout({ recargar }) {
  $('#modalGrupo').addEventListener('show.bs.modal', () => pintarListaDeGrupos(recargar));

  // "Cambiar de grupo" vive en la ventana del profesor: se cierra esa y, al terminar, se abre la lista de grupos
  $('#btnCambiarGrupo').addEventListener('click', () => {
    $('#modalPerfil').addEventListener('hidden.bs.modal', () => Modal.getOrCreateInstance('#modalGrupo').show(), { once: true });
    Modal.getOrCreateInstance('#modalPerfil').hide();
  });
}

// Escribe los datos del grupo activo en todos los textos marcados con data-group (también en la pantalla abierta)
export function pintarGrupo() {
  const g = grupo();
  $$('[data-group]').forEach((nodo) => {
    const valor = g[nodo.dataset.group];
    if (valor !== undefined) nodo.textContent = valor;
  });
}

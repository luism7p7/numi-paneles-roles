import { getInicio } from '../api/inicio.api.js';
import { statusSpan } from '../utils/badges.js';
import { $, $$, el } from '../utils/dom.js';
import { plural } from '../utils/formatters.js';
import { mostrarError } from '../utils/toast.js';

export function InicioPage() {
  return `<header class="topbar">
        <button class="btn btn-light d-lg-none" type="button" data-bs-toggle="offcanvas" data-bs-target="#sidebar" aria-controls="sidebar" aria-label="Abrir menú"><i class="bi bi-list"></i></button>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb"><li class="breadcrumb-item active" aria-current="page">Inicio</li></ol>
        </nav>
        <div class="topbar-actions">
          <span class="text-secondary small d-flex align-items-center gap-1"><i class="bi bi-clock-history"></i> Datos al 29 ago, 14:20</span>
        </div>
      </header>

<main class="app-content">
        <div class="page-header">
          <div>
            <h1 class="page-title">Panel administrativo</h1>
            <p class="page-subtitle">Resumen general de la red de instituciones que usan Numi.</p>
          </div>
        </div>

        <!-- Indicadores -->
        <div class="row g-3 mb-4">
          <div class="col-6 col-xl-3">
            <div class="card stat-card">
              <span class="stat-icon icon-teal"><i class="bi bi-building"></i></span>
              <div><div class="stat-value">—</div><div class="stat-label">Instituciones</div></div>
            </div>
          </div>
          <div class="col-6 col-xl-3">
            <div class="card stat-card">
              <span class="stat-icon icon-sky"><i class="bi bi-person-video3"></i></span>
              <div><div class="stat-value">—</div><div class="stat-label">Docentes</div></div>
            </div>
          </div>
          <div class="col-6 col-xl-3">
            <div class="card stat-card">
              <span class="stat-icon icon-amber"><i class="bi bi-collection"></i></span>
              <div><div class="stat-value">—</div><div class="stat-label">Grupos</div></div>
            </div>
          </div>
          <div class="col-6 col-xl-3">
            <div class="card stat-card">
              <span class="stat-icon icon-emerald"><i class="bi bi-mortarboard"></i></span>
              <div><div class="stat-value">—</div><div class="stat-label">Estudiantes</div></div>
            </div>
          </div>
        </div>

        <div class="row g-4 mb-4">
          <!-- Cobertura -->
          <div class="col-lg-7">
            <div class="card h-100">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h2 class="card-title">Cobertura por comuna y corregimiento</h2>
                <span class="small text-secondary">Estudiantes</span>
              </div>
              <div class="card-body p-4" id="coberturaComunas">
              </div>
            </div>
          </div>

          <!-- Requieren acción -->
          <div class="col-lg-5">
            <div class="card h-100" id="cardAcciones">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h2 class="card-title">Requieren acción</h2>
                <span class="badge rounded-pill text-bg-danger">0</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Accesos rápidos -->
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">Accesos rápidos</h2>
            <p class="small text-secondary mb-0">Atajos a lo que hay en cada sección.</p>
          </div>
          <div class="card-body">
            <div class="row g-3">
              <div class="col-6 col-md-4 col-xl"><a href="#/recursos" class="quick-link"><i class="bi bi-cloud-arrow-up"></i> Subir recursos</a></div>
              <div class="col-6 col-md-4 col-xl"><a href="#/institucion-nueva" class="quick-link"><i class="bi bi-building-add"></i> Crear institución</a></div>
              <div class="col-6 col-md-6 col-xl"><a href="#/usuarios?crear=1" class="quick-link"><i class="bi bi-person-plus"></i> Crear usuario</a></div>
              <div class="col-12 col-md-6 col-xl"><a href="#/monitoreo" class="quick-link"><i class="bi bi-activity"></i> Monitoreo técnico</a></div>
            </div>
          </div>
        </div>
      </main>`;
}

function itemAccion(punto, titulo, detalle, extra) {
  const item = el('div', 'action-item');
  const info = el('div', 'flex-grow-1');
  info.append(el('div', 'fw-semibold', titulo), el('div', 'cell-sub', detalle));
  item.append(el('span', `action-dot ${punto}`), info);
  if (extra) item.appendChild(extra);
  return item;
}

function enlaceBoton(texto, href) {
  const a = el('a', 'btn btn-sm btn-soft', texto);
  a.href = href;
  return a;
}

export async function mountInicioPage() {
  const cuerpoCobertura = $('#coberturaComunas');
  const cardAcciones = $('#cardAcciones');
  let datos;
  try {
    datos = await getInicio();
  } catch (error) {
    return mostrarError(error);
  }

  const t = datos.totales;
  const valores = [t.instituciones, t.docentes, t.grupos, t.estudiantes];
  $$('.stat-card .stat-value').forEach((nodo, i) => {
    nodo.textContent = valores[i];
  });
  const fecha = $('.topbar-actions span');
  if (fecha) fecha.lastChild.textContent = ` Datos al ${datos.fecha}`;

  // Cobertura por comuna: la barra más larga es la comuna con más estudiantes
  const maximo = Math.max(1, ...datos.cobertura.map((c) => c.estudiantes));
  cuerpoCobertura.replaceChildren(
    ...datos.cobertura.map((c) => {
      const fila = el('div', 'coverage-row');
      const cabecera = el('div', 'd-flex justify-content-between small mb-1');
      cabecera.append(el('span', 'fw-semibold', c.comuna), el('span', 'fw-bold', c.estudiantes));
      const barra = el('div', 'progress');
      barra.setAttribute('role', 'progressbar');
      barra.setAttribute('aria-label', c.comuna);
      barra.setAttribute('aria-valuenow', c.estudiantes);
      barra.setAttribute('aria-valuemin', 0);
      barra.setAttribute('aria-valuemax', maximo);
      const relleno = el('div', 'progress-bar');
      relleno.style.width = `${Math.round((c.estudiantes * 100) / maximo)}%`;
      barra.appendChild(relleno);
      fila.append(cabecera, barra);
      return fila;
    }),
  );

  // Requieren acción
  const acciones = [];
  if (t.pendientes) {
    acciones.push(
      itemAccion(
        'bg-warning',
        `${plural(t.pendientes, 'docente pendiente', 'docentes pendientes')} de aprobación`,
        'Esperan entrar a su grupo',
        enlaceBoton('Revisar', '#/usuarios?estado=Pendiente'),
      ),
    );
  }
  if (datos.sin_sincronizar) {
    acciones.push(
      itemAccion('bg-warning', `${plural(datos.sin_sincronizar, 'dispositivo', 'dispositivos')} sin sincronizar`, 'Más de 7 días sin conexión', enlaceBoton('Ver', '#/monitoreo')),
    );
  }
  datos.servicios_caidos.forEach((s) => {
    acciones.push(
      itemAccion(
        'bg-danger',
        `${s.nombre} sin responder desde las ${s.desde}`,
        s.clave === 'contenido' ? 'Asistente de IA afectado' : 'La app no puede sincronizar el progreso',
        statusSpan('Crítico'),
      ),
    );
  });
  $('.badge', cardAcciones).textContent = acciones.length;
  if (!acciones.length) acciones.push(itemAccion('bg-success', 'Todo en orden', 'No hay tareas pendientes.'));
  cardAcciones.append(...acciones);
}

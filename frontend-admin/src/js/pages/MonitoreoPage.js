import { descargarInforme, generarInforme, getMonitoreo } from '../api/monitoreo.api.js';
import { statusSpan } from '../utils/badges.js';
import { guardarArchivo } from '../utils/descargas.js';
import { $, $$, el, icono } from '../utils/dom.js';
import { mostrarError, showToast } from '../utils/toast.js';

export function MonitoreoPage() {
  return `<header class="topbar">
        <button class="btn btn-light d-lg-none" type="button" data-bs-toggle="offcanvas" data-bs-target="#sidebar" aria-controls="sidebar" aria-label="Abrir menú"><i class="bi bi-list"></i></button>
        <a href="#/inicio" class="btn-back"><i class="bi bi-arrow-left"></i> Volver</a>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="#/inicio">Inicio</a></li>
            <li class="breadcrumb-item active" aria-current="page">Monitoreo técnico</li>
          </ol>
        </nav>
        <div class="topbar-actions align-items-center">
          <span class="small text-secondary d-none d-md-inline"><i class="bi bi-arrow-repeat me-1"></i>Actualizado hace 3 minutos</span>
          <button type="button" class="btn btn-primary btn-sm" id="btnInforme"><i class="bi bi-download me-1"></i> Descargar informe</button>
        </div>
      </header>

<main class="app-content">
        <div class="page-header">
          <div>
            <h1 class="page-title">Monitoreo técnico</h1>
            <p class="page-subtitle">Estado de los servicios y de los equipos de los estudiantes.</p>
          </div>
        </div>

        <!-- Estado de servicios -->
        <div class="row g-3 mb-4">
          <div class="col-sm-6 col-xl-3">
            <div class="card p-3 h-100">
              <div class="small text-secondary mb-2"><i class="bi bi-database me-1"></i> Firestore</div>
              <div class="service-status text-success"><span class="pulse bg-success"></span> Operativo</div>
            </div>
          </div>
          <div class="col-sm-6 col-xl-3">
            <div class="card p-3 h-100 border-danger-subtle">
              <div class="small text-secondary mb-2"><i class="bi bi-robot me-1"></i> RAG API</div>
              <div class="service-status text-danger"><span class="pulse bg-danger"></span> Sin respuesta</div>
            </div>
          </div>
          <div class="col-sm-6 col-xl-3">
            <div class="card p-3 h-100">
              <div class="small text-secondary mb-2"><i class="bi bi-cloud-slash me-1"></i> Sin sincronizar</div>
              <div class="stat-value text-warning-emphasis">—</div>
            </div>
          </div>
          <div class="col-sm-6 col-xl-3">
            <div class="card p-3 h-100">
              <div class="small text-secondary mb-2"><i class="bi bi-bug me-1"></i> Errores 24 h</div>
              <div class="stat-value">—</div>
            </div>
          </div>
        </div>

        <div class="row g-4 mb-4">
          <!-- Informes recientes -->
          <div class="col-lg-7">
            <div class="card h-100" id="cardInformes">
              <div class="card-header">
                <h2 class="card-title">Informes recientes</h2>
                <p class="small text-secondary mb-0">Genera uno nuevo con el botón Descargar informe.</p>
              </div>
              <div class="card-footer bg-transparent small text-secondary"></div>
            </div>
          </div>

          <!-- Versiones de la app -->
          <div class="col-lg-5">
            <div class="card h-100">
              <div class="card-header d-flex justify-content-between align-items-center gap-2">
                <div>
                  <h2 class="card-title">Versiones de la app en uso</h2>
                  <p class="small text-secondary mb-0">Consulta qué versión de Numi tiene cada equipo.</p>
                </div>
                <button class="btn btn-sm btn-soft text-nowrap" type="button" data-bs-toggle="collapse" data-bs-target="#versiones" aria-expanded="false" aria-controls="versiones" id="btnVersiones">Ver versiones</button>
              </div>
              <div class="collapse" id="versiones">
                <div class="card-body">
                                  </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Registro de eventos -->
        <div class="card" id="cardEventos">
          <div class="card-header"><h2 class="card-title">Registro de eventos</h2></div>
        </div>
      </main>`;
}

async function cargarMonitoreo(cardInformes, cardEventos) {
  let datos;
  try {
    datos = await getMonitoreo();
  } catch (error) {
    return mostrarError(error);
  }

  const actualizado = $('.topbar-actions span.small');
  if (actualizado) actualizado.lastChild.textContent = `Actualizado a las ${datos.actualizado}`;

  // Estado de los servicios del backend de la app
  const ESTADOS = {
    true: ['text-success', 'bg-success', 'Operativo'],
    false: ['text-danger', 'bg-danger', 'Sin respuesta'],
    null: ['text-secondary', 'bg-secondary', 'Sin configurar'],
  };
  $$('.service-status').forEach((nodo, i) => {
    const servicio = datos.servicios[i];
    if (!servicio) return;
    const [texto, punto, etiqueta] = ESTADOS[servicio.operativo];
    nodo.className = `service-status ${texto}`;
    nodo.replaceChildren(el('span', `pulse ${punto}`), ` ${etiqueta}`);
    nodo.closest('.card').classList.toggle('border-danger-subtle', servicio.operativo === false);
  });
  const [sinSync, errores] = $$('.stat-value');
  sinSync.textContent = datos.sin_sincronizar;
  errores.textContent = datos.errores_24h;

  // Informes recientes
  $$('.report-item', cardInformes).forEach((n) => n.remove());
  const pie = $('.card-footer', cardInformes);
  datos.informes.forEach((inf) => {
    const item = el('div', 'report-item');
    const vista = el('span', 'thumb-sm');
    vista.appendChild(icono(inf.formato === 'PDF' ? 'bi-filetype-pdf' : 'bi-filetype-csv'));
    const info = el('div', 'flex-grow-1');
    info.append(el('div', 'fw-semibold', inf.titulo), el('div', 'cell-sub', `${inf.formato} · ${inf.tamano}`));
    const descargar = el('button', 'btn btn-sm btn-light');
    descargar.type = 'button';
    descargar.setAttribute('aria-label', 'Descargar');
    descargar.appendChild(icono('bi-download'));
    descargar.addEventListener('click', () => guardarArchivo(() => descargarInforme(inf.id)));
    item.append(vista, info, descargar);
    pie.before(item);
  });
  pie.textContent = `Son ${datos.equipos} equipos con datos sincronizados.`;

  // Versiones de la app en uso
  const filas = datos.versiones.map((v) => {
    const fila = el('div', 'coverage-row');
    const cabecera = el('div', 'd-flex justify-content-between small mb-1');
    cabecera.append(el('span', 'fw-semibold', `v${v.version}`), el('span', 'fw-bold', v.equipos));
    const barra = el('div', 'progress');
    const relleno = el('div', `progress-bar${v.desactualizada ? ' bg-warning' : ''}`);
    relleno.style.width = `${v.porcentaje}%`;
    barra.appendChild(relleno);
    fila.append(cabecera, barra);
    return fila;
  });
  if (datos.desactualizados.equipos) {
    filas.push(el('div', 'alert alert-warning small mt-3 mb-0', `${datos.desactualizados.equipos} equipos con versión desactualizada no reciben actividades nuevas.`));
  }
  $('#versiones .card-body').replaceChildren(...filas);

  // Registro de eventos
  $$('.event-item', cardEventos).forEach((n) => n.remove());
  datos.eventos.forEach((ev) => {
    const item = el('div', 'event-item');
    item.append(statusSpan(ev.nivel), el('span', '', ev.mensaje), el('span', 'event-time', ev.fecha));
    cardEventos.appendChild(item);
  });
  if (!datos.eventos.length) cardEventos.appendChild(el('div', 'event-item text-secondary', 'Sin eventos registrados.'));
}

export function mountMonitoreoPage() {
  const cardInformes = $('#cardInformes');
  const cardEventos = $('#cardEventos');
  $('#btnInforme').addEventListener('click', async () => {
    showToast('Generando informe… aparecerá en Informes recientes.');
    try {
      await generarInforme();
    } catch (error) {
      return mostrarError(error);
    }
    cargarMonitoreo(cardInformes, cardEventos);
  });
  cargarMonitoreo(cardInformes, cardEventos);

  const versiones = $('#versiones');
  versiones.addEventListener('shown.bs.collapse', () => {
    $('#btnVersiones').textContent = 'Ocultar';
  });
  versiones.addEventListener('hidden.bs.collapse', () => {
    $('#btnVersiones').textContent = 'Ver versiones';
  });
}

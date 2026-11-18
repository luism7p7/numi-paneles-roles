import { getHistorial } from '../api/actividades.api.js';
import { aplicarFiltros } from '../components/tablas/filtros.js';
import { statusSpan } from '../utils/badges.js';
import { $, el } from '../utils/dom.js';
import { fechaISO } from '../utils/formatters.js';
import { mostrarError } from '../utils/toast.js';

export function HistorialPage() {
  return `<header class="topbar">
        <button class="btn btn-light d-lg-none" type="button" data-bs-toggle="offcanvas" data-bs-target="#sidebar" aria-controls="sidebar" aria-label="Abrir menú"><i class="bi bi-list"></i></button>
        <a href="#/actividades" class="btn-back"><i class="bi bi-arrow-left"></i> Volver</a>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="#/inicio">Inicio</a></li>
            <li class="breadcrumb-item"><a href="#/actividades">Actividades</a></li>
            <li class="breadcrumb-item active" aria-current="page">Historial</li>
          </ol>
        </nav>
      </header>

<main class="app-content">
        <div class="page-header">
          <div>
            <h1 class="page-title">Historial de actividades</h1>
            <p class="page-subtitle">Cada cambio guardado en el panel queda registrado aquí.</p>
          </div>
        </div>

        <form class="filters" data-table-filter="#tablaHistorial">
          <div class="row g-3 align-items-end">
            <div class="col-md-6 col-xl-4">
              <label class="form-label" for="buscarHist">Buscar actividad</label>
              <div class="input-group">
                <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
                <input type="search" class="form-control" id="buscarHist" placeholder="Nombre de la actividad" data-filter="text">
              </div>
            </div>
            <div class="col-md-6 col-xl-4">
              <label class="form-label" for="tipoCambio">Tipo de cambio</label>
              <select class="form-select" id="tipoCambio" data-filter="estado">
                <option value="">Todos los cambios</option>
                <option>Editada</option>
                <option>Borrador</option>
                <option>Desactivada</option>
                <option>Publicada</option>
              </select>
            </div>
            <div class="col-6 col-xl-2">
              <label class="form-label" for="desde">Desde</label>
              <input type="date" class="form-control" id="desde" value="2026-08-01">
            </div>
            <div class="col-6 col-xl-2">
              <label class="form-label" for="hasta">Hasta</label>
              <input type="date" class="form-control" id="hasta" value="2026-08-29">
            </div>
          </div>
        </form>

        <div class="notice">
          <i class="bi bi-info-circle"></i>
          <div>Datos de ejemplo: el historial real se arma con cada cambio guardado en el panel.</div>
        </div>

        <div class="card table-card">
          <div class="table-responsive">
            <table class="table table-hover" id="tablaHistorial">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Actividad</th>
                  <th>Cambio</th>
                  <th>Estado</th>
                  <th>Hecho por</th>
                </tr>
              </thead>
              <tbody>
              </tbody>
            </table>
          </div>
          <div class="table-footer">
            <span><span data-visible>0</span> cambios</span>
          </div>
        </div>
      </main>`;
}

export async function mountHistorialPage() {
  const tbody = $('#tablaHistorial tbody');
  tbody.replaceChildren();
  // Filtros de fecha: por defecto, todo el año en curso
  const hoy = new Date();
  $('#desde').dataset.filter = 'desde';
  $('#hasta').dataset.filter = 'hasta';
  $('#desde').value = `${hoy.getFullYear()}-01-01`;
  $('#hasta').value = fechaISO(hoy);

  let datos;
  try {
    datos = await getHistorial();
  } catch (error) {
    return mostrarError(error);
  }
  datos.forEach((h) => {
    const tr = el('tr');
    Object.assign(tr.dataset, { estado: h.tipo, dia: h.dia });
    const tdEstado = el('td');
    tdEstado.appendChild(statusSpan(h.tipo));
    tr.append(el('td', 'text-nowrap', h.fecha), el('td', 'cell-title', h.actividad), el('td', '', h.cambio), tdEstado, el('td', 'text-nowrap', h.hecho_por));
    tbody.appendChild(tr);
  });
  aplicarFiltros('#tablaHistorial');
}

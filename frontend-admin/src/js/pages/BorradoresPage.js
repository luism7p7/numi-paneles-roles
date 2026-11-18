import { getActividades } from '../api/actividades.api.js';
import { statusSpan } from '../utils/badges.js';
import { $, el } from '../utils/dom.js';
import { filaVacia, plural } from '../utils/formatters.js';
import { mostrarError } from '../utils/toast.js';
import { mensajesDeActividades } from './ActividadesPage.js';

export function BorradoresPage() {
  return `<header class="topbar">
        <button class="btn btn-light d-lg-none" type="button" data-bs-toggle="offcanvas" data-bs-target="#sidebar" aria-controls="sidebar" aria-label="Abrir menú"><i class="bi bi-list"></i></button>
        <a href="#/actividades" class="btn-back"><i class="bi bi-arrow-left"></i> Volver</a>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="#/inicio">Inicio</a></li>
            <li class="breadcrumb-item"><a href="#/actividades">Actividades</a></li>
            <li class="breadcrumb-item active" aria-current="page">Borradores</li>
          </ol>
        </nav>
        <div class="topbar-actions">
          <a href="#/historial" class="btn btn-outline-secondary btn-sm"><i class="bi bi-clock-history me-1"></i> Historial</a>
          <a href="#/constructor" class="btn btn-primary btn-sm"><i class="bi bi-plus-lg me-1"></i> Nueva actividad</a>
        </div>
      </header>

<main class="app-content">
        <div class="page-header">
          <div>
            <h1 class="page-title">Contenido educativo</h1>
            <p class="page-subtitle">Actividades guardadas que todavía no se publican.</p>
          </div>
        </div>

        <ul class="nav section-tabs">
          <li class="nav-item"><a class="nav-link" href="#/actividades">Actividades <span class="badge ms-1">0</span></a></li>
          <li class="nav-item"><a class="nav-link active" href="#/borradores">Borradores</a></li>
        </ul>

        <div id="flash"></div>

        <div class="notice">
          <i class="bi bi-info-circle"></i>
          <div>Los borradores <strong>no llegan</strong> al celular del niño hasta que se publican.</div>
        </div>

        <div class="card table-card">
          <div class="table-responsive">
            <table class="table table-hover" id="tablaBorradores">
              <thead>
                <tr>
                  <th>Actividad</th>
                  <th>Materia</th>
                  <th>Grado</th>
                  <th>Tipo</th>
                  <th>Estado</th>
                  <th class="text-end">Acción</th>
                </tr>
              </thead>
              <tbody>
              </tbody>
            </table>
          </div>
          <div class="table-footer">
            <span id="draftCount">1 borrador</span>
          </div>
        </div>
      </main>`;
}

export async function mountBorradoresPage({ query }) {
  const tbody = $('#tablaBorradores tbody');
  tbody.replaceChildren();
  mensajesDeActividades(query);
  let datos;
  try {
    datos = await getActividades();
  } catch (error) {
    return mostrarError(error);
  }

  const borradores = datos.filter((a) => a.estado === 'Borrador');
  borradores.forEach((a) => {
    const tr = el('tr');
    tr.dataset.id = a.id;
    const tdEstado = el('td');
    tdEstado.appendChild(statusSpan(a.estado));
    const tdAccion = el('td', 'text-end');
    const continuar = el('a', 'btn btn-sm btn-soft', 'Continuar editando');
    continuar.href = `#/constructor?id=${encodeURIComponent(a.id)}`;
    tdAccion.appendChild(continuar);
    tr.append(el('td', 'cell-title', a.nombre), el('td', '', a.materia), el('td', '', `Grado ${a.grado}`), el('td', '', a.tipo), tdEstado, tdAccion);
    tbody.appendChild(tr);
  });
  if (!borradores.length) filaVacia(tbody, 6, 'No hay borradores guardados.');
  $('#draftCount').textContent = plural(borradores.length, 'borrador', 'borradores');
  const badge = $('.section-tabs .badge');
  if (badge) badge.textContent = datos.length;
}

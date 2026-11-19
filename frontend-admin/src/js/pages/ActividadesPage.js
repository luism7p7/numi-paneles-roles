import { getActividades } from '../api/actividades.api.js';
import { aplicarFiltros } from '../components/tablas/filtros.js';
import { statusSpan } from '../utils/badges.js';
import { $, botonVer, el } from '../utils/dom.js';
import { filaVacia } from '../utils/formatters.js';
import { mostrarError, showFlash } from '../utils/toast.js';

export function ActividadesPage() {
  return `<header class="topbar">
        <button class="btn btn-light d-lg-none" type="button" data-bs-toggle="offcanvas" data-bs-target="#sidebar" aria-controls="sidebar" aria-label="Abrir menú"><i class="bi bi-list"></i></button>
        <a href="#/inicio" class="btn-back"><i class="bi bi-arrow-left"></i> Volver</a>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="#/inicio">Inicio</a></li>
            <li class="breadcrumb-item active" aria-current="page">Actividades</li>
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
            <p class="page-subtitle">Actividades que llegan al celular de los estudiantes.</p>
          </div>
        </div>

        <ul class="nav section-tabs">
          <li class="nav-item"><a class="nav-link active" href="#/actividades">Actividades <span class="badge ms-1" data-count>0</span></a></li>
          <li class="nav-item"><a class="nav-link" href="#/borradores">Borradores</a></li>
        </ul>

        <!-- Mensaje de resultado (lo muestra app.js) -->
        <div id="flash"></div>

        <!-- Filtros -->
        <form class="filters" data-table-filter="#tablaActividades">
          <div class="row g-3 align-items-end">
            <div class="col-md-6 col-xl-3">
              <label class="form-label" for="buscar">Buscar</label>
              <div class="input-group">
                <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
                <input type="search" class="form-control" id="buscar" placeholder="Nombre de la actividad" data-filter="text">
              </div>
            </div>
            <div class="col-md-6 col-xl-3">
              <label class="form-label" for="materia">Materia</label>
              <select class="form-select" id="materia" data-filter="materia">
                <option value="">Todas las materias</option>
                <option>Matemáticas</option>
                <option>Español</option>
                <option>Ciencias naturales</option>
                <option>Sociales</option>
                <option>Inglés</option>
              </select>
            </div>
            <div class="col-md-6 col-xl-3">
              <label class="form-label" for="grado">Grado</label>
              <select class="form-select" id="grado" data-filter="grado">
                <option value="">Todos los grados</option>
                <option>1°</option><option>2°</option><option>3°</option><option>4°</option><option>5°</option>
              </select>
            </div>
            <div class="col-md-6 col-xl-3">
              <label class="form-label" for="estado">Estado</label>
              <select class="form-select" id="estado" data-filter="estado">
                <option value="">Todos los estados</option>
                <option>Publicada</option>
                <option>Borrador</option>
                <option>Desactivada</option>
              </select>
            </div>
          </div>
        </form>

        <div class="notice">
          <i class="bi bi-phone"></i>
          <div>Los cambios llegan al celular del niño en su <strong>próxima sincronización</strong>, no de inmediato. Toca el ojo <i class="bi bi-eye"></i> de cada fila para abrir la información completa de esa actividad.</div>
        </div>

        <!-- Tabla -->
        <div class="card table-card">
          <div class="table-responsive">
            <table class="table table-hover" id="tablaActividades">
              <thead>
                <tr>
                  <th>Actividad</th>
                  <th>Materia</th>
                  <th>Grado</th>
                  <th>Tipo</th>
                  <th>Estado</th>
                  <th class="text-end">Detalle</th>
                </tr>
              </thead>
              <tbody>
              </tbody>
            </table>
          </div>
          <div class="table-footer">
            <span><span data-visible>0</span> de <span data-total>0</span> actividades</span>
            <nav aria-label="Paginación">
              <ul class="pagination pagination-sm"></ul>
            </nav>
          </div>
        </div>
      </main>`;
}

// Avisos que dejan el constructor y el detalle al volver a las listas (borradores también los usa)
export function mensajesDeActividades(query) {
  if (query.get('msg') === 'publicada') showFlash('Actividad publicada. Llega al celular del niño en su próxima sincronización.');
  if (query.get('msg') === 'cambios') showFlash('Cambios publicados. Llegan al celular del niño en su próxima sincronización.');
  if (query.get('msg') === 'borrador') showFlash('Actividad guardada como borrador.');
  if (query.get('eliminada')) showFlash(`Se eliminó la actividad «${query.get('eliminada')}».`);
}

export async function mountActividadesPage({ query }) {
  const tbody = $('#tablaActividades tbody');
  tbody.replaceChildren();
  mensajesDeActividades(query);
  let datos;
  try {
    datos = await getActividades();
  } catch (error) {
    return mostrarError(error);
  }

  datos.forEach((a) => {
    const tr = el('tr');
    Object.assign(tr.dataset, { id: a.id, materia: a.materia, grado: a.grado, estado: a.estado });
    const tdEstado = el('td');
    tdEstado.appendChild(statusSpan(a.estado));
    const tdDetalle = el('td', 'text-end');
    const ver = botonVer('Ver detalle', 'a');
    ver.href = `#/actividad-detalle?id=${encodeURIComponent(a.id)}`;
    tdDetalle.appendChild(ver);
    tr.append(el('td', 'cell-title', a.nombre), el('td', '', a.materia), el('td', '', a.grado), el('td', '', a.tipo), tdEstado, tdDetalle);
    tbody.appendChild(tr);
  });
  if (!datos.length) filaVacia(tbody, 6, 'Todavía no hay actividades. Crea la primera con «Nueva actividad».');
  $('[data-total]').textContent = datos.length;
  $('[data-count]').textContent = datos.length;
  aplicarFiltros('#tablaActividades');
}

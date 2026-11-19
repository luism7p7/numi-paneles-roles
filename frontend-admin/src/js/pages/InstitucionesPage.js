import { getInstitucion, getInstituciones } from '../api/instituciones.api.js';
import { aplicarFiltros } from '../components/tablas/filtros.js';
import { statusSpan } from '../utils/badges.js';
import { $, botonVer, el } from '../utils/dom.js';
import { fijarTotal } from '../utils/formatters.js';
import { mostrarError, showFlash } from '../utils/toast.js';

export function InstitucionesPage() {
  return `<header class="topbar">
        <button class="btn btn-light d-lg-none" type="button" data-bs-toggle="offcanvas" data-bs-target="#sidebar" aria-controls="sidebar" aria-label="Abrir menú"><i class="bi bi-list"></i></button>
        <a href="#/inicio" class="btn-back"><i class="bi bi-arrow-left"></i> Volver</a>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="#/inicio">Inicio</a></li>
            <li class="breadcrumb-item active" aria-current="page">Instituciones</li>
          </ol>
        </nav>
        <div class="topbar-actions">
          <a href="#/institucion-nueva" class="btn btn-primary btn-sm"><i class="bi bi-building-add me-1"></i> Crear institución</a>
        </div>
      </header>

<main class="app-content">
        <div class="page-header">
          <div>
            <h1 class="page-title">Instituciones y grupos</h1>
            <p class="page-subtitle">Sedes educativas conectadas a Numi.</p>
          </div>
        </div>

        <div id="flash"></div>

        <form class="filters" data-table-filter="#tablaInstituciones">
          <div class="row g-3 align-items-end">
            <div class="col-md-4">
              <label class="form-label" for="buscarInst">Buscar</label>
              <div class="input-group">
                <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
                <input type="search" class="form-control" id="buscarInst" placeholder="Nombre de la institución" data-filter="text">
              </div>
            </div>
            <div class="col-md-4">
              <label class="form-label" for="comuna">Comuna o corregimiento</label>
              <select class="form-select" id="comuna" data-filter="comuna">
                <option value="">Todas</option>
                <option>San Cristóbal</option>
                <option>Palmitas</option>
                <option>Santa Elena</option>
                <option>Altavista</option>
                <option>San Antonio de Prado</option>
              </select>
            </div>
            <div class="col-md-4">
              <label class="form-label" for="estadoInst">Estado</label>
              <select class="form-select" id="estadoInst" data-filter="estado">
                <option value="">Todos los estados</option>
                <option>Activa</option>
                <option>Inactiva</option>
              </select>
            </div>
          </div>
        </form>

        <div class="notice">
          <i class="bi bi-hand-index"></i>
          <div>Toca el ojo <i class="bi bi-eye"></i> de cada fila para abrir la información completa de esa institución.</div>
        </div>

        <div class="card table-card">
          <div class="table-responsive">
            <table class="table table-hover" id="tablaInstituciones">
              <thead>
                <tr><th>Institución</th><th>Comuna o corregimiento</th><th>Sedes</th><th>Estudiantes</th><th>Estado</th><th class="text-end">Detalle</th></tr>
              </thead>
              <tbody>
              </tbody>
            </table>
          </div>
          <div class="table-footer">
            <span><span data-visible>0</span> de 0 instituciones</span>
            <ul class="pagination pagination-sm"></ul>
          </div>
        </div>
      </main>

<div class="modal fade" id="modalInstitucion" tabindex="-1" aria-labelledby="modalInstitucionTitulo" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <div>
            <p class="small text-secondary mb-0">Detalle de la institución</p>
            <h2 class="modal-title fs-5" id="modalInstitucionTitulo">Institución</h2>
          </div>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
        </div>
        <div class="modal-body">
          <div class="row g-3 mb-3">
            <div class="col-4"><div class="border rounded-3 p-3 text-center"><div class="small text-secondary">Estado</div><div class="fw-bold text-success" id="instEstado">Activa</div></div></div>
            <div class="col-4"><div class="border rounded-3 p-3 text-center"><div class="small text-secondary">Sedes</div><div class="fw-bold" id="instSedes">2</div></div></div>
            <div class="col-4"><div class="border rounded-3 p-3 text-center"><div class="small text-secondary">Estudiantes</div><div class="fw-bold" id="instEstudiantes">198</div></div></div>
          </div>
          <p class="small mb-3"><i class="bi bi-geo-alt me-1 text-primary"></i> Comuna o corregimiento: <strong id="instComuna">San Cristóbal</strong></p>
          <h3 class="h6 fw-bold">Grupos</h3>
          <ul class="list-group" id="instGrupos"></ul>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-primary" data-bs-dismiss="modal">Cerrar</button>
        </div>
      </div>
    </div>
  </div>`;
}

export async function mountInstitucionesPage({ query }) {
  const tbody = $('#tablaInstituciones tbody');
  tbody.replaceChildren();
  if (query.get('msg') === 'institucion') showFlash('Institución creada. Ya puedes agregar sus grupos.');

  $('#modalInstitucion').addEventListener('show.bs.modal', async (e) => {
    const instId = e.relatedTarget?.dataset.inst;
    if (!instId) return;
    const lista = $('#instGrupos');
    lista.replaceChildren();
    let inst;
    try {
      inst = await getInstitucion(instId);
    } catch (error) {
      return mostrarError(error);
    }
    $('#modalInstitucionTitulo').textContent = inst.nombre;
    $('#instEstado').textContent = inst.estado;
    $('#instEstado').className = `fw-bold ${inst.estado === 'Activa' ? 'text-success' : 'text-secondary'}`;
    $('#instComuna').textContent = inst.comuna;
    $('#instSedes').textContent = inst.sedes;
    $('#instEstudiantes').textContent = inst.estudiantes;
    inst.grupos.forEach(({ nombre, docente }) => {
      const li = el('li', 'list-group-item d-flex justify-content-between align-items-center gap-2');
      li.append(el('span', 'fw-semibold', nombre), el('span', docente ? 'small text-secondary text-end' : 'status status-warning', docente || 'Sin docente asignado'));
      lista.appendChild(li);
    });
    if (!inst.grupos.length) lista.appendChild(el('li', 'list-group-item small text-secondary', 'Todavía no tiene grupos.'));
  });

  let datos;
  try {
    datos = await getInstituciones();
  } catch (error) {
    return mostrarError(error);
  }
  datos.forEach((i) => {
    const tr = el('tr');
    Object.assign(tr.dataset, { comuna: i.comuna, estado: i.estado });
    const tdEstado = el('td');
    tdEstado.appendChild(statusSpan(i.estado));
    const tdDetalle = el('td', 'text-end');
    const boton = botonVer('Ver detalle');
    Object.assign(boton.dataset, { bsToggle: 'modal', bsTarget: '#modalInstitucion', inst: i.id });
    tdDetalle.appendChild(boton);
    tr.append(el('td', 'cell-title', i.nombre), el('td', '', i.comuna), el('td', '', i.sedes), el('td', '', i.estudiantes), tdEstado, tdDetalle);
    tbody.appendChild(tr);
  });
  fijarTotal($('[data-visible]', tbody.closest('.card')), datos.length, 'instituciones');
  aplicarFiltros('#tablaInstituciones');
}

import { Modal } from 'bootstrap';

import { activarActividad, getActividades } from '../api/seguimiento.api.js';
import { grupo } from '../state/docente.store.js';
import { statusBadge } from '../utils/badges.js';
import { BAR_CLASS } from '../utils/constantes.js';
import { $, $$, el } from '../utils/dom.js';
import { mostrarError, showToast } from '../utils/toast.js';

export function ActividadesPage() {
  return `<div class="section-bar">
        <a href="#/panel" class="btn-back"><i class="bi bi-arrow-left"></i> Volver</a>
        <h2 class="section-title">Actividades</h2>
      </div>

<main class="app-content">
        <form class="filters" id="filtrosActividades">
          <div class="row g-3 align-items-end">
            <div class="col-md-5">
              <label class="form-label" for="buscarAct">Buscar</label>
              <div class="input-group">
                <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
                <input type="search" class="form-control" id="buscarAct" placeholder="Nombre de la actividad">
              </div>
            </div>
            <div class="col-sm-6 col-md-3">
              <label class="form-label" for="materiaAct">Materia</label>
              <select class="form-select" id="materiaAct">
                <option value="">Todas las materias</option>
                <option>Matemáticas</option>
                <option>Ciencias</option>
                <option>Español</option>
                <option>Sociales</option>
                <option>Inglés</option>
              </select>
            </div>
            <div class="col-sm-6 col-md-4">
              <label class="form-label" for="estadoAct">Estado</label>
              <select class="form-select" id="estadoAct">
                <option value="">Todos los estados</option>
                <option>Activa</option>
                <option>Inactiva</option>
              </select>
            </div>
          </div>
        </form>

        <div class="notice">
          <i class="bi bi-hand-index"></i>
          <div>Toca una actividad para ver su detalle. Las casillas activan o desactivan cada actividad en el grupo.</div>
        </div>

        <div class="card table-card">
          <div class="table-responsive">
            <table class="table table-hover" id="tablaActividades">
              <thead>
                <tr><th>Actividad</th><th>Materia</th><th>Estado</th><th>Detalle</th><th class="text-end">En el grupo</th></tr>
              </thead>
              <tbody>
              </tbody>
            </table>
          </div>
          <div class="table-footer"><span id="contadorActividades">0</span> actividades</div>
        </div>
      </main>

<div class="modal fade" id="modalActividad" tabindex="-1" aria-labelledby="actTitulo" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <div>
            <p class="small text-secondary mb-0">Detalle de la actividad</p>
            <h2 class="modal-title fs-5" id="actTitulo">Los números</h2>
          </div>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
        </div>
        <div class="modal-body">
          <h3 class="h6 fw-bold">De qué se trata</h3>
          <p class="text-secondary" id="actDescripcion">Reconocer del 1 al 20</p>
          <dl class="row detail-list mb-2">
            <dt class="col-6">Materia</dt><dd class="col-6" id="actMateria">Matemáticas</dd>
            <dt class="col-6">Estado</dt><dd class="col-6" id="actEstado">Activa</dd>
          </dl>
          <div class="d-flex justify-content-between small fw-bold mb-1"><span>Avance del grupo</span><span id="actAvanceTxt">88%</span></div>
          <div class="progress mini-progress mb-4" style="height: 10px"><div class="progress-bar" id="actAvanceBar" style="width: 88%"></div></div>
          <h3 class="h6 fw-bold">En las fichas de estudiantes</h3>
          <ul class="list-group list-group-flush" id="actEstudiantes"></ul>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-light" data-bs-dismiss="modal">Cerrar</button>
          <a href="#/estudiantes" class="btn btn-primary">Ver estudiantes</a>
        </div>
      </div>
    </div>
  </div>`;
}

function filtrarActividades() {
  const tabla = $('#tablaActividades');
  const q = $('#buscarAct').value.trim().toLowerCase();
  const materia = $('#materiaAct').value;
  const estadoFiltro = $('#estadoAct').value;
  let visibles = 0;
  $$('tbody tr', tabla).forEach((tr) => {
    const activa = $('input[role="switch"]', tr).checked ? 'Activa' : 'Inactiva';
    const coincide =
      tr.textContent.toLowerCase().includes(q) && (!materia || tr.dataset.materia === materia) && (!estadoFiltro || activa === estadoFiltro);
    tr.classList.toggle('d-none', !coincide);
    if (coincide) visibles++;
  });
  $('#contadorActividades').textContent = visibles;
}

function abrirDetalle(act) {
  $('#actTitulo').textContent = act.nombre;
  $('#actDescripcion').textContent = act.descripcion;
  $('#actMateria').textContent = act.materia;
  $('#actEstado').replaceChildren(statusBadge(act.activa ? 'Activa' : 'Inactiva'));
  $('#actAvanceTxt').textContent = `${act.avance}%`;
  $('#actAvanceBar').style.width = `${act.avance}%`;

  const ul = $('#actEstudiantes');
  ul.replaceChildren();
  if (!act.estudiantes.length) {
    ul.appendChild(el('li', 'list-group-item px-0 text-secondary small', 'Ningún estudiante del grupo la ha empezado.'));
  }
  act.estudiantes.forEach(([nombre, valor]) => {
    const li = el('li', 'list-group-item d-flex justify-content-between align-items-center px-0');
    const clase = valor === 'Completada' ? 'status status-success' : valor === 'Sin empezar' ? 'status status-muted' : 'small fw-bold';
    li.append(el('span', '', nombre), el('span', clase, valor));
    ul.appendChild(li);
  });
  Modal.getOrCreateInstance('#modalActividad').show();
}

function filaActividad(act) {
  const tr = el('tr');
  Object.assign(tr.dataset, { act: act.id, materia: act.materia });

  const tdNombre = el('td');
  const envoltura = el('div', 'd-flex align-items-center gap-3');
  const textos = el('div');
  const titulo = el('div', 'cell-title', act.nombre);
  if (act.mas_errores) titulo.append(' ', el('span', 'badge text-bg-danger-subtle text-danger-emphasis ms-1', 'Más errores'));
  textos.append(titulo, el('div', 'cell-sub', act.descripcion.replace(/\.$/, '')));
  envoltura.append(el('span', `subject-icon ${BAR_CLASS[act.materia_indice]}`, act.materia[0]), textos);
  tdNombre.appendChild(envoltura);

  const tdEstado = el('td');
  tdEstado.dataset.estado = '';
  tdEstado.appendChild(statusBadge(act.activa ? 'Activa' : 'Inactiva'));

  const tdDetalle = el('td');
  const ver = el('button', 'btn btn-sm btn-soft text-nowrap', 'Ver detalle ');
  ver.type = 'button';
  ver.appendChild(el('i', 'bi bi-chevron-right'));
  tdDetalle.appendChild(ver);

  const tdInterruptor = el('td', 'text-end');
  const caja = el('div', 'form-check form-switch d-inline-flex justify-content-end gap-2 mb-0');
  const interruptor = el('input', 'form-check-input');
  interruptor.type = 'checkbox';
  interruptor.setAttribute('role', 'switch');
  interruptor.setAttribute('aria-label', 'Activa para el grupo');
  interruptor.checked = act.activa;
  caja.append(interruptor, el('span', 'small text-nowrap d-none d-md-inline', 'Activa para el grupo'));
  tdInterruptor.appendChild(caja);
  tr.append(tdNombre, el('td', '', act.materia), tdEstado, tdDetalle, tdInterruptor);

  interruptor.addEventListener('change', async () => {
    interruptor.disabled = true;
    try {
      await activarActividad(act.id, interruptor.checked);
    } catch (error) {
      interruptor.disabled = false;
      interruptor.checked = !interruptor.checked;
      return mostrarError(error);
    }
    interruptor.disabled = false;
    act.activa = interruptor.checked;
    tdEstado.replaceChildren(statusBadge(act.activa ? 'Activa' : 'Inactiva'));
    showToast(
      act.activa
        ? `«${act.nombre}» quedó activa para ${grupo().nombre}.`
        : `«${act.nombre}» ya no aparece en los celulares de ${grupo().nombre}.`,
    );
    filtrarActividades();
  });

  ver.addEventListener('click', () => abrirDetalle(act));
  return tr;
}

export async function mountActividadesPage() {
  $('#filtrosActividades').addEventListener('submit', (e) => e.preventDefault());
  $$('#filtrosActividades input, #filtrosActividades select').forEach((c) => c.addEventListener('input', filtrarActividades));

  const tbody = $('#tablaActividades tbody');
  tbody.replaceChildren();
  try {
    const actividades = await getActividades();
    tbody.append(...actividades.map(filaActividad));
  } catch (error) {
    return mostrarError(error);
  }
  filtrarActividades();
}

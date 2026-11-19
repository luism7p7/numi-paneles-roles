import { Modal } from 'bootstrap';

import {
  exportarEstudiantes,
  getEstudiantes,
  getFicha,
  guardarNota as guardarNotaApi,
  informeDeEstudiante,
} from '../api/seguimiento.api.js';
import { estado } from '../state/docente.store.js';
import { statusBadge } from '../utils/badges.js';
import { BAR_CLASS, ICONO_MATERIA, MATERIAS } from '../utils/constantes.js';
import { guardarArchivo } from '../utils/descargas.js';
import { $, $$, botonVer, el, icono } from '../utils/dom.js';
import { mostrarError, showToast } from '../utils/toast.js';

export function EstudiantesPage() {
  return `<div class="section-bar">
        <a href="#/panel" class="btn-back"><i class="bi bi-arrow-left"></i> Volver</a>
        <h2 class="section-title">Estudiantes</h2>
        <div class="section-actions">
          <button type="button" class="btn btn-outline-primary btn-sm" id="btnExportar"><i class="bi bi-download me-1"></i> Exportar</button>
        </div>
      </div>

<main class="app-content">
        <form class="filters" id="filtrosEstudiantes">
          <div class="row g-3 align-items-end">
            <div class="col-md-5">
              <label class="form-label" for="buscarEst">Buscar</label>
              <div class="input-group">
                <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
                <input type="search" class="form-control" id="buscarEst" placeholder="Nombre del estudiante">
              </div>
            </div>
            <div class="col-sm-6 col-md-3">
              <label class="form-label" for="materiaEst">Materia</label>
              <select class="form-select" id="materiaEst">
                <option value="">Todas las materias</option>
                <option value="0">Matemáticas</option>
                <option value="1">Ciencias</option>
                <option value="2">Español</option>
                <option value="3">Sociales</option>
                <option value="4">Inglés</option>
              </select>
            </div>
            <div class="col-sm-6 col-md-4">
              <label class="form-label" for="estadoEst">Estado</label>
              <select class="form-select" id="estadoEst">
                <option value="">Todos los estados</option>
                <option>Al día</option>
                <option>Sin sincronizar</option>
                <option>Inactivo</option>
              </select>
            </div>
          </div>
        </form>

        <div class="card table-card">
          <div class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr><th>Estudiante</th><th id="colAvance">Avance</th><th>Racha</th><th>Estado</th><th class="text-end">Detalle</th></tr>
              </thead>
              <tbody id="tablaEstudiantes">
</tbody>
            </table>
          </div>
          <div class="table-footer">
            <span id="contadorEstudiantes">0 de 0 estudiantes</span> · toca el ojo <i class="bi bi-eye"></i> para abrir la ficha completa.
          </div>
        </div>
      </main>

<div class="modal fade" id="modalFicha" tabindex="-1" aria-labelledby="fichaNombre" aria-hidden="true">
    <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
      <div class="modal-content">
        <div class="modal-header">
          <div class="d-flex align-items-center gap-3">
            <span class="avatar avatar-lg" id="fichaIniciales">MO</span>
            <div>
              <h2 class="modal-title fs-5" id="fichaNombre">Mariana Ospina</h2>
              <div class="small text-secondary" data-group="nombre">Grado 3° — grupo A</div>
            </div>
          </div>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
        </div>
        <div class="modal-body">
          <div class="row g-3 mb-4">
            <div class="col-4"><div class="kpi-box"><div class="label"><i class="bi bi-graph-up-arrow text-primary me-1"></i>Avance</div><div class="value" id="fichaAvance">64%</div></div></div>
            <div class="col-4"><div class="kpi-box"><div class="label"><i class="bi bi-fire text-warning me-1"></i>Racha</div><div class="value" id="fichaRacha">6 d</div></div></div>
            <div class="col-4"><div class="kpi-box"><div class="label"><i class="bi bi-wifi text-info me-1"></i>Estado</div><div class="value fs-6 pt-1" id="fichaEstado"></div></div></div>
          </div>

          <div class="row g-4">
            <div class="col-md-6">
              <h3 class="h6 fw-bold mb-3"><i class="bi bi-bar-chart-line text-primary me-2"></i>Por materia</h3>
              <div id="fichaMaterias"></div>
            </div>
            <div class="col-md-6">
              <h3 class="h6 fw-bold mb-3"><i class="bi bi-puzzle text-primary me-2"></i>Actividades</h3>
              <ul class="list-group list-group-flush mb-4" id="fichaActividades"></ul>
              <h3 class="h6 fw-bold mb-3"><i class="bi bi-clipboard-check text-primary me-2"></i>Evaluación</h3>
              <ul class="list-group list-group-flush" id="fichaEvaluacion"></ul>
            </div>
          </div>

          <div class="mt-4">
            <label class="form-label" for="fichaNota"><i class="bi bi-journal-text text-primary me-2"></i>Nota del docente</label>
            <textarea class="form-control" id="fichaNota" rows="3" placeholder="Escribe una observación sobre el estudiante…"></textarea>
          </div>
        </div>
        <div class="modal-footer justify-content-between">
          <button type="button" class="btn btn-light" data-bs-dismiss="modal"><i class="bi bi-arrow-left me-1"></i> Volver a la lista</button>
          <button type="button" class="btn btn-primary" id="btnInformeEstudiante"><i class="bi bi-file-earmark-pdf me-1"></i> Descargar informe</button>
        </div>
      </div>
    </div>
  </div>`;
}

let fichaActual = null;
let temporizadorNota = null;

async function pintarEstudiantes() {
  const tbody = $('#tablaEstudiantes');
  if (!estado.estudiantes) {
    tbody.replaceChildren();
    try {
      estado.estudiantes = await getEstudiantes();
    } catch (error) {
      return mostrarError(error);
    }
  }
  const alumnos = estado.estudiantes;
  const q = $('#buscarEst').value.trim().toLowerCase();
  const materia = $('#materiaEst').value;
  const estadoFiltro = $('#estadoEst').value;

  $('#colAvance').textContent = materia === '' ? 'Avance' : `Avance · ${MATERIAS[materia]}`;
  tbody.replaceChildren();

  const visibles = alumnos.filter((a) => a.nombre.toLowerCase().includes(q) && (!estadoFiltro || a.estado === estadoFiltro));
  visibles.forEach((alumno) => {
    const valor = materia === '' ? alumno.avance : alumno.materias[materia];
    const tr = el('tr');

    const tdNombre = el('td', 'cell-title', alumno.nombre);

    const tdAvance = el('td');
    const barra = el('div', 'd-flex align-items-center gap-2');
    const progreso = el('div', 'progress mini-progress flex-grow-1');
    const relleno = el('div', 'progress-bar');
    relleno.style.width = `${valor}%`;
    progreso.appendChild(relleno);
    barra.append(progreso, el('span', 'small fw-bold', `${valor}%`));
    tdAvance.appendChild(barra);

    const tdRacha = el('td', 'text-nowrap', alumno.racha);

    const tdEstado = el('td');
    tdEstado.appendChild(statusBadge(alumno.estado));

    const tdBoton = el('td', 'text-end');
    const boton = botonVer('Ver');
    boton.addEventListener('click', () => abrirFicha(alumno));
    tdBoton.appendChild(boton);

    tr.append(tdNombre, tdAvance, tdRacha, tdEstado, tdBoton);
    tbody.appendChild(tr);
  });

  if (!visibles.length) {
    const tr = el('tr');
    const td = el(
      'td',
      'text-center text-secondary py-4',
      alumnos.length ? 'No hay estudiantes con esos filtros.' : 'Todavía no hay estudiantes en este grupo. Comparte el código desde Gestión.',
    );
    td.colSpan = 5;
    tr.appendChild(td);
    tbody.appendChild(tr);
  }
  $('#contadorEstudiantes').textContent = `${visibles.length} de ${alumnos.length} estudiantes`;
}

async function abrirFicha(alumno) {
  let ficha;
  try {
    ficha = await getFicha(alumno.id);
  } catch (error) {
    return mostrarError(error);
  }
  fichaActual = ficha;
  $('#fichaIniciales').textContent = ficha.iniciales;
  $('#fichaNombre').textContent = ficha.nombre;
  $('#fichaAvance').textContent = `${ficha.avance}%`;
  $('#fichaRacha').textContent = ficha.racha;
  $('#fichaEstado').replaceChildren(statusBadge(ficha.estado));
  $('#fichaNota').value = ficha.nota;

  const materias = $('#fichaMaterias');
  materias.replaceChildren();
  ficha.materias.forEach((valor, i) => {
    const fila = el('div', 'subject-row');
    const cabecera = el('div', 'd-flex justify-content-between small fw-bold mb-1');
    const nombreMateria = el('span');
    nombreMateria.append(icono(`${ICONO_MATERIA[i]} me-2`), MATERIAS[i]);
    cabecera.append(nombreMateria, el('span', '', `${valor}%`));
    const progreso = el('div', 'progress');
    const relleno = el('div', `progress-bar ${BAR_CLASS[i]}`);
    relleno.style.width = `${valor}%`;
    progreso.appendChild(relleno);
    fila.append(cabecera, progreso);
    materias.appendChild(fila);
  });

  const lista = (id, items, vacio, iconoDeLista) => {
    const ul = $(id);
    ul.replaceChildren();
    items.forEach(([nombre, valor]) => {
      const li = el('li', 'list-group-item d-flex justify-content-between align-items-center px-0');
      const clase = valor === 'Completada' ? 'status status-success' : valor === 'Sin empezar' ? 'status status-muted' : 'small fw-bold';
      const titulo = el('span');
      titulo.append(icono(`${iconoDeLista} text-secondary me-2`), nombre);
      li.append(titulo, el('span', clase, valor));
      ul.appendChild(li);
    });
    if (!items.length) ul.appendChild(el('li', 'list-group-item px-0 text-secondary small', vacio));
  };
  lista('#fichaActividades', ficha.actividades, 'No hay actividades activas para el grupo.', 'bi-controller');
  lista('#fichaEvaluacion', ficha.evaluacion, 'Todavía no ha respondido el banco de preguntas.', 'bi-patch-question');

  Modal.getOrCreateInstance('#modalFicha').show();
}

// La nota del docente se guarda sola mientras escribe (no hay botón Guardar)
async function guardarNota() {
  clearTimeout(temporizadorNota);
  if (!fichaActual) return;
  const nota = $('#fichaNota').value;
  if (nota.trim() === fichaActual.nota.trim()) return;
  try {
    const datos = await guardarNotaApi(fichaActual.id, nota);
    fichaActual.nota = datos.nota;
    showToast('Nota guardada.');
  } catch (error) {
    mostrarError(error);
  }
}

export function mountEstudiantesPage() {
  fichaActual = null;
  $('#filtrosEstudiantes').addEventListener('submit', (e) => e.preventDefault());
  $$('#filtrosEstudiantes input, #filtrosEstudiantes select').forEach((c) => c.addEventListener('input', pintarEstudiantes));
  $('#btnExportar').addEventListener('click', () => {
    showToast('Exportando la lista de estudiantes en Excel…');
    guardarArchivo(exportarEstudiantes);
  });
  $('#btnInformeEstudiante').addEventListener('click', () => {
    if (!fichaActual) return;
    showToast('Descargando el informe del estudiante en PDF…');
    guardarArchivo(() => informeDeEstudiante(fichaActual.id));
  });
  $('#fichaNota').addEventListener('input', () => {
    clearTimeout(temporizadorNota);
    temporizadorNota = setTimeout(guardarNota, 1000);
  });
  $('#fichaNota').addEventListener('blur', guardarNota);
  $('#modalFicha').addEventListener('hide.bs.modal', guardarNota);
  return pintarEstudiantes();
}

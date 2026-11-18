import { Modal } from 'bootstrap';

import { descargarReporte, getReporte } from '../api/reportes.api.js';
import { BAR_CLASS, CLAVES_MATERIA, MATERIAS } from '../utils/constantes.js';
import { guardarArchivo } from '../utils/descargas.js';
import { $, $$, el, iniciales } from '../utils/dom.js';
import { mostrarError, showToast } from '../utils/toast.js';

export function ReportesPage() {
  return `<div class="section-bar">
        <a href="#/panel" class="btn-back"><i class="bi bi-arrow-left"></i> Volver</a>
        <h2 class="section-title">Reportes</h2>
        <div class="section-actions">
          <button type="button" class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#modalGenerar"><i class="bi bi-file-earmark-arrow-down me-1"></i> Generar</button>
        </div>
      </div>

<main class="app-content">
        <div class="row g-3 mb-4 align-items-stretch">
          <div class="col-md-6 col-xl-4">
            <div class="card p-3 h-100">
              <label class="form-label" for="periodo">Periodo</label>
              <select class="form-select" id="periodo">
                <option value="">Cargando…</option>
              </select>
              <p class="small text-secondary mb-0 mt-2"><i class="bi bi-info-circle me-1"></i>Se ven las estadísticas de un solo periodo.</p>
            </div>
          </div>
          <div class="col-6 col-md-3 col-xl-4">
            <div class="card stat-card">
              <div class="stat-top">Promedio del periodo <i class="bi bi-graph-up icon-teal"></i></div>
              <div class="stat-value" id="repPromedio">—</div>
            </div>
          </div>
          <div class="col-6 col-md-3 col-xl-4">
            <div class="card stat-card">
              <div class="stat-top">Materia más baja <i class="bi bi-exclamation-triangle icon-rose"></i></div>
              <div class="stat-value" id="repMinimo">—</div>
              <div class="small text-secondary fw-bold" id="repMinimoNombre">Inglés</div>
            </div>
          </div>
        </div>

        <div class="row g-4">
          <div class="col-lg-7">
            <div class="card h-100">
              <div class="card-header"><h3 class="card-title">Avance por materia · <span data-periodo-nombre>Periodo 1</span></h3></div>
              <div class="card-body">
                <div class="bar-chart" id="graficoMaterias"><!-- Lo completa app.js --></div>
              </div>
            </div>
          </div>
          <div class="col-lg-5">
            <div class="card table-card h-100">
              <div class="card-header"><h3 class="card-title">Avance en <span data-periodo-nombre>Periodo 1</span></h3></div>
              <div class="table-responsive">
                <table class="table">
                  <thead><tr><th>Estudiante</th><th class="text-end">Avance</th></tr></thead>
                  <tbody id="tablaReporte">
</tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <p class="small text-secondary mt-4 mb-0"><i class="bi bi-download me-1"></i>Las descargas en PDF y Excel están dentro del botón <strong>Generar</strong>.</p>
      </main>

<div class="modal fade" id="modalGenerar" tabindex="-1" aria-labelledby="generarTitulo" aria-hidden="true">
    <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
      <div class="modal-content">
        <div class="modal-header">
          <div>
            <h2 class="modal-title fs-5" id="generarTitulo">Generar reporte</h2>
            <p class="small text-secondary mb-0">Filtros del reporte de <span data-group="nombre">Grado 3° — grupo A</span></p>
          </div>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
        </div>
        <div class="modal-body">
          <div class="row g-3 mb-4">
            <div class="col-sm-6 col-lg-3">
              <label class="form-label" for="genDesde">Desde</label>
              <input type="date" class="form-control" id="genDesde" value="2026-06-01">
            </div>
            <div class="col-sm-6 col-lg-3">
              <label class="form-label" for="genHasta">Hasta</label>
              <input type="date" class="form-control" id="genHasta" value="2026-08-29">
            </div>
            <div class="col-sm-6 col-lg-3">
              <label class="form-label" for="genPeriodo">Periodo</label>
              <select class="form-select" id="genPeriodo">
                <option value="">Cargando…</option>
              </select>
            </div>
            <div class="col-sm-6 col-lg-3">
              <label class="form-label" for="genEstado">Estado del estudiante</label>
              <select class="form-select" id="genEstado">
                <option>Todos los estados</option>
                <option>Al día</option>
                <option>Sin sincronizar</option>
                <option>Inactivo</option>
              </select>
            </div>
          </div>
          <p class="small text-secondary mt-n2"><i class="bi bi-info-circle me-1"></i>El periodo es el mismo que elegiste en el filtro de Reportes.</p>

          <div class="row g-4">
            <div class="col-md-6">
              <h3 class="h6 fw-bold mb-2">Materias incluidas</h3>
              <div class="form-check"><input class="form-check-input" type="checkbox" id="mMat" checked><label class="form-check-label" for="mMat">Matemáticas</label></div>
              <div class="form-check"><input class="form-check-input" type="checkbox" id="mCie" checked><label class="form-check-label" for="mCie">Ciencias</label></div>
              <div class="form-check"><input class="form-check-input" type="checkbox" id="mEsp" checked><label class="form-check-label" for="mEsp">Español</label></div>
              <div class="form-check"><input class="form-check-input" type="checkbox" id="mSoc" checked><label class="form-check-label" for="mSoc">Sociales</label></div>
              <div class="form-check"><input class="form-check-input" type="checkbox" id="mIng" checked><label class="form-check-label" for="mIng">Inglés</label></div>
            </div>
            <div class="col-md-6">
              <h3 class="h6 fw-bold mb-2">Incluir en el archivo</h3>
              <div class="form-check"><input class="form-check-input" type="checkbox" id="iAvance" checked><label class="form-check-label" for="iAvance">Avance por materia</label></div>
              <div class="form-check"><input class="form-check-input" type="checkbox" id="iDetalle" checked><label class="form-check-label" for="iDetalle">Detalle de actividades</label></div>
              <div class="form-check"><input class="form-check-input" type="checkbox" id="iEval" checked><label class="form-check-label" for="iEval">Resultados de evaluación</label></div>
              <div class="form-check"><input class="form-check-input" type="checkbox" id="iNotas"><label class="form-check-label" for="iNotas">Notas del docente</label></div>
              <div class="form-check"><input class="form-check-input" type="checkbox" id="iRacha"><label class="form-check-label" for="iRacha">Racha y conexiones</label></div>
            </div>
          </div>

          <div class="notice mt-4 mb-0">
            <i class="bi bi-file-earmark-text"></i>
            <div>Se generará el reporte de <strong data-group="nombre">Grado 3° — grupo A</strong> con <strong><span data-group="estudiantes">24</span> estudiantes</strong> en el periodo seleccionado. Elige el formato de descarga:</div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-light me-auto" data-bs-dismiss="modal">Cerrar</button>
          <button type="button" class="btn btn-outline-primary" data-bs-dismiss="modal" id="btnReporteExcel"><i class="bi bi-file-earmark-excel me-1"></i> Descargar Excel</button>
          <button type="button" class="btn btn-primary" data-bs-dismiss="modal" id="btnReportePdf"><i class="bi bi-file-earmark-pdf me-1"></i> Descargar PDF</button>
        </div>
      </div>
    </div>
  </div>`;
}

let periodoActual = null;
let periodosListos = false;

// Los periodos vienen de la API (así cubren todo el año y no quedan opciones sin datos)
function llenarPeriodos(periodos) {
  ['#periodo', '#genPeriodo'].forEach((selector) => {
    $(selector).replaceChildren(
      ...periodos.map((p) => {
        const opcion = el('option', '', p.nombre);
        opcion.value = p.clave;
        return opcion;
      }),
    );
  });
  periodosListos = true;
}

async function pintarReporte() {
  // Al abrir la página no hay periodo elegido: la API responde con el de hoy
  const elegido = periodosListos ? $('#periodo').value : '';
  let datos;
  try {
    datos = await getReporte(elegido);
  } catch (error) {
    return mostrarError(error);
  }
  periodoActual = datos.periodo;
  if (!periodosListos) llenarPeriodos(datos.periodos);
  $('#periodo').value = datos.periodo.clave;

  $('#repPromedio').textContent = `${datos.promedio}%`;
  $('#repMinimo').textContent = `${datos.minimo}%`;
  $('#repMinimoNombre').textContent = datos.minimo_nombre;
  $$('[data-periodo-nombre]').forEach((n) => {
    n.textContent = datos.periodo.nombre;
  });

  const grafico = $('#graficoMaterias');
  grafico.replaceChildren();
  datos.materias.forEach((valor, i) => {
    const columna = el('div', 'bar-col');
    const barra = el('div', `bar ${BAR_CLASS[i]}`);
    barra.style.height = `${valor * 1.6}px`;
    columna.append(el('span', 'bar-value', `${valor}%`), barra, el('span', 'bar-label', MATERIAS[i]));
    grafico.appendChild(columna);
  });

  const tbody = $('#tablaReporte');
  tbody.replaceChildren();
  datos.estudiantes.forEach(([nombre, valor]) => {
    const tr = el('tr');
    const td1 = el('td');
    const envoltura = el('div', 'd-flex align-items-center gap-2');
    envoltura.append(el('span', 'avatar', iniciales(nombre)), el('span', 'cell-title', nombre));
    td1.appendChild(envoltura);
    tr.append(td1, el('td', 'text-end fw-bold', `${valor}%`));
    tbody.appendChild(tr);
  });
}

export function mountReportesPage({ query }) {
  periodoActual = null;
  periodosListos = false;
  const modal = $('#modalGenerar');
  // El aviso "Descargando…" solo se muestra si el reporte se puede generar
  const avisos = { xlsx: 'Descargando el reporte en Excel…', pdf: 'Descargando el reporte en PDF…' };

  const fechasDelPeriodo = async () => {
    if (!periodoActual || periodoActual.clave !== $('#genPeriodo').value) {
      try {
        periodoActual = (await getReporte($('#genPeriodo').value)).periodo;
      } catch {
        return;
      }
    }
    $('#genDesde').value = periodoActual.desde;
    $('#genHasta').value = periodoActual.hasta;
  };

  $('#periodo').addEventListener('change', pintarReporte);
  modal.addEventListener('show.bs.modal', () => {
    $('#genPeriodo').value = $('#periodo').value;
    fechasDelPeriodo();
  });
  $('#genPeriodo').addEventListener('change', fechasDelPeriodo);

  const generar = (formato) => {
    const materias = ['#mMat', '#mCie', '#mEsp', '#mSoc', '#mIng'].map((id, i) => ($(id).checked ? CLAVES_MATERIA[i] : null)).filter(Boolean);
    const incluir = [
      ['#iAvance', 'avance'],
      ['#iDetalle', 'detalle'],
      ['#iEval', 'evaluacion'],
      ['#iNotas', 'notas'],
      ['#iRacha', 'racha'],
    ]
      .filter(([id]) => $(id).checked)
      .map(([, clave]) => clave);
    if (!materias.length) return showToast('Elige al menos una materia.');
    if (!incluir.length) return showToast('Elige al menos un contenido para incluir en el archivo.');
    const consulta = new URLSearchParams({
      formato,
      periodo: $('#genPeriodo').value,
      desde: $('#genDesde').value,
      hasta: $('#genHasta').value,
      estado: $('#genEstado').selectedIndex > 0 ? $('#genEstado').value : '',
      materias: materias.join(','),
      incluir: incluir.join(','),
    });
    showToast(avisos[formato]);
    guardarArchivo(() => descargarReporte(consulta));
  };
  $('#btnReporteExcel').addEventListener('click', () => generar('xlsx'));
  $('#btnReportePdf').addEventListener('click', () => generar('pdf'));

  const listo = pintarReporte();
  if (query.get('generar') === '1') listo.then(() => Modal.getOrCreateInstance(modal).show());
  return listo;
}

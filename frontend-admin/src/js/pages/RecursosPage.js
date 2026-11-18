import { getRecursos, subirRecursos } from '../api/recursos.api.js';
import { miniatura } from '../components/recursos/Miniatura.js';
import { paginar } from '../components/tablas/filtros.js';
import { $, $$, el, icono } from '../utils/dom.js';
import { plural } from '../utils/formatters.js';
import { mostrarError, showToast } from '../utils/toast.js';

export function RecursosPage() {
  return `<header class="topbar">
        <button class="btn btn-light d-lg-none" type="button" data-bs-toggle="offcanvas" data-bs-target="#sidebar" aria-controls="sidebar" aria-label="Abrir menú"><i class="bi bi-list"></i></button>
        <a href="#/inicio" class="btn-back"><i class="bi bi-arrow-left"></i> Volver</a>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="#/inicio">Inicio</a></li>
            <li class="breadcrumb-item active" aria-current="page">Recursos</li>
          </ol>
        </nav>
        <div class="topbar-actions">
          <button type="button" class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#modalSubir"><i class="bi bi-folder-plus me-1"></i> Subir carpeta</button>
        </div>
      </header>

<main class="app-content">
        <div class="page-header">
          <div>
            <h1 class="page-title">Recursos</h1>
            <p class="page-subtitle">Imágenes y audios disponibles para las actividades.</p>
          </div>
        </div>

        <ul class="nav section-tabs" role="tablist">
          <li class="nav-item" role="presentation"><button class="nav-link active" data-bs-toggle="tab" data-bs-target="#tabImagenes" type="button" role="tab">Imágenes</button></li>
          <li class="nav-item" role="presentation"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#tabAudio" type="button" role="tab">Audio</button></li>
        </ul>

        <form class="filters">
          <div class="row g-3 align-items-end">
            <div class="col-md-4">
              <label class="form-label" for="buscarRec">Buscar</label>
              <div class="input-group">
                <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
                <input type="search" class="form-control" id="buscarRec" placeholder="Nombre del archivo">
              </div>
            </div>
            <div class="col-md-4">
              <label class="form-label" for="carpeta">Carpeta</label>
              <select class="form-select" id="carpeta">
                <option>Todas las carpetas</option>
                <option>actividades/ciencias</option>
                <option>actividades/matematicas</option>
                <option>actividades/espanol</option>
              </select>
            </div>
            <div class="col-md-4">
              <label class="form-label" for="compat">Compatibilidad</label>
              <select class="form-select" id="compat">
                <option>Todas</option>
                <option>Todas las versiones</option>
                <option>Desde v1.4.0</option>
              </select>
            </div>
          </div>
        </form>

        <div class="notice">
          <i class="bi bi-lightbulb"></i>
          <div>Estos recursos se usan en el constructor de actividades con el botón <strong>Más recursos</strong>.</div>
        </div>

        <div class="tab-content">
          <!-- Imágenes -->
          <div class="tab-pane fade show active" id="tabImagenes" role="tabpanel">
            <div class="card table-card">
              <div class="card-header small text-secondary"><i class="bi bi-folder2-open me-1"></i> assets/images/actividades/ciencias</div>
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead><tr><th>Vista</th><th>Recurso</th><th>Tipo</th><th>Compatibilidad</th></tr></thead>
                  <tbody>
                  </tbody>
                </table>
              </div>
              <div class="table-footer">
                <span>0 de 0 recursos</span>
                <ul class="pagination pagination-sm"></ul>
              </div>
            </div>
          </div>

          <!-- Audio -->
          <div class="tab-pane fade" id="tabAudio" role="tabpanel">
            <div class="card table-card">
              <div class="card-header small text-secondary"><i class="bi bi-folder2-open me-1"></i> assets/audio/actividades/ciencias</div>
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead><tr><th>Vista</th><th>Recurso</th><th>Tipo</th><th>Compatibilidad</th></tr></thead>
                  <tbody>
                  </tbody>
                </table>
              </div>
              <div class="table-footer">
                <span>0 de 0 recursos</span>
              </div>
            </div>
          </div>
        </div>
      </main>

<div class="modal fade" id="modalSubir" tabindex="-1" aria-labelledby="modalSubirTitulo" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title fs-5" id="modalSubirTitulo">Subir carpeta</h2>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
        </div>
        <div class="modal-body">
          <div class="dropzone">
            <i class="bi bi-cloud-arrow-up d-block mb-2"></i>
            <p class="fw-semibold mb-1 text-dark">Arrastra aquí una carpeta con imágenes o audios</p>
            <p class="small mb-3">PNG, JPG o MP3</p>
            <label class="btn btn-soft btn-sm">Seleccionar carpeta <input type="file" class="d-none" multiple></label>
          </div>
          <p class="small text-secondary mt-3 mb-0">Demostración: en el prototipo los archivos no se cargan ni se procesan.</p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-light" data-bs-dismiss="modal">Cancelar</button>
          <button type="button" class="btn btn-primary" data-bs-dismiss="modal">Subir</button>
        </div>
      </div>
    </div>
  </div>`;
}

function llenarSelect(select, opciones, conservarPrimera = false) {
  const primera = conservarPrimera ? [select.options[0]] : [];
  select.replaceChildren(...primera, ...opciones.map((texto) => el('option', '', texto)));
}

// Pestaña "Videos": copia de la de Audio (mismo estilo), porque el HTML solo trae Imágenes y Audio
function crearPestanaVideos() {
  const botonAudio = $('[data-bs-target="#tabAudio"]');
  const itemVideos = botonAudio.parentElement.cloneNode(true);
  const botonVideos = $('button', itemVideos);
  botonVideos.dataset.bsTarget = '#tabVideos';
  botonVideos.textContent = 'Videos';
  botonVideos.classList.remove('active');
  botonAudio.parentElement.after(itemVideos);

  const panelVideos = $('#tabAudio').cloneNode(true);
  panelVideos.id = 'tabVideos';
  panelVideos.classList.remove('show', 'active');
  $('tbody', panelVideos).replaceChildren();
  $('#tabAudio').after(panelVideos);
}

// Agrega paginación a las tablas que en el HTML no la traen (Audio y Videos)
function asegurarPaginacion(panel) {
  const pie = $('.table-footer', panel);
  if (!$('.pagination', pie)) pie.appendChild(el('ul', 'pagination pagination-sm'));
}

async function cargarRecursos() {
  let datos;
  try {
    datos = await getRecursos();
  } catch (error) {
    return mostrarError(error);
  }
  const paneles = [
    { tipo: 'Imagen', carpetaBase: 'images', panel: $('#tabImagenes'), estado: { pagina: 1 } },
    { tipo: 'Audio', carpetaBase: 'audio', panel: $('#tabAudio'), estado: { pagina: 1 } },
    { tipo: 'Video', carpetaBase: 'videos', panel: $('#tabVideos'), estado: { pagina: 1 } },
  ];

  // Filtro de carpetas con las carpetas que existen de verdad
  const selectCarpeta = $('#carpeta');
  const elegida = selectCarpeta.selectedIndex > 0 ? selectCarpeta.value : '';
  const carpetas = [...new Set(datos.recursos.map((r) => r.carpeta))].sort();
  llenarSelect(selectCarpeta, carpetas, true);
  if (carpetas.includes(elegida)) selectCarpeta.value = elegida;

  paneles.forEach((p) => {
    asegurarPaginacion(p.panel);
    const tbody = $('tbody', p.panel);
    tbody.replaceChildren();
    datos.recursos
      .filter((r) => r.tipo === p.tipo)
      .forEach((r) => {
        const tr = el('tr');
        Object.assign(tr.dataset, { carpeta: r.carpeta, compat: r.compatibilidad });
        const tdVista = el('td');
        tdVista.appendChild(miniatura(r, 'thumb-sm'));
        const tdCompat = el('td');
        tdCompat.appendChild(el('span', `status ${r.version_minima ? 'status-warning' : 'status-success'}`, r.compatibilidad));
        tr.append(tdVista, el('td', 'cell-title', r.nombre), el('td', '', r.tipo), tdCompat);
        tbody.appendChild(tr);
      });
  });

  const filtrar = (reiniciar = true) => {
    const q = $('#buscarRec').value.trim().toLowerCase();
    const carpeta = $('#carpeta').selectedIndex > 0 ? $('#carpeta').value : '';
    const compat = $('#compat').selectedIndex > 0 ? $('#compat').value : '';
    paneles.forEach((p) => {
      if (reiniciar) p.estado.pagina = 1;
      const filas = $$('tbody tr', p.panel);
      const coinciden = filas.filter(
        (r) => r.textContent.toLowerCase().includes(q) && (!carpeta || r.dataset.carpeta === carpeta) && (!compat || r.dataset.compat === compat),
      );
      const visibles = paginar(filas, coinciden, $('.pagination', p.panel), p.estado, () => filtrar(false));
      $('.table-footer > span', p.panel).textContent = `${visibles} de ${datos.recursos.length} recursos`;
      $('.card-header', p.panel).replaceChildren(icono('bi-folder2-open me-1'), ` assets/${p.carpetaBase}/${carpeta || 'actividades'}`);
    });
  };
  const form = $('form.filters');
  form.oninput = () => filtrar();
  form.onsubmit = (e) => e.preventDefault();
  filtrar();
}

export function mountRecursosPage() {
  const modal = $('#modalSubir');
  const botonSubir = $('.modal-footer .btn-primary', modal);
  crearPestanaVideos();
  cargarRecursos();

  // Subir archivos: botón "Seleccionar carpeta" o arrastrar a la zona
  const input = $('input[type="file"]', modal);
  const zona = $('.dropzone', modal);
  const ayuda = $('p.small', zona);
  let elegidos = [];
  const elegir = (archivos) => {
    elegidos = Array.from(archivos);
    ayuda.textContent = elegidos.length ? `${plural(elegidos.length, 'archivo listo', 'archivos listos')} para subir` : 'PNG, JPG, MP3 o MP4';
  };
  input.accept = '.png,.jpg,.jpeg,.mp3,.mp4';
  input.addEventListener('change', () => elegir(input.files));
  zona.addEventListener('dragover', (e) => e.preventDefault());
  zona.addEventListener('drop', (e) => {
    e.preventDefault();
    elegir(e.dataTransfer.files);
  });
  modal.addEventListener('hidden.bs.modal', () => {
    input.value = '';
    elegir([]);
  });

  botonSubir.addEventListener('click', async () => {
    if (!elegidos.length) {
      showToast('Selecciona al menos un archivo PNG, JPG, MP3 o MP4.');
      return;
    }
    const formulario = new FormData();
    elegidos.forEach((archivo) => formulario.append('archivos', archivo));
    const carpeta = $('#carpeta');
    formulario.append('carpeta', carpeta.selectedIndex > 0 ? carpeta.value : '');
    showToast('Carpeta enviada. Los recursos aparecerán cuando termine la carga.');
    const partes = [];
    try {
      const datos = await subirRecursos(formulario);
      if (datos.subidos.length) partes.push(`Se ${datos.subidos.length === 1 ? 'subió' : 'subieron'} ${plural(datos.subidos.length, 'recurso', 'recursos')}.`);
      if (datos.omitidos.length) partes.push(`Omitidos: ${datos.omitidos.join('; ')}.`);
    } catch (error) {
      // Si no se subió nada, la API explica por qué se omitió cada archivo
      if (!error.details?.omitidos) return mostrarError(error);
      partes.push(`Omitidos: ${error.details.omitidos.join('; ')}.`);
    }
    showToast(partes.join(' '));
    cargarRecursos();
  });
}

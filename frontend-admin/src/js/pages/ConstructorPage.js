import { Modal } from 'bootstrap';

import { crearActividad, editarActividad, getActividad } from '../api/actividades.api.js';
import { getRecursos } from '../api/recursos.api.js';
import { crearEditorContenido } from '../components/actividades/EditorContenido.js';
import { miniatura } from '../components/recursos/Miniatura.js';
import { crearSelectorRecursos, etiquetaCarpeta } from '../components/recursos/SelectorRecursos.js';
import { CARPETA_MATERIA } from '../utils/constantes.js';
import { $, $$, el, icono } from '../utils/dom.js';
import { plural } from '../utils/formatters.js';
import { mostrarError, showToast } from '../utils/toast.js';

export function ConstructorPage() {
  return `<header class="topbar">
        <button class="btn btn-light d-lg-none" type="button" data-bs-toggle="offcanvas" data-bs-target="#sidebar" aria-controls="sidebar" aria-label="Abrir menú"><i class="bi bi-list"></i></button>
        <a href="#/actividades" class="btn-back"><i class="bi bi-arrow-left"></i> Volver</a>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb" id="builderCrumb">
            <li class="breadcrumb-item"><a href="#/actividades">Actividades</a></li>
            <li class="breadcrumb-item active" aria-current="page">Nueva</li>
          </ol>
        </nav>
        <div class="topbar-actions">
          <a href="#/borradores?msg=borrador" class="btn btn-outline-secondary btn-sm" id="btnBorrador"><i class="bi bi-save me-1"></i> Guardar borrador</a>
          <button type="button" class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#modalResumen"><i class="bi bi-send me-1"></i> Publicar</button>
        </div>
      </header>

<main class="app-content">
        <div class="page-header">
          <div>
            <h1 class="page-title" id="builderTitle">Constructor de actividades</h1>
            <p class="page-subtitle">Todo se edita en esta misma vista: cada cambio se aplica al instante.</p>
          </div>
        </div>

        <div class="notice">
          <i class="bi bi-phone"></i>
          <div>Los cambios llegan al celular del niño en su próxima sincronización, no de inmediato.</div>
        </div>

        <div class="row g-4">
          <!-- Datos -->
          <div class="col-xl-5">
            <div class="card h-100">
              <div class="card-header"><h2 class="card-title"><i class="bi bi-card-text me-2 text-primary"></i>Datos</h2></div>
              <div class="card-body p-4">
                <div class="mb-3">
                  <label class="form-label" for="actNombre">Nombre de la actividad</label>
                  <input type="text" class="form-control" id="actNombre" value="¿Vivo o no vivo?">
                </div>
                <div class="mb-3">
                  <label class="form-label" for="actMateria">Materia</label>
                  <select class="form-select" id="actMateria">
                    <option>Matemáticas</option>
                    <option>Español</option>
                    <option selected>Ciencias naturales</option>
                    <option>Sociales</option>
                    <option>Inglés</option>
                  </select>
                </div>
                <div class="row g-3">
                  <div class="col-sm-6">
                    <label class="form-label" for="actGrado">Grado</label>
                    <select class="form-select" id="actGrado">
                      <option>Grado 1°</option>
                      <option selected>Grado 2°</option>
                      <option>Grado 3°</option>
                      <option>Grado 4°</option>
                      <option>Grado 5°</option>
                    </select>
                  </div>
                  <div class="col-sm-6">
                    <label class="form-label" for="actTipo">Tipo</label>
                    <select class="form-select" id="actTipo">
                      <option selected>Arrastrar</option>
                      <option>Arrastrar y soltar</option>
                      <option>Ordenar sílabas</option>
                      <option>Selección múltiple</option>
                      <option>Comprensión auditiva</option>
                      <option>Memory match</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Recursos -->
          <div class="col-xl-7">
            <div class="card h-100">
              <div class="card-header d-flex justify-content-between align-items-center flex-wrap gap-2">
                <div>
                  <h2 class="card-title"><i class="bi bi-images me-2 text-primary"></i>Recursos</h2>
                  <span class="small text-secondary" id="recursosAyuda">Lo que elegiste y algunas imágenes de la materia</span>
                </div>
                <span class="badge rounded-pill text-bg-light border" id="selCount">0 seleccionados</span>
              </div>
              <div class="card-body p-4">
                <div class="resource-grid" id="resourceGrid">
                  <button type="button" class="resource-tile add-tile">
                    <i class="bi bi-plus-circle"></i> Ver todos
                  </button>
                </div>

                <div class="alert alert-warning d-flex gap-2 mt-4 mb-0 small d-none" role="alert">
                  <i class="bi bi-exclamation-triangle"></i>
                  <div></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

<div class="modal fade" id="modalResumen" tabindex="-1" aria-labelledby="modalResumenTitulo" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <div>
            <h2 class="modal-title fs-5" id="modalResumenTitulo">Resumen antes de publicar</h2>
            <p class="small text-secondary mb-0">Revisa lo que seleccionaste. Al continuar, la actividad se publica.</p>
          </div>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
        </div>
        <div class="modal-body">
          <dl class="row detail-list">
            <dt class="col-5">Actividad</dt><dd class="col-7" id="resNombre">—</dd>
            <dt class="col-5">Materia</dt><dd class="col-7" id="resMateria">—</dd>
            <dt class="col-5">Grado</dt><dd class="col-7" id="resGrado">—</dd>
            <dt class="col-5">Tipo</dt><dd class="col-7" id="resTipo">—</dd>
            <dt class="col-5">Recursos seleccionados</dt>
            <dd class="col-7"><span id="resCount">0 recursos</span><ul class="list-unstyled small text-secondary mb-0 mt-1" id="resLista"></ul></dd>
            <dt class="col-5">Estado al continuar</dt><dd class="col-7"><span class="status status-success" id="resEstado">Publicada</span></dd>
          </dl>
          <div class="border rounded-3 p-3 small bg-light">
            <div class="fw-bold mb-2"><i class="bi bi-phone me-1"></i> Llega al celular del niño en su próxima sincronización.</div>
            <div class="d-flex justify-content-between gap-2"><span>Equipos desactualizados</span><span class="fw-semibold text-end">—</span></div>
            <div class="d-flex justify-content-between gap-2 mt-1"><span>Recursos nuevos</span><span class="fw-semibold text-end">—</span></div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-light" data-bs-dismiss="modal">Volver a editar</button>
          <a href="#/actividades?msg=publicada" class="btn btn-primary" id="btnContinuar">Continuar</a>
        </div>
      </div>
    </div>
  </div>`;
}

export async function mountConstructorPage({ navigate, query }) {
  const id = query.get('id');
  const grid = $('#resourceGrid');
  const botonMas = $('.add-tile', grid);
  const selected = new Map();
  $$('.resource-tile:not(.add-tile)', grid).forEach((n) => n.remove());

  let meta;
  let actividad = null;
  try {
    [meta, actividad] = await Promise.all([getRecursos(), id ? getActividad(id) : Promise.resolve(null)]);
  } catch (error) {
    return mostrarError(error);
  }
  const catalogo = meta.recursos;
  const buscarRecurso = (valor) => catalogo.find((r) => String(r.id) === String(valor));
  const esEdicion = Boolean(actividad) && actividad.estado !== 'Borrador';

  if (actividad) {
    $('#actNombre').value = actividad.nombre;
    $('#actMateria').value = actividad.materia;
    $('#actGrado').value = `Grado ${actividad.grado}`;
    $('#actTipo').value = actividad.tipo;
    actividad.recursos.forEach((r) => selected.set(String(r.id), buscarRecurso(r.id)));
  }
  if (esEdicion) {
    $('#builderTitle').textContent = 'Editar actividad';
    $('#builderCrumb').innerHTML =
      '<li class="breadcrumb-item"><a href="#/actividades">Actividades</a></li><li class="breadcrumb-item"></li><li class="breadcrumb-item active" aria-current="page">Editar</li>';
    const crumb = $('#builderCrumb .breadcrumb-item:nth-child(2)');
    const enlace = document.createElement('a');
    enlace.href = `#/actividad-detalle?id=${encodeURIComponent(actividad.id)}`;
    enlace.textContent = actividad.nombre;
    crumb.appendChild(enlace);
    $('#resEstado').textContent = 'Publicada (reemplaza la versión actual)';
  }

  const selector = crearSelectorRecursos(catalogo);
  const carpetaDeLaMateria = () => `actividades/${CARPETA_MATERIA[$('#actMateria').value]}`;

  // Cuadrícula: lo que ya eligió y, como sugerencia, imágenes de la materia. Todo lo demás está en el selector.
  const render = () => {
    $$('input[type="checkbox"]', grid).forEach((cb) => {
      cb.checked = selected.has(cb.value);
    });
    const n = selected.size;
    $('#selCount').textContent = `${n} seleccionado${n === 1 ? '' : 's'}`;
  };
  grid.addEventListener('change', (ev) => {
    const cb = ev.target;
    if (cb.type !== 'checkbox') return;
    if (cb.checked) selected.set(cb.value, buscarRecurso(cb.value));
    else selected.delete(cb.value);
    render();
  });

  const tarjeta = (recurso) => {
    const label = el('label', `resource-tile${recurso.compatible ? '' : ' is-disabled'}`);
    if (!recurso.compatible) label.title = `Disponible desde v${recurso.version_minima}`;
    const input = el('input');
    input.type = 'checkbox';
    input.value = recurso.id;
    input.dataset.tipo = recurso.tipo;
    input.disabled = !recurso.compatible;
    const check = el('span', 'check');
    check.appendChild(icono('bi-check-lg'));
    label.append(input, check, miniatura(recurso, 'thumb'), el('div', 'name', recurso.nombre.split('/').pop()));
    return label;
  };
  const cardRecursos = grid.closest('.card');
  const renderGrid = () => {
    const carpeta = carpetaDeLaMateria();
    $('#recursosAyuda').textContent = `Lo que elegiste y algunas imágenes de ${etiquetaCarpeta(carpeta)}`;
    $$('.resource-tile:not(.add-tile)', grid).forEach((n) => n.remove());
    const sugeridos = catalogo.filter((r) => r.carpeta === carpeta && r.tipo === 'Imagen' && !selected.has(String(r.id))).slice(0, 6);
    const mostrados = [...selected.values(), ...sugeridos];
    mostrados.forEach((r) => grid.insertBefore(tarjeta(r), botonMas));

    const alerta = $('.alert-warning', cardRecursos);
    const bloqueados = mostrados.filter((r) => !r.compatible);
    alerta.classList.toggle('d-none', !bloqueados.length);
    if (bloqueados.length) {
      const b = bloqueados[0];
      $('div', alerta).replaceChildren(
        el('strong', '', bloqueados.map((r) => r.nombre).join(', ')),
        document.createTextNode(
          ` está atenuada porque llegó en la v${b.version_minima}. Los ${b.equipos_incompatibles} equipos con versiones anteriores no podrían mostrar esta actividad.`,
        ),
      );
    }
    render();
  };
  $('#actMateria').addEventListener('change', renderGrid);
  const editor = crearEditorContenido(actividad, catalogo, selector);

  // Buscador visible: abre el selector con todo el catálogo (imágenes y audios de todas las materias)
  const abrirSelector = () => selector.elegirVarios({ seleccion: selected, materia: carpetaDeLaMateria(), alCambiar: renderGrid });
  const imagenes = catalogo.filter((r) => r.tipo === 'Imagen').length;
  const audios = catalogo.filter((r) => r.tipo === 'Audio').length;
  const buscar = el('button', 'picker-trigger');
  buscar.type = 'button';
  buscar.append(icono('bi-search'), el('span', '', `Buscar entre ${plural(imagenes, 'imagen', 'imágenes')} y ${plural(audios, 'audio', 'audios')}…`));
  buscar.addEventListener('click', abrirSelector);
  grid.before(buscar);
  botonMas.addEventListener('click', abrirSelector);

  // Resumen antes de publicar
  $('#modalResumen').addEventListener('show.bs.modal', () => {
    $('#resNombre').textContent = $('#actNombre').value || 'Sin nombre';
    $('#resMateria').textContent = $('#actMateria').value;
    $('#resGrado').textContent = $('#actGrado').value;
    $('#resTipo').textContent = $('#actTipo').value;
    $('#resCount').textContent = `${selected.size} recurso${selected.size === 1 ? '' : 's'}`;
    const lista = $('#resLista');
    lista.replaceChildren();
    selected.forEach((recurso) => lista.appendChild(el('li', '', `${recurso.nombre} · ${recurso.tipo}`)));

    // Fila "Contenido" en el resumen (solo para actividades con plantilla)
    let filaContenido = $('#resContenido');
    if (!filaContenido) {
      const estado = $('#resEstado').closest('dd').previousElementSibling;
      filaContenido = el('dd', 'col-7');
      filaContenido.id = 'resContenido';
      estado.before(el('dt', 'col-5', 'Contenido'), filaContenido);
    }
    filaContenido.textContent = editor.resumen() ?? 'No aplica (pantalla propia de la app)';

    const [equipos, nuevos] = $$('#modalResumen .bg-light > .d-flex');
    const [eqTitulo, eqValor] = $$('span', equipos);
    eqTitulo.textContent = meta.version_desactualizada ? `Equipos con v${meta.version_desactualizada}` : 'Equipos desactualizados';
    eqValor.textContent = meta.equipos_desactualizados
      ? `${meta.equipos_desactualizados} equipos no reciben actividades nuevas`
      : 'Todos los equipos reciben actividades nuevas';
    eqValor.className = `${meta.equipos_desactualizados ? 'text-warning-emphasis' : 'text-success'} fw-semibold text-end`;

    const [nvTitulo, nvValor] = $$('span', nuevos);
    const conVersion = [...selected.values()].filter((r) => r.version_minima);
    nvTitulo.textContent = 'Recursos nuevos';
    nvValor.textContent = conVersion.length
      ? `Usa ${conVersion.map((r) => r.nombre).join(', ')}: requiere v${conVersion[0].version_minima}`
      : 'No usa recursos nuevos: compatible con todas las versiones';
    nvValor.className = `${conVersion.length ? 'text-warning-emphasis' : 'text-success'} fw-semibold text-end`;
  });

  // Guardar: borrador o publicada
  const guardar = async (estado, boton) => {
    const nombre = $('#actNombre').value.trim();
    if (!nombre) {
      Modal.getInstance('#modalResumen')?.hide();
      showToast('Escribe el nombre de la actividad.');
      return;
    }
    boton.classList.add('disabled');
    const cuerpo = {
      nombre,
      materia: $('#actMateria').value,
      grado: $('#actGrado').value,
      tipo: $('#actTipo').value,
      estado,
      recursos: [...selected.keys()].map(Number),
      contenido: editor.contenido(),
    };
    try {
      if (actividad) await editarActividad(actividad.id, cuerpo);
      else await crearActividad(cuerpo);
    } catch (error) {
      Modal.getInstance('#modalResumen')?.hide();
      mostrarError(error);
      boton.classList.remove('disabled');
      return;
    }
    if (estado === 'Borrador') navigate('borradores?msg=borrador');
    else navigate(`actividades?msg=${esEdicion ? 'cambios' : 'publicada'}`);
  };
  $('#btnBorrador').addEventListener('click', (e) => {
    e.preventDefault();
    guardar('Borrador', e.currentTarget);
  });
  $('#btnContinuar').addEventListener('click', (e) => {
    e.preventDefault();
    guardar('Publicada', e.currentTarget);
  });

  renderGrid();
  return () => selector.destruir(); // la ventana del selector vive en <body>
}

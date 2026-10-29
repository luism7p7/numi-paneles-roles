/* =========================================================
   Numi · Panel administrativo
   Interacciones del panel (modales, filtros y mensajes) y
   conexión con el servidor Flask (API en /api/...)
   ========================================================= */

const STATUS_CLASS = {
  Publicada: 'status-success', Activa: 'status-success', Activo: 'status-success',
  Borrador: 'status-warning', Pendiente: 'status-warning',
  Desactivada: 'status-muted', Inactivo: 'status-muted', Inactiva: 'status-muted',
  Editada: 'status-info', Eliminada: 'status-danger',
  'Crítico': 'status-danger', Alerta: 'status-warning', Info: 'status-info',
  'Todas las versiones': 'status-success'
};

// Carpeta de recursos de cada materia (assets/images/actividades/<carpeta>)
const CARPETA_MATERIA = {
  'Matemáticas': 'matematicas', 'Español': 'espanol', 'Ciencias naturales': 'ciencias',
  'Sociales': 'sociales', 'Inglés': 'ingles'
};

const POR_PAGINA = 10;
const PAGINA = window.location.pathname.split('/').pop() || 'index.html';
const params = new URLSearchParams(window.location.search);
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));

/* ---------- Utilidades ---------- */
function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function icono(clases) {
  return el('i', `bi ${clases}`);
}

function plural(n, singular, varios) {
  return `${n} ${n === 1 ? singular : varios}`;
}

function fechaISO(fecha) {
  const dos = n => String(n).padStart(2, '0');
  return `${fecha.getFullYear()}-${dos(fecha.getMonth() + 1)}-${dos(fecha.getDate())}`;
}

/* ---------- Utilidades de mensajes ---------- */
function showToast(message) {
  let area = $('#toastArea');
  if (!area) {
    area = el('div', 'toast-container position-fixed bottom-0 end-0 p-3');
    area.id = 'toastArea';
    document.body.appendChild(area);
  }
  const toast = document.createElement('div');
  toast.className = 'toast align-items-center text-bg-dark border-0';
  toast.setAttribute('role', 'status');
  toast.innerHTML = '<div class="d-flex"><div class="toast-body"></div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Cerrar"></button></div>';
  $('.toast-body', toast).textContent = message;
  area.appendChild(toast);
  new bootstrap.Toast(toast, { delay: 4500 }).show();
  toast.addEventListener('hidden.bs.toast', () => toast.remove());
}

function showFlash(message, type = 'success') {
  const flash = $('#flash');
  if (!flash) {
    showToast(message);
    return;
  }
  const alert = document.createElement('div');
  alert.className = `alert alert-${type} alert-dismissible fade show d-flex align-items-center gap-2`;
  alert.setAttribute('role', 'alert');
  const iconoAlerta = type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-triangle-fill';
  alert.innerHTML = `<i class="bi ${iconoAlerta}"></i><span></span><button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>`;
  $('span', alert).textContent = message;
  flash.replaceChildren(alert);
}

function setStatus(node, estado) {
  node.className = `status ${STATUS_CLASS[estado] || 'status-muted'}`;
  node.textContent = estado;
}

function statusSpan(estado) {
  const span = el('span');
  setStatus(span, estado);
  return span;
}

function mostrarError(datos) {
  showToast(datos.error || 'Ocurrió un error inesperado.');
}

// Cambia el total en textos como "<span data-visible>4</span> de 7 instituciones"
function fijarTotal(contador, total, nombre) {
  if (contador) contador.parentElement.lastChild.textContent = ` de ${total} ${nombre}`;
}

function filaVacia(tbody, columnas, texto) {
  const tr = el('tr');
  tr.dataset.vacia = 'true';
  const td = el('td', 'text-center text-secondary py-4', texto);
  td.colSpan = columnas;
  tr.appendChild(td);
  tbody.appendChild(tr);
}

/* ---------- Comunicación con el servidor (Flask) ---------- */
// Devuelve { ok, status, datos }. Si la sesión terminó (401) vuelve al login.
async function api(url, { metodo = 'GET', cuerpo, formulario } = {}) {
  const opciones = { method: metodo, headers: {} };
  if (formulario) {
    opciones.body = formulario;
  } else if (cuerpo !== undefined) {
    opciones.headers['Content-Type'] = 'application/json';
    opciones.body = JSON.stringify(cuerpo);
  }
  try {
    const resp = await fetch(url, opciones);
    const datos = await resp.json().catch(() => ({}));
    if (resp.status === 401 && !['index.html', 'crear-usuario.html'].includes(PAGINA)) {
      window.location.href = 'index.html';
    }
    return { ok: resp.ok, status: resp.status, datos };
  } catch {
    return { ok: false, status: 0, datos: { error: 'No hay conexión con el servidor. Abre el panel desde Flask (python app.py).' } };
  }
}

/* ---------- Paginación ---------- */
function dibujarPaginacion(ul, actual, total, irA) {
  ul.replaceChildren();
  const item = (texto, pagina, { activo = false, deshabilitado = false } = {}) => {
    const li = el('li', `page-item${activo ? ' active' : ''}${deshabilitado ? ' disabled' : ''}`);
    const a = el('a', 'page-link', texto);
    a.href = '#';
    a.addEventListener('click', e => {
      e.preventDefault();
      if (!activo && !deshabilitado) irA(pagina);
    });
    li.appendChild(a);
    return li;
  };
  ul.appendChild(item('Anterior', actual - 1, { deshabilitado: actual === 1 }));
  for (let p = 1; p <= total; p++) ul.appendChild(item(String(p), p, { activo: p === actual }));
  ul.appendChild(item('Siguiente', actual + 1, { deshabilitado: actual === total }));
}

// Muestra solo la página actual de las filas que cumplen los filtros. Devuelve cuántas quedan visibles.
function paginar(todas, coinciden, ul, estado, redibujar) {
  let visibles = coinciden;
  if (ul) {
    const paginas = Math.max(1, Math.ceil(coinciden.length / POR_PAGINA));
    estado.pagina = Math.min(Math.max(1, estado.pagina), paginas);
    const inicio = (estado.pagina - 1) * POR_PAGINA;
    visibles = coinciden.slice(inicio, inicio + POR_PAGINA);
    dibujarPaginacion(ul, estado.pagina, paginas, p => { estado.pagina = p; redibujar(); });
  }
  todas.forEach(fila => fila.classList.toggle('d-none', !visibles.includes(fila)));
  return visibles.length;
}

/* ---------- Filtros de tablas ---------- */
$$('[data-table-filter]').forEach(form => {
  const table = $(form.dataset.tableFilter);
  if (!table) return;
  const card = table.closest('.card');
  const counter = $('[data-visible]', card);
  const paginacion = $('.pagination', card);
  const estado = { pagina: 1 };

  const cumple = (row, ctrl) => {
    const value = ctrl.value.trim().toLowerCase();
    if (!value) return true;
    const filtro = ctrl.dataset.filter;
    if (filtro === 'text') return row.textContent.toLowerCase().includes(value);
    if (filtro === 'desde') return (row.dataset.dia || '') >= value;
    if (filtro === 'hasta') return (row.dataset.dia || '') <= value;
    return (row.dataset[filtro] || '').toLowerCase() === value;
  };

  const apply = (reiniciar = true) => {
    if (reiniciar) estado.pagina = 1;
    const filas = $$('tbody tr', table).filter(row => !row.dataset.vacia);
    const controles = $$('[data-filter]', form);
    const coinciden = filas.filter(row => controles.every(ctrl => cumple(row, ctrl)));
    const visibles = paginar(filas, coinciden, paginacion, estado, () => apply(false));
    if (counter) counter.textContent = visibles;
  };

  form.addEventListener('input', () => apply());
  form.addEventListener('submit', e => e.preventDefault());
  form.applyFilters = apply;
});

const aplicarFiltros = (tabla, reiniciar = true) => {
  const form = $(`[data-table-filter="${tabla}"]`);
  if (form) form.applyFilters(reiniciar);
};

/* ---------- Inicio de sesión ---------- */
function iniciarLogin() {
  const loginForm = $('#loginForm');
  loginForm.addEventListener('submit', async e => {
    e.preventDefault();
    const error = $('#loginError');
    error.classList.add('d-none');
    if (!loginForm.checkValidity()) {
      loginForm.classList.add('was-validated');
      return;
    }
    const boton = $('button[type="submit"]', loginForm);
    boton.disabled = true;
    const { ok, datos } = await api('/api/login', {
      metodo: 'POST',
      cuerpo: { correo: $('#email').value.trim(), password: $('#password').value }
    });
    if (ok) {
      window.location.href = 'inicio.html';
      return;
    }
    $('span', error).textContent = datos.error || 'No se pudo iniciar sesión.';
    error.classList.remove('d-none');
    boton.disabled = false;
  });

  const olvide = $$('a[href="#"]').find(a => a.textContent.includes('Olvidé'));
  if (olvide) {
    olvide.addEventListener('click', e => {
      e.preventDefault();
      showToast('Pide a otro administrador que active de nuevo tu cuenta: recibirás una contraseña temporal.');
    });
  }
}

/* ---------- Solicitud de cuenta (crear-usuario.html) ---------- */
function iniciarRegistro() {
  const form = $('form');
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const boton = $('button[type="submit"]', form);
    boton.disabled = true;
    const { ok, datos } = await api('/api/registro', {
      metodo: 'POST',
      cuerpo: { nombre: $('#nombre').value, apellido: $('#apellido').value, correo: $('#correo').value }
    });
    $('#avisoRegistro')?.remove();
    const aviso = el('div', `alert alert-${ok ? 'success' : 'danger'} d-flex align-items-center gap-2`);
    aviso.id = 'avisoRegistro';
    aviso.setAttribute('role', 'alert');
    aviso.append(icono(ok ? 'bi-check-circle-fill' : 'bi-exclamation-triangle-fill'), el('span', '', ok ? datos.mensaje : (datos.error || 'No se pudo enviar la solicitud.')));
    form.before(aviso);
    if (ok) form.reset();
    boton.disabled = false;
  });
}

/* ---------- Inicio (resumen general) ---------- */
function itemAccion(punto, titulo, detalle, extra) {
  const item = el('div', 'action-item');
  const info = el('div', 'flex-grow-1');
  info.append(el('div', 'fw-semibold', titulo), el('div', 'cell-sub', detalle));
  item.append(el('span', `action-dot ${punto}`), info);
  if (extra) item.appendChild(extra);
  return item;
}

function enlaceBoton(texto, href) {
  const a = el('a', 'btn btn-sm btn-soft', texto);
  a.href = href;
  return a;
}

async function iniciarInicio() {
  const cuerpoCobertura = $('.coverage-row').parentElement;
  const cardAcciones = $('.action-item').closest('.card');
  const { ok, datos } = await api('/api/inicio');
  if (!ok) return mostrarError(datos);

  const t = datos.totales;
  const valores = [t.instituciones, t.docentes, t.grupos, t.estudiantes];
  $$('.stat-card .stat-value').forEach((nodo, i) => { nodo.textContent = valores[i]; });
  const fecha = $('.topbar-actions span');
  if (fecha) fecha.lastChild.textContent = ` Datos al ${datos.fecha}`;

  // Cobertura por comuna: la barra más larga es la comuna con más estudiantes
  const maximo = Math.max(1, ...datos.cobertura.map(c => c.estudiantes));
  cuerpoCobertura.replaceChildren(...datos.cobertura.map(c => {
    const fila = el('div', 'coverage-row');
    const cabecera = el('div', 'd-flex justify-content-between small mb-1');
    cabecera.append(el('span', 'fw-semibold', c.comuna), el('span', 'fw-bold', c.estudiantes));
    const barra = el('div', 'progress');
    barra.setAttribute('role', 'progressbar');
    barra.setAttribute('aria-label', c.comuna);
    barra.setAttribute('aria-valuenow', c.estudiantes);
    barra.setAttribute('aria-valuemin', 0);
    barra.setAttribute('aria-valuemax', maximo);
    const relleno = el('div', 'progress-bar');
    relleno.style.width = `${Math.round(c.estudiantes * 100 / maximo)}%`;
    barra.appendChild(relleno);
    fila.append(cabecera, barra);
    return fila;
  }));

  // Requieren acción
  $$('.action-item', cardAcciones).forEach(n => n.remove());
  const acciones = [];
  if (t.pendientes) {
    acciones.push(itemAccion('bg-warning', `${plural(t.pendientes, 'docente pendiente', 'docentes pendientes')} de aprobación`,
      'Esperan entrar a su grupo', enlaceBoton('Revisar', 'usuarios.html?estado=Pendiente')));
  }
  if (datos.sin_sincronizar) {
    acciones.push(itemAccion('bg-warning', `${plural(datos.sin_sincronizar, 'dispositivo', 'dispositivos')} sin sincronizar`,
      'Más de 7 días sin conexión', enlaceBoton('Ver', 'monitoreo.html')));
  }
  datos.servicios_caidos.forEach(s => {
    acciones.push(itemAccion('bg-danger', `${s.nombre} sin responder desde las ${s.desde}`,
      s.clave === 'contenido' ? 'Asistente de IA afectado' : 'La app no puede sincronizar el progreso', statusSpan('Crítico')));
  });
  $('.badge', cardAcciones).textContent = acciones.length;
  if (!acciones.length) acciones.push(itemAccion('bg-success', 'Todo en orden', 'No hay tareas pendientes.'));
  cardAcciones.append(...acciones);
}

/* ---------- Actividades ---------- */
function mensajesDeActividades() {
  if (params.get('msg') === 'publicada') showFlash('Actividad publicada. Llega al celular del niño en su próxima sincronización.');
  if (params.get('msg') === 'cambios') showFlash('Cambios publicados. Llegan al celular del niño en su próxima sincronización.');
  if (params.get('msg') === 'borrador') showFlash('Actividad guardada como borrador.');
  if (params.get('eliminada')) showFlash(`Se eliminó la actividad «${params.get('eliminada')}».`);
}

async function iniciarActividades() {
  const tbody = $('#tablaActividades tbody');
  tbody.replaceChildren();
  mensajesDeActividades();
  const { ok, datos } = await api('/api/actividades');
  if (!ok) return mostrarError(datos);

  datos.forEach(a => {
    const tr = el('tr');
    Object.assign(tr.dataset, { id: a.id, materia: a.materia, grado: a.grado, estado: a.estado });
    const tdNombre = el('td');
    tdNombre.append(el('div', 'cell-title', a.nombre), el('div', 'cell-sub', a.tipo));
    const tdEstado = el('td');
    tdEstado.appendChild(statusSpan(a.estado));
    const tdDetalle = el('td', 'text-end');
    tdDetalle.appendChild(enlaceBoton('Ver detalle', `actividad-detalle.html?id=${encodeURIComponent(a.id)}`));
    tr.append(tdNombre, el('td', '', a.materia), el('td', '', a.grado), tdEstado, tdDetalle);
    tbody.appendChild(tr);
  });
  if (!datos.length) filaVacia(tbody, 5, 'Todavía no hay actividades. Crea la primera con «Nueva actividad».');
  $('[data-total]').textContent = datos.length;
  $('[data-count]').textContent = datos.length;
  aplicarFiltros('#tablaActividades');
}

/* ---------- Borradores ---------- */
async function iniciarBorradores() {
  const tbody = $('#tablaBorradores tbody');
  tbody.replaceChildren();
  mensajesDeActividades();
  const { ok, datos } = await api('/api/actividades');
  if (!ok) return mostrarError(datos);

  const borradores = datos.filter(a => a.estado === 'Borrador');
  borradores.forEach(a => {
    const tr = el('tr');
    tr.dataset.id = a.id;
    const tdEstado = el('td');
    tdEstado.appendChild(statusSpan(a.estado));
    const tdAccion = el('td', 'text-end');
    tdAccion.appendChild(enlaceBoton('Continuar editando', `constructor.html?id=${encodeURIComponent(a.id)}`));
    tr.append(el('td', 'cell-title', a.nombre), el('td', '', a.materia), el('td', '', `Grado ${a.grado}`),
      el('td', '', a.tipo), tdEstado, tdAccion);
    tbody.appendChild(tr);
  });
  if (!borradores.length) filaVacia(tbody, 6, 'No hay borradores guardados.');
  $('#draftCount').textContent = plural(borradores.length, 'borrador', 'borradores');
  const badge = $('.section-tabs .badge');
  if (badge) badge.textContent = datos.length;
}

/* ---------- Detalle de actividad ---------- */
async function iniciarDetalle() {
  const id = params.get('id');
  if (!id) {
    window.location.href = 'actividades.html';
    return;
  }
  const { ok, datos: act } = await api(`/api/actividades/${encodeURIComponent(id)}`);
  if (!ok) {
    window.location.href = 'actividades.html';
    return;
  }
  document.title = `${act.nombre} · Numi Admin`;
  $$('[data-act]').forEach(nodo => {
    const key = nodo.dataset.act;
    if (key === 'estadoBadge') setStatus(nodo, act.estado);
    else nodo.textContent = act[key];
  });
  $('#btnEditar').href = `constructor.html?id=${encodeURIComponent(act.id)}`;

  const confirmar = $('#btnConfirmarEliminar');
  confirmar.href = '#';
  confirmar.addEventListener('click', async e => {
    e.preventDefault();
    confirmar.classList.add('disabled');
    const resp = await api(`/api/actividades/${encodeURIComponent(act.id)}`, { metodo: 'DELETE' });
    if (resp.ok) {
      window.location.href = `actividades.html?eliminada=${encodeURIComponent(resp.datos.nombre)}`;
      return;
    }
    bootstrap.Modal.getInstance('#modalEliminar')?.hide();
    mostrarError(resp.datos);
    confirmar.classList.remove('disabled');
  });
}

/* ---------- Constructor de actividades ---------- */
function miniatura(recurso, clase) {
  const nodo = el(clase === 'thumb' ? 'div' : 'span', clase);
  if (recurso.tipo === 'Audio') {
    nodo.appendChild(icono('bi-music-note-beamed'));
  } else if (recurso.tipo === 'Video') {
    nodo.appendChild(icono('bi-film'));
  } else if (recurso.url) {
    // Imagen real de la app: cabe dentro del mismo cuadro que tenía el emoji
    // (.thumb mide 64px de alto y .thumb-sm 40px; sin este límite la imagen se sale)
    const alto = clase === 'thumb' ? '64px' : '40px';
    const img = el('img');
    img.src = recurso.url;
    img.alt = recurso.nombre;
    img.loading = 'lazy';
    Object.assign(img.style, { maxWidth: '100%', maxHeight: alto, objectFit: 'contain' });
    nodo.style.overflow = 'hidden';
    nodo.appendChild(img);
  } else {
    nodo.textContent = recurso.emoji || '🖼️';
  }
  return nodo;
}

/* ---------- Editor de contenido (plantilla Selección múltiple) ---------- */
// El HTML del constructor no trae esta tarjeta: se crea aquí con las mismas clases del diseño.
const TIPOS_CON_PLANTILLA = ['Selección múltiple'];
const MAX_OPCIONES = 4;

function crearEditorContenido(actividad, catalogo) {
  const enApp = Boolean(actividad?.en_app);
  const preguntas = structuredClone(actividad?.contenido?.preguntas || []);
  const preguntaNueva = () => ({
    enunciado: '', audio: null,
    opciones: [{ texto: '', imagen: null, correcta: true }, { texto: '', imagen: null, correcta: false }]
  });

  const filaPrincipal = $('#resourceGrid').closest('.row');
  const aviso = el('div', 'notice mt-4');
  aviso.append(icono('bi-info-circle'), el('div', '', 'La app todavía no tiene plantilla para este tipo de actividad: guárdala como borrador. Por ahora se pueden publicar actividades de tipo Selección múltiple.'));
  const tarjeta = el('div', 'card mt-4');
  const cabecera = el('div', 'card-header d-flex justify-content-between align-items-center flex-wrap gap-2');
  const titulos = el('div');
  const titulo = el('h2', 'card-title');
  titulo.append(icono('bi-ui-checks-grid me-2 text-primary'), 'Contenido');
  titulos.append(titulo, el('span', 'small text-secondary', 'Preguntas que verá el niño. Marca la respuesta correcta de cada una.'));
  const botonAgregar = el('button', 'btn btn-sm btn-soft');
  botonAgregar.type = 'button';
  botonAgregar.append(icono('bi-plus-lg me-1'), 'Agregar pregunta');
  cabecera.append(titulos, botonAgregar);
  const lista = el('div', 'card-body p-4');
  tarjeta.append(cabecera, lista);
  filaPrincipal.after(aviso, tarjeta);

  // Imágenes y audios de la carpeta de la materia elegida, más los generales de la app
  const recursosDe = tipo => {
    const carpeta = `actividades/${CARPETA_MATERIA[$('#actMateria').value]}`;
    return catalogo.filter(r => r.tipo === tipo && r.compatible && (r.carpeta === carpeta || r.carpeta === 'app/general'));
  };
  const selectRecurso = (tipo, elegido, vacio) => {
    const select = el('select', 'form-select form-select-sm');
    const opciones = recursosDe(tipo);
    const actual = catalogo.find(r => r.id === elegido);
    if (actual && !opciones.includes(actual)) opciones.unshift(actual); // conserva lo ya elegido
    select.append(el('option', '', vacio), ...opciones.map(r => {
      const op = el('option', '', r.nombre);
      op.value = r.id;
      return op;
    }));
    select.value = elegido ?? '';
    return select;
  };

  const render = () => {
    lista.replaceChildren();
    if (!preguntas.length) lista.appendChild(el('p', 'text-secondary mb-0', 'Todavía no hay preguntas. Usa «Agregar pregunta».'));
    preguntas.forEach((p, i) => {
      const bloque = el('div', 'border rounded-4 p-3 mb-3');
      const encabezado = el('div', 'd-flex justify-content-between align-items-center mb-2');
      const quitar = el('button', 'btn btn-sm btn-outline-danger', 'Quitar pregunta');
      quitar.type = 'button';
      quitar.addEventListener('click', () => { preguntas.splice(i, 1); render(); });
      encabezado.append(el('span', 'fw-bold', `Pregunta ${i + 1}`), quitar);

      const fila = el('div', 'row g-3 mb-3');
      const colTexto = el('div', 'col-md-8');
      const enunciado = el('input', 'form-control');
      enunciado.maxLength = 200;
      enunciado.placeholder = 'Ej. ¿Cuál de estos es una fruta?';
      enunciado.value = p.enunciado;
      enunciado.addEventListener('input', () => { p.enunciado = enunciado.value; });
      colTexto.append(el('label', 'form-label', 'Enunciado'), enunciado);
      const colAudio = el('div', 'col-md-4');
      const audio = selectRecurso('Audio', p.audio, 'Sin audio');
      audio.addEventListener('change', () => { p.audio = audio.value ? Number(audio.value) : null; });
      colAudio.append(el('label', 'form-label', 'Audio de la pregunta (opcional)'), audio);
      fila.append(colTexto, colAudio);

      const opciones = el('div');
      p.opciones.forEach((o, j) => {
        const filaOpcion = el('div', 'd-flex align-items-center gap-2 mb-2');
        const correcta = el('input', 'form-check-input mt-0');
        correcta.type = 'radio';
        correcta.name = `correcta-${i}`;
        correcta.checked = o.correcta;
        correcta.title = 'Respuesta correcta';
        correcta.setAttribute('aria-label', 'Respuesta correcta');
        correcta.addEventListener('change', () => p.opciones.forEach((otra, k) => { otra.correcta = k === j; }));
        const texto = el('input', 'form-control form-control-sm');
        texto.maxLength = 60;
        texto.placeholder = `Opción ${j + 1}`;
        texto.value = o.texto;
        texto.addEventListener('input', () => { o.texto = texto.value; });
        const vista = el('span', 'thumb-sm flex-shrink-0');
        const pintarVista = () => {
          const recurso = catalogo.find(r => r.id === o.imagen);
          vista.replaceChildren(...(recurso ? miniatura(recurso, 'thumb-sm').childNodes : []));
        };
        const imagen = selectRecurso('Imagen', o.imagen, 'Sin imagen');
        imagen.style.maxWidth = '220px';
        imagen.addEventListener('change', () => { o.imagen = imagen.value ? Number(imagen.value) : null; pintarVista(); });
        pintarVista();
        const borrar = el('button', 'btn btn-sm btn-light');
        borrar.type = 'button';
        borrar.setAttribute('aria-label', 'Quitar opción');
        borrar.appendChild(icono('bi-x-lg'));
        borrar.disabled = p.opciones.length <= 2;
        borrar.addEventListener('click', () => {
          p.opciones.splice(j, 1);
          if (!p.opciones.some(x => x.correcta)) p.opciones[0].correcta = true;
          render();
        });
        filaOpcion.append(correcta, texto, vista, imagen, borrar);
        opciones.appendChild(filaOpcion);
      });
      if (p.opciones.length < MAX_OPCIONES) {
        const agregar = el('button', 'btn btn-sm btn-soft mt-1');
        agregar.type = 'button';
        agregar.append(icono('bi-plus-lg me-1'), 'Agregar opción');
        agregar.addEventListener('click', () => { p.opciones.push({ texto: '', imagen: null, correcta: false }); render(); });
        opciones.appendChild(agregar);
      }
      bloque.append(encabezado, fila, el('div', 'small fw-semibold mb-2', 'Opciones (marca la correcta)'), opciones);
      lista.appendChild(bloque);
    });
  };

  const usaPlantilla = () => !enApp && TIPOS_CON_PLANTILLA.includes($('#actTipo').value);
  const actualizar = () => {
    tarjeta.classList.toggle('d-none', !usaPlantilla());
    aviso.classList.toggle('d-none', enApp || usaPlantilla());
  };
  botonAgregar.addEventListener('click', () => { preguntas.push(preguntaNueva()); render(); });
  $('#actTipo').addEventListener('change', actualizar);
  $('#actMateria').addEventListener('change', render);
  render();
  actualizar();

  return {
    contenido: () => (usaPlantilla() ? { preguntas } : null),
    cantidad: () => (usaPlantilla() ? preguntas.length : null)
  };
}

async function iniciarConstructor() {
  const id = params.get('id');
  const grid = $('#resourceGrid');
  const botonMas = $('.add-tile', grid);
  const tbodyModal = $('#tablaRecursosModal tbody');
  const filtroTipoModal = $('#modalRecursos .modal-body select');
  const contadorModal = $('#modalRecursos .modal-body > .d-flex span');
  const paginacionModal = $('#modalRecursos .pagination');
  const estadoModal = { pagina: 1 };
  const selected = new Map();
  $$('.resource-tile:not(.add-tile)', grid).forEach(n => n.remove());
  tbodyModal.replaceChildren();

  const [respRecursos, respActividad] = await Promise.all([
    api('/api/recursos'),
    id ? api(`/api/actividades/${encodeURIComponent(id)}`) : Promise.resolve(null)
  ]);
  if (!respRecursos.ok) return mostrarError(respRecursos.datos);
  const catalogo = respRecursos.datos.recursos;
  const meta = respRecursos.datos;
  const buscarRecurso = valor => catalogo.find(r => String(r.id) === String(valor));

  let actividad = null;
  if (respActividad && respActividad.ok) actividad = respActividad.datos;
  else if (respActividad) mostrarError(respActividad.datos);
  const esEdicion = Boolean(actividad) && actividad.estado !== 'Borrador';

  if (actividad) {
    $('#actNombre').value = actividad.nombre;
    $('#actMateria').value = actividad.materia;
    $('#actGrado').value = `Grado ${actividad.grado}`;
    $('#actTipo').value = actividad.tipo;
    actividad.recursos.forEach(r => selected.set(String(r.id), buscarRecurso(r.id)));
  }
  if (esEdicion) {
    document.title = 'Editar actividad · Numi Admin';
    $('#builderTitle').textContent = 'Editar actividad';
    $('#builderCrumb').innerHTML = '<li class="breadcrumb-item"><a href="actividades.html">Actividades</a></li><li class="breadcrumb-item"></li><li class="breadcrumb-item active" aria-current="page">Editar</li>';
    const crumb = $('#builderCrumb .breadcrumb-item:nth-child(2)');
    const link = document.createElement('a');
    link.href = `actividad-detalle.html?id=${encodeURIComponent(actividad.id)}`;
    link.textContent = actividad.nombre;
    crumb.appendChild(link);
    $('#resEstado').textContent = 'Publicada (reemplaza la versión actual)';
  }

  // Selección sincronizada entre la cuadrícula y el modal "Más recursos"
  const allChecks = () => $$('input[type="checkbox"]', grid).concat($$('input[type="checkbox"]', tbodyModal));
  const render = () => {
    allChecks().forEach(cb => { cb.checked = selected.has(cb.value); });
    const n = selected.size;
    $('#selCount').textContent = `${n} seleccionado${n === 1 ? '' : 's'}`;
  };
  const alCambiar = e => {
    const cb = e.target;
    if (cb.type !== 'checkbox') return;
    if (cb.checked) selected.set(cb.value, buscarRecurso(cb.value));
    else selected.delete(cb.value);
    render();
  };
  grid.addEventListener('change', alCambiar);
  tbodyModal.addEventListener('change', alCambiar);

  // Cuadrícula: imágenes de la carpeta de la materia elegida
  const tarjeta = recurso => {
    const label = el('label', `resource-tile${recurso.compatible ? '' : ' is-disabled'}`);
    if (!recurso.compatible) label.title = `Disponible desde v${recurso.version_minima}`;
    const input = el('input');
    input.type = 'checkbox';
    input.value = recurso.id;
    input.dataset.tipo = recurso.tipo;
    input.disabled = !recurso.compatible;
    const check = el('span', 'check');
    check.appendChild(icono('bi-check-lg'));
    label.append(input, check, miniatura(recurso, 'thumb'), el('div', 'name', recurso.nombre));
    return label;
  };
  const cardRecursos = grid.closest('.card');
  const renderGrid = () => {
    const carpeta = `actividades/${CARPETA_MATERIA[$('#actMateria').value]}`;
    $('.card-header code', cardRecursos).textContent = `assets/images/${carpeta}`;
    $$('.resource-tile:not(.add-tile)', grid).forEach(n => n.remove());
    const recientes = catalogo.filter(r => r.carpeta === carpeta && r.tipo === 'Imagen').slice(0, 5);
    recientes.forEach(r => grid.insertBefore(tarjeta(r), botonMas));

    const alerta = $('.alert-warning', cardRecursos);
    const bloqueados = recientes.filter(r => !r.compatible);
    alerta.classList.toggle('d-none', !bloqueados.length);
    if (bloqueados.length) {
      const b = bloqueados[0];
      $('div', alerta).replaceChildren(
        el('strong', '', bloqueados.map(r => r.nombre).join(', ')),
        document.createTextNode(` está atenuada porque llegó en la v${b.version_minima}. Los ${b.equipos_incompatibles} equipos con versiones anteriores no podrían mostrar esta actividad.`)
      );
    }
    render();
  };
  $('#actMateria').addEventListener('change', renderGrid);
  const editor = crearEditorContenido(actividad, catalogo);

  // Modal "Más recursos": todo el catálogo, con búsqueda, tipo y páginas
  catalogo.forEach(r => {
    const tr = el('tr', r.compatible ? '' : 'opacity-50');
    tr.dataset.tipo = r.tipo;
    const tdCheck = el('td');
    const input = el('input', 'form-check-input');
    input.type = 'checkbox';
    input.value = r.id;
    input.dataset.tipo = r.tipo;
    input.disabled = !r.compatible;
    input.setAttribute('aria-label', r.nombre);
    tdCheck.appendChild(input);
    const tdVista = el('td');
    tdVista.appendChild(miniatura(r, 'thumb-sm'));
    const tdCompat = el('td');
    tdCompat.appendChild(el('span', `status ${r.version_minima ? 'status-warning' : 'status-success'}`, r.compatibilidad));
    tr.append(tdCheck, tdVista, el('td', 'fw-semibold', r.nombre), el('td', '', r.tipo), tdCompat);
    tbodyModal.appendChild(tr);
  });
  const filtrarModal = (reiniciar = true) => {
    if (reiniciar) estadoModal.pagina = 1;
    const q = $('#buscarRecursoModal').value.trim().toLowerCase();
    const tipo = ['', 'Imagen', 'Audio'][filtroTipoModal.selectedIndex];
    const filas = $$('tr', tbodyModal);
    const coinciden = filas.filter(r => r.textContent.toLowerCase().includes(q) && (!tipo || r.dataset.tipo === tipo));
    const visibles = paginar(filas, coinciden, paginacionModal, estadoModal, () => filtrarModal(false));
    contadorModal.textContent = `${visibles} de ${catalogo.length} recursos`;
  };
  $('#buscarRecursoModal').addEventListener('input', () => filtrarModal());
  filtroTipoModal.addEventListener('change', () => filtrarModal());

  // Resumen antes de publicar
  $('#modalResumen').addEventListener('show.bs.modal', () => {
    $('#resNombre').textContent = $('#actNombre').value || 'Sin nombre';
    $('#resMateria').textContent = $('#actMateria').value;
    $('#resGrado').textContent = $('#actGrado').value;
    $('#resTipo').textContent = $('#actTipo').value;
    $('#resCount').textContent = `${selected.size} recurso${selected.size === 1 ? '' : 's'}`;
    const list = $('#resLista');
    list.replaceChildren();
    selected.forEach(recurso => list.appendChild(el('li', '', `${recurso.nombre} · ${recurso.tipo}`)));

    // Fila "Preguntas" en el resumen (solo para actividades con plantilla)
    let filaPreguntas = $('#resPreguntas');
    if (!filaPreguntas) {
      const estado = $('#resEstado').closest('dd').previousElementSibling;
      filaPreguntas = el('dd', 'col-7');
      filaPreguntas.id = 'resPreguntas';
      estado.before(el('dt', 'col-5', 'Preguntas'), filaPreguntas);
    }
    const cantidad = editor.cantidad();
    filaPreguntas.textContent = cantidad === null ? 'No aplica (pantalla propia de la app)' : plural(cantidad, 'pregunta', 'preguntas');

    const [equipos, nuevos] = $$('#modalResumen .bg-light > .d-flex');
    const [eqTitulo, eqValor] = $$('span', equipos);
    eqTitulo.textContent = meta.version_desactualizada ? `Equipos con v${meta.version_desactualizada}` : 'Equipos desactualizados';
    eqValor.textContent = meta.equipos_desactualizados
      ? `${meta.equipos_desactualizados} equipos no reciben actividades nuevas`
      : 'Todos los equipos reciben actividades nuevas';
    eqValor.className = `${meta.equipos_desactualizados ? 'text-warning-emphasis' : 'text-success'} fw-semibold text-end`;

    const [nvTitulo, nvValor] = $$('span', nuevos);
    const conVersion = [...selected.values()].filter(r => r.version_minima);
    nvTitulo.textContent = 'Recursos nuevos';
    nvValor.textContent = conVersion.length
      ? `Usa ${conVersion.map(r => r.nombre).join(', ')}: requiere v${conVersion[0].version_minima}`
      : 'No usa recursos nuevos: compatible con todas las versiones';
    nvValor.className = `${conVersion.length ? 'text-warning-emphasis' : 'text-success'} fw-semibold text-end`;
  });

  // Guardar: borrador o publicada
  const guardar = async (estado, boton) => {
    const nombre = $('#actNombre').value.trim();
    if (!nombre) {
      bootstrap.Modal.getInstance('#modalResumen')?.hide();
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
      contenido: editor.contenido()
    };
    const { ok, datos } = actividad
      ? await api(`/api/actividades/${encodeURIComponent(actividad.id)}`, { metodo: 'PUT', cuerpo })
      : await api('/api/actividades', { metodo: 'POST', cuerpo });
    if (!ok) {
      bootstrap.Modal.getInstance('#modalResumen')?.hide();
      mostrarError(datos);
      boton.classList.remove('disabled');
      return;
    }
    if (estado === 'Borrador') window.location.href = 'borradores.html?msg=borrador';
    else window.location.href = `actividades.html?msg=${esEdicion ? 'cambios' : 'publicada'}`;
  };
  $('#btnBorrador').addEventListener('click', e => { e.preventDefault(); guardar('Borrador', e.currentTarget); });
  $('#btnContinuar').addEventListener('click', e => { e.preventDefault(); guardar('Publicada', e.currentTarget); });

  renderGrid();
  filtrarModal();
}

/* ---------- Recursos ---------- */
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

function iniciarRecursos() {
  const modal = $('#modalSubir');
  const botonSubir = $('.modal-footer .btn-primary', modal);
  delete botonSubir.dataset.toast; // el mensaje lo da el resultado real de la carga
  crearPestanaVideos();
  cargarRecursos();

  // Subir archivos: botón "Seleccionar carpeta" o arrastrar a la zona
  const input = $('input[type="file"]', modal);
  const zona = $('.dropzone', modal);
  const ayuda = $('p.small', zona);
  let elegidos = [];
  const elegir = archivos => {
    elegidos = Array.from(archivos);
    ayuda.textContent = elegidos.length ? `${plural(elegidos.length, 'archivo listo', 'archivos listos')} para subir` : 'PNG, JPG, MP3 o MP4';
  };
  input.accept = '.png,.jpg,.jpeg,.mp3,.mp4';
  input.addEventListener('change', () => elegir(input.files));
  zona.addEventListener('dragover', e => e.preventDefault());
  zona.addEventListener('drop', e => {
    e.preventDefault();
    elegir(e.dataTransfer.files);
  });
  modal.addEventListener('hidden.bs.modal', () => { input.value = ''; elegir([]); });

  botonSubir.addEventListener('click', async () => {
    if (!elegidos.length) {
      showToast('Selecciona al menos un archivo PNG, JPG, MP3 o MP4.');
      return;
    }
    const formulario = new FormData();
    elegidos.forEach(archivo => formulario.append('archivos', archivo));
    const carpeta = $('#carpeta');
    formulario.append('carpeta', carpeta.selectedIndex > 0 ? carpeta.value : '');
    showToast('Carpeta enviada. Los recursos aparecerán cuando termine la carga.');
    const { datos } = await api('/api/recursos', { metodo: 'POST', formulario });
    if (!datos.subidos) return mostrarError(datos);
    const partes = [];
    if (datos.subidos.length) partes.push(`Se ${datos.subidos.length === 1 ? 'subió' : 'subieron'} ${plural(datos.subidos.length, 'recurso', 'recursos')}.`);
    if (datos.omitidos.length) partes.push(`Omitidos: ${datos.omitidos.join('; ')}.`);
    showToast(partes.join(' '));
    cargarRecursos();
  });
}

async function cargarRecursos() {
  const { ok, datos } = await api('/api/recursos');
  if (!ok) return mostrarError(datos);
  const paneles = [
    { tipo: 'Imagen', carpetaBase: 'images', panel: $('#tabImagenes'), estado: { pagina: 1 } },
    { tipo: 'Audio', carpetaBase: 'audio', panel: $('#tabAudio'), estado: { pagina: 1 } },
    { tipo: 'Video', carpetaBase: 'videos', panel: $('#tabVideos'), estado: { pagina: 1 } }
  ];

  // Filtro de carpetas con las carpetas que existen de verdad
  const selectCarpeta = $('#carpeta');
  const elegida = selectCarpeta.selectedIndex > 0 ? selectCarpeta.value : '';
  const carpetas = [...new Set(datos.recursos.map(r => r.carpeta))].sort();
  llenarSelect(selectCarpeta, carpetas, true);
  if (carpetas.includes(elegida)) selectCarpeta.value = elegida;

  paneles.forEach(p => {
    asegurarPaginacion(p.panel);
    const tbody = $('tbody', p.panel);
    tbody.replaceChildren();
    datos.recursos.filter(r => r.tipo === p.tipo).forEach(r => {
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
    paneles.forEach(p => {
      if (reiniciar) p.estado.pagina = 1;
      const filas = $$('tbody tr', p.panel);
      const coinciden = filas.filter(r => r.textContent.toLowerCase().includes(q)
        && (!carpeta || r.dataset.carpeta === carpeta) && (!compat || r.dataset.compat === compat));
      const visibles = paginar(filas, coinciden, $('.pagination', p.panel), p.estado, () => filtrar(false));
      $('.table-footer > span', p.panel).textContent = `${visibles} de ${datos.recursos.length} recursos`;
      $('.card-header', p.panel).replaceChildren(icono('bi-folder2-open me-1'), ` assets/${p.carpetaBase}/${carpeta || 'actividades'}`);
    });
  };
  const form = $('form.filters');
  form.oninput = () => filtrar();
  form.onsubmit = e => e.preventDefault();
  filtrar();
}

/* ---------- Instituciones ---------- */
async function iniciarInstituciones() {
  const tbody = $('#tablaInstituciones tbody');
  tbody.replaceChildren();
  if (params.get('msg') === 'institucion') showFlash('Institución creada. Ya puedes agregar sus grupos.');

  $('#modalInstitucion').addEventListener('show.bs.modal', async e => {
    const instId = e.relatedTarget?.dataset.inst;
    if (!instId) return;
    const list = $('#instGrupos');
    list.replaceChildren();
    const { ok, datos: inst } = await api(`/api/instituciones/${instId}`);
    if (!ok) return mostrarError(inst);
    $('#modalInstitucionTitulo').textContent = inst.nombre;
    $('#instEstado').textContent = inst.estado;
    $('#instEstado').className = `fw-bold ${inst.estado === 'Activa' ? 'text-success' : 'text-secondary'}`;
    $('#instComuna').textContent = inst.comuna;
    $('#instSedes').textContent = inst.sedes;
    $('#instEstudiantes').textContent = inst.estudiantes;
    inst.grupos.forEach(({ nombre, docente }) => {
      const li = el('li', 'list-group-item d-flex justify-content-between align-items-center gap-2');
      li.append(el('span', 'fw-semibold', nombre), el('span', docente ? 'small text-secondary text-end' : 'status status-warning', docente || 'Sin docente asignado'));
      list.appendChild(li);
    });
    if (!inst.grupos.length) list.appendChild(el('li', 'list-group-item small text-secondary', 'Todavía no tiene grupos.'));
  });

  const { ok, datos } = await api('/api/instituciones');
  if (!ok) return mostrarError(datos);
  datos.forEach(i => {
    const tr = el('tr');
    Object.assign(tr.dataset, { comuna: i.comuna, estado: i.estado });
    const tdEstado = el('td');
    tdEstado.appendChild(statusSpan(i.estado));
    const tdDetalle = el('td', 'text-end');
    const boton = el('button', 'btn btn-sm btn-soft', 'Ver detalle');
    boton.type = 'button';
    Object.assign(boton.dataset, { bsToggle: 'modal', bsTarget: '#modalInstitucion', inst: i.id });
    tdDetalle.appendChild(boton);
    tr.append(el('td', 'cell-title', i.nombre), el('td', '', i.comuna), el('td', '', i.sedes), el('td', '', i.estudiantes), tdEstado, tdDetalle);
    tbody.appendChild(tr);
  });
  fijarTotal($('[data-visible]', tbody.closest('.card')), datos.length, 'instituciones');
  aplicarFiltros('#tablaInstituciones');
}

function iniciarInstitucionNueva() {
  const form = $('#formInstitucion');
  const nombre = $('#instNombre');
  const avisoNombre = nombre.nextElementSibling;
  const textoOriginal = avisoNombre.textContent;
  nombre.addEventListener('input', () => {
    nombre.setCustomValidity('');
    avisoNombre.textContent = textoOriginal;
  });
  form.addEventListener('submit', async e => {
    e.preventDefault();
    if (!form.checkValidity()) {
      form.classList.add('was-validated');
      return;
    }
    const { ok, status, datos } = await api('/api/instituciones', {
      metodo: 'POST',
      cuerpo: { nombre: nombre.value, comuna: $('#instComunaSel').value, sedes: $('#instSedesNum').value, estado: $('#instEstadoSel').value }
    });
    if (ok) {
      window.location.href = 'instituciones.html?msg=institucion';
      return;
    }
    if (status === 409) {
      nombre.setCustomValidity(datos.error);
      avisoNombre.textContent = datos.error;
      form.classList.add('was-validated');
    } else {
      mostrarError(datos);
    }
  });
}

/* ---------- Usuarios ---------- */
function llenarSelect(select, opciones, conservarPrimera = false) {
  const primera = conservarPrimera ? [select.options[0]] : [];
  select.replaceChildren(...primera, ...opciones.map(texto => el('option', '', texto)));
}

// Ventana con la contraseña temporal: se muestra una sola vez y se puede copiar
function mostrarPasswordTemporal(nombre, password) {
  let modal = $('#modalPasswordTemporal');
  if (!modal) {
    document.body.insertAdjacentHTML('beforeend', `
      <div class="modal fade" id="modalPasswordTemporal" tabindex="-1" aria-labelledby="passwordTemporalTitulo" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-body text-center p-4">
              <div class="danger-icon bg-success-subtle text-success"><i class="bi bi-key"></i></div>
              <h2 class="h5 fw-bold" id="passwordTemporalTitulo"></h2>
              <p class="text-secondary">Compártela solo con esa persona. Por seguridad <strong>no se volverá a mostrar</strong>.</p>
              <div class="border rounded-3 p-3 fs-3 fw-bold font-monospace mb-3" data-password></div>
              <button type="button" class="btn btn-primary" data-copiar><i class="bi bi-clipboard me-1"></i> Copiar contraseña</button>
            </div>
            <div class="modal-footer justify-content-center border-0 pt-0 pb-4">
              <button type="button" class="btn btn-light" data-bs-dismiss="modal">Listo, ya la guardé</button>
            </div>
          </div>
        </div>
      </div>`);
    modal = $('#modalPasswordTemporal');
    $('[data-copiar]', modal).addEventListener('click', () => {
      const texto = $('[data-password]', modal).textContent;
      const listo = () => showToast('Contraseña copiada.');
      if (navigator.clipboard) navigator.clipboard.writeText(texto).then(listo, listo);
      else listo();
    });
  }
  $('#passwordTemporalTitulo', modal).textContent = `Contraseña temporal de ${nombre}`;
  $('[data-password]', modal).textContent = password;
  bootstrap.Modal.getOrCreateInstance(modal).show();
}

// "Grupos a cargo" dentro de los modales Crear / Editar usuario (el HTML no lo trae).
// Muestra los grupos de la institución elegida y permite crear uno nuevo.
function crearSelectorGrupos(modal, selectRol, selectInst, instituciones) {
  const bloque = el('div', 'mt-3');
  bloque.innerHTML = `
    <label class="form-label">Grupos a cargo</label>
    <p class="small text-secondary mb-2">Marca los grados y grupos que manejará el docente. Puede tener varios.</p>
    <div class="d-grid gap-1 mb-2" data-lista></div>
    <div class="d-flex gap-2 align-items-center flex-wrap">
      <select class="form-select form-select-sm w-auto" aria-label="Grado del grupo nuevo" data-grado>
        ${[1, 2, 3, 4, 5].map(g => `<option value="${g}">Grado ${g}°</option>`).join('')}
      </select>
      <select class="form-select form-select-sm w-auto" aria-label="Letra del grupo nuevo" data-letra>
        ${'ABCDEFGH'.split('').map(l => `<option>${l}</option>`).join('')}
      </select>
      <button type="button" class="btn btn-sm btn-soft" data-crear><i class="bi bi-plus-lg me-1"></i>Crear grupo</button>
    </div>`;
  $('.modal-body', modal).appendChild(bloque);
  const lista = $('[data-lista]', bloque);
  let usuarioId = null;
  let grupos = [];

  const institucionId = () => instituciones().find(i => i.nombre === selectInst.value)?.id;
  const marcados = () => $$('input[type="checkbox"]:checked', lista).map(cb => Number(cb.value));
  const visible = () => selectRol.value === 'Docente' && Boolean(institucionId());

  const pintar = seleccion => {
    lista.replaceChildren();
    if (!grupos.length) lista.appendChild(el('span', 'small text-secondary', 'Esta institución todavía no tiene grupos: crea uno abajo.'));
    grupos.forEach(g => {
      const fila = el('div', 'form-check mb-0');
      const cb = el('input', 'form-check-input');
      cb.type = 'checkbox';
      cb.value = g.id;
      cb.id = `grupo-${modal.id}-${g.id}`;
      cb.checked = seleccion.includes(g.id);
      const etiqueta = el('label', 'form-check-label', g.nombre);
      etiqueta.htmlFor = cb.id;
      if (g.docente_id && g.docente_id !== usuarioId) {
        etiqueta.append(' ', el('span', 'small text-secondary', `(hoy: ${g.docente_nombre}; si lo marcas, pasa a este docente)`));
      }
      fila.append(cb, etiqueta);
      lista.appendChild(fila);
    });
  };

  const cargar = async (seleccion = []) => {
    bloque.classList.toggle('d-none', !visible());
    if (!visible()) return;
    const { ok, datos } = await api(`/api/instituciones/${institucionId()}`);
    grupos = ok ? datos.grupos : [];
    pintar(seleccion);
  };

  $('[data-crear]', bloque).addEventListener('click', async () => {
    const { ok, datos } = await api(`/api/instituciones/${institucionId()}/grupos`, {
      metodo: 'POST', cuerpo: { grado: $('[data-grado]', bloque).value, letra: $('[data-letra]', bloque).value }
    });
    if (!ok) return mostrarError(datos);
    showToast(`Se creó el grupo ${datos.corto}.`);
    await cargar([...marcados(), datos.id]);
  });
  selectRol.addEventListener('change', () => cargar(marcados()));
  selectInst.addEventListener('change', () => cargar([]));

  return {
    abrir: (id, seleccion) => { usuarioId = id; return cargar(seleccion); },
    ids: () => (visible() ? marcados() : [])
  };
}

function iniciarUsuarios() {
  const tablaUsuarios = $('#tablaUsuarios');
  const tbody = $('tbody', tablaUsuarios);
  const modalEditar = new bootstrap.Modal('#modalEditar');
  const modalConfirmar = new bootstrap.Modal('#modalConfirmarEstado');
  const modalCrearEl = $('#modalCrear');
  const modalImportar = $('#modalImportar');
  const botonImportar = $('.modal-footer .btn-primary', modalImportar);
  delete botonImportar.dataset.toast; // el mensaje lo da el resultado real de la importación
  let actual = null;
  let instituciones = []; // [{id, nombre}] para saber de qué institución pedir los grupos
  tbody.replaceChildren();

  const gruposEditar = crearSelectorGrupos($('#modalEditar'), $('#edRol'), $('#edInst'), () => instituciones);
  const gruposCrear = crearSelectorGrupos(modalCrearEl, $('#crRol'), $('#crInst'), () => instituciones);
  modalCrearEl.addEventListener('show.bs.modal', () => gruposCrear.abrir(null, []));

  // Sección "Contraseña" en el modal Editar (el HTML no la trae).
  // Pide un segundo clic para confirmar, porque la contraseña anterior deja de servir.
  const bloqueContrasena = el('div', 'mt-3');
  bloqueContrasena.innerHTML = `
    <label class="form-label">Contraseña</label>
    <p class="small text-secondary mb-2">Por seguridad no se puede ver. Si el usuario no la sabe, genera una temporal nueva.</p>`;
  const btnRestablecer = el('button', '', '');
  btnRestablecer.type = 'button';
  bloqueContrasena.appendChild(btnRestablecer);
  $('#modalEditar .modal-body').appendChild(bloqueContrasena);
  const prepararRestablecer = () => {
    btnRestablecer.innerHTML = '<i class="bi bi-key me-1"></i>Restablecer contraseña';
    btnRestablecer.className = 'btn btn-sm btn-outline-secondary';
    delete btnRestablecer.dataset.confirmar;
  };
  btnRestablecer.addEventListener('click', async () => {
    if (!btnRestablecer.dataset.confirmar) {
      btnRestablecer.dataset.confirmar = '1';
      btnRestablecer.textContent = '¿Seguro? La anterior dejará de servir';
      btnRestablecer.className = 'btn btn-sm btn-warning';
      return;
    }
    const { ok, datos } = await api(`/api/usuarios/${actual.id}/password-temporal`, { metodo: 'POST' });
    prepararRestablecer();
    if (!ok) return mostrarError(datos);
    modalEditar.hide();
    mostrarPasswordTemporal(actual.nombre_completo, datos.password_temporal);
  });

  const abrirEditar = u => {
    actual = u;
    $('#modalEditarTitulo').textContent = u.nombre_completo;
    $('#edNombre').value = u.nombre;
    $('#edApellido').value = u.apellido;
    $('#edCorreo').value = u.correo;
    $('#edRol').value = u.rol;
    $('#edInst').value = u.institucion;
    gruposEditar.abrir(u.id, u.grupos.map(g => g.id));
    const activar = u.estado !== 'Activo';
    $('#btnToggleEstado').textContent = activar ? 'Activar usuario' : 'Desactivar usuario';
    $('#btnToggleEstado').className = activar ? 'btn btn-outline-success' : 'btn btn-outline-danger';
    prepararRestablecer();
    bloqueContrasena.classList.toggle('d-none', u.estado !== 'Activo'); // solo cuentas activas
    modalEditar.show();
  };

  const filaUsuario = u => {
    const tr = el('tr');
    Object.assign(tr.dataset, { user: u.id, rol: u.rol, institucion: u.institucion, estado: u.estado });
    const tdUsuario = el('td');
    const wrap = el('div', 'd-flex align-items-center gap-2');
    const textos = el('div');
    const nombre = el('div', 'cell-title', u.nombre_completo);
    nombre.dataset.field = 'nombre';
    textos.append(nombre, el('div', 'cell-sub', u.correo));
    wrap.append(el('span', 'avatar', u.iniciales), textos);
    tdUsuario.appendChild(wrap);
    const tdEstado = el('td');
    tdEstado.dataset.field = 'estado';
    tdEstado.appendChild(statusSpan(u.estado));
    const tdAccion = el('td', 'text-end');
    const editar = el('button', 'btn btn-sm btn-soft', 'Editar');
    editar.type = 'button';
    editar.addEventListener('click', () => abrirEditar(u));
    tdAccion.appendChild(editar);
    // Institución y, debajo, los grupos que maneja el docente
    const tdInstitucion = el('td');
    tdInstitucion.append(el('div', '', u.institucion));
    if (u.grupos.length) tdInstitucion.append(el('div', 'cell-sub', u.grupos.map(g => g.corto).join(' · ')));
    tr.append(tdUsuario, el('td', '', u.rol), tdInstitucion, el('td', 'text-nowrap', u.ultimo_acceso), tdEstado, tdAccion);
    return tr;
  };

  const cargar = async (reiniciar = true) => {
    const { ok, datos } = await api('/api/usuarios');
    if (!ok) return mostrarError(datos);
    tbody.replaceChildren(...datos.map(filaUsuario));
    const pendientes = datos.filter(u => u.estado === 'Pendiente').length;
    const aviso = $('.alert-warning', $('main'));
    aviso.classList.toggle('d-none', !pendientes);
    $('strong', aviso).textContent = plural(pendientes, 'docente', 'docentes');
    $('span.flex-grow-1', aviso).lastChild.textContent = pendientes === 1
      ? ' espera aprobación para entrar a su grupo.'
      : ' esperan aprobación para entrar a su grupo.';
    fijarTotal($('[data-visible]', tablaUsuarios.closest('.card')), datos.length, 'usuarios');
    aplicarFiltros('#tablaUsuarios', reiniciar);
  };

  $('#btnToggleEstado').addEventListener('click', () => {
    const activar = actual.estado !== 'Activo';
    const nombre = actual.nombre_completo;
    $('#modalConfirmarTitulo').textContent = activar ? `¿Activar a ${nombre}?` : `¿Desactivar a ${nombre}?`;
    $('#confirmTexto').textContent = activar
      ? (actual.estado === 'Pendiente'
        ? 'Se aprueba la cuenta y podrá iniciar sesión en Numi. Si no tiene contraseña, se genera una temporal.'
        : 'Podrá volver a iniciar sesión en Numi con su correo institucional.')
      : 'No podrá iniciar sesión en Numi. El registro no se elimina: queda en la lista de usuarios con estado Inactivo.';
    $('#btnConfirmarEstado').textContent = activar ? 'Activar' : 'Desactivar';
    $('#btnConfirmarEstado').className = activar ? 'btn btn-success' : 'btn btn-danger';
    $('#confirmIcon').className = activar ? 'danger-icon bg-success-subtle text-success' : 'danger-icon';
    modalEditar.hide();
    modalConfirmar.show();
  });

  $('#btnConfirmarEstado').addEventListener('click', async () => {
    const activar = actual.estado !== 'Activo';
    const nombre = actual.nombre_completo;
    const { ok, datos } = await api(`/api/usuarios/${actual.id}/estado`, {
      metodo: 'PATCH', cuerpo: { estado: activar ? 'Activo' : 'Inactivo' }
    });
    modalConfirmar.hide();
    if (!ok) return mostrarError(datos);
    let mensaje = activar
      ? `Se activó la cuenta de ${nombre}. Ya puede iniciar sesión en Numi.`
      : `Se desactivó la cuenta de ${nombre}. Su registro no se eliminó: sigue en la lista como Inactivo.`;
    showFlash(mensaje);
    // La contraseña temporal va en su propia ventana para que no pase desapercibida
    if (datos.password_temporal) mostrarPasswordTemporal(nombre, datos.password_temporal);
    cargar(false);
  });

  $('#formEditar').addEventListener('submit', async e => {
    e.preventDefault();
    const { ok, datos } = await api(`/api/usuarios/${actual.id}`, {
      metodo: 'PUT',
      cuerpo: { nombre: $('#edNombre').value, apellido: $('#edApellido').value, correo: $('#edCorreo').value, rol: $('#edRol').value, institucion: $('#edInst').value, grupos: gruposEditar.ids() }
    });
    if (!ok) return mostrarError(datos);
    modalEditar.hide();
    showFlash(`Se guardaron los cambios de ${datos.nombre_completo}.`);
    cargar(false);
  });

  $('#formCrear').addEventListener('submit', async e => {
    e.preventDefault();
    const { ok, datos } = await api('/api/usuarios', {
      metodo: 'POST',
      cuerpo: { nombre: $('#crNombre').value, apellido: $('#crApellido').value, correo: $('#crCorreo').value, rol: $('#crRol').value, institucion: $('#crInst').value, grupos: gruposCrear.ids() }
    });
    if (!ok) return mostrarError(datos);
    bootstrap.Modal.getOrCreateInstance(modalCrearEl).hide();
    showFlash(`Se creó la cuenta de ${datos.nombre_completo}. Queda pendiente de aprobación.`);
    e.target.reset();
    cargar();
  });

  // Importar usuarios desde CSV o JSON
  const archivoImportar = $('input[type="file"]', modalImportar);
  const zona = $('.dropzone', modalImportar);
  const textoZona = $('p', zona);
  archivoImportar.addEventListener('change', () => {
    textoZona.textContent = archivoImportar.files[0]?.name || 'Arrastra aquí tu archivo .csv o .json';
  });
  zona.addEventListener('dragover', e => e.preventDefault());
  zona.addEventListener('drop', e => {
    e.preventDefault();
    archivoImportar.files = e.dataTransfer.files;
    archivoImportar.dispatchEvent(new Event('change'));
  });
  botonImportar.addEventListener('click', async () => {
    const archivo = archivoImportar.files[0];
    if (!archivo) {
      showToast('Selecciona un archivo .csv o .json.');
      return;
    }
    const formulario = new FormData();
    formulario.append('archivo', archivo);
    formulario.append('rol', $('#impRol').value);
    formulario.append('institucion', $('#impInst').value);
    showToast('Archivo recibido. Las cuentas se crearán al procesarlo.');
    const { ok, datos } = await api('/api/usuarios/importar', { metodo: 'POST', formulario });
    archivoImportar.value = '';
    archivoImportar.dispatchEvent(new Event('change'));
    if (!ok) return mostrarError(datos);
    let mensaje = `Se ${datos.creados === 1 ? 'creó' : 'crearon'} ${plural(datos.creados, 'cuenta', 'cuentas')} pendientes de aprobación.`;
    if (datos.omitidos.length) mensaje += ` Omitidas: ${datos.omitidos.join('; ')}.`;
    showFlash(mensaje, datos.creados ? 'success' : 'warning');
    cargar();
  });

  // Botón "Revisar" del aviso de docentes pendientes
  $('[data-filter-shortcut]').addEventListener('click', e => {
    const select = $('#estadoUsr');
    select.value = e.currentTarget.dataset.filterShortcut;
    select.dispatchEvent(new Event('input', { bubbles: true }));
  });

  // Instituciones reales en los selectores
  api('/api/instituciones').then(({ ok, datos }) => {
    if (!ok) return;
    instituciones = datos;
    const nombres = datos.map(i => i.nombre).sort((a, b) => a.localeCompare(b));
    llenarSelect($('#instUsr'), [...nombres, 'Todas'], true);
    llenarSelect($('#edInst'), [...nombres, 'Todas']);
    llenarSelect($('#crInst'), nombres);
    llenarSelect($('#impInst'), nombres);
    // Si "Crear usuario" ya estaba abierto (usuarios.html?crear=1), carga sus grupos ahora
    if (modalCrearEl.classList.contains('show')) gruposCrear.abrir(null, []);
  });

  if (params.get('crear') === '1') bootstrap.Modal.getOrCreateInstance(modalCrearEl).show();
  cargar().then(() => {
    if (params.get('estado') === 'Pendiente') $('[data-filter-shortcut]').click();
  });
}

/* ---------- Historial ---------- */
async function iniciarHistorial() {
  const tbody = $('#tablaHistorial tbody');
  tbody.replaceChildren();
  // Filtros de fecha: por defecto, todo el año en curso
  const hoy = new Date();
  $('#desde').dataset.filter = 'desde';
  $('#hasta').dataset.filter = 'hasta';
  $('#desde').value = `${hoy.getFullYear()}-01-01`;
  $('#hasta').value = fechaISO(hoy);

  const { ok, datos } = await api('/api/historial');
  if (!ok) return mostrarError(datos);
  datos.forEach(h => {
    const tr = el('tr');
    Object.assign(tr.dataset, { estado: h.tipo, dia: h.dia });
    const tdEstado = el('td');
    tdEstado.appendChild(statusSpan(h.tipo));
    tr.append(el('td', 'text-nowrap', h.fecha), el('td', 'cell-title', h.actividad), el('td', '', h.cambio), tdEstado, el('td', 'text-nowrap', h.hecho_por));
    tbody.appendChild(tr);
  });
  aplicarFiltros('#tablaHistorial');
}

/* ---------- Monitoreo técnico ---------- */
function iniciarMonitoreo() {
  const cardInformes = $('.report-item').closest('.card');
  const cardEventos = $('.event-item').closest('.card');
  $('.topbar [data-toast]').addEventListener('click', async () => {
    const { ok, datos } = await api('/api/informes', { metodo: 'POST' });
    if (!ok) return mostrarError(datos);
    cargarMonitoreo(cardInformes, cardEventos);
  });
  cargarMonitoreo(cardInformes, cardEventos);

  const versiones = $('#versiones');
  versiones.addEventListener('shown.bs.collapse', () => { $('#btnVersiones').textContent = 'Ocultar'; });
  versiones.addEventListener('hidden.bs.collapse', () => { $('#btnVersiones').textContent = 'Ver versiones'; });
}

async function cargarMonitoreo(cardInformes, cardEventos) {
  const { ok, datos } = await api('/api/monitoreo');
  if (!ok) return mostrarError(datos);

  const actualizado = $('.topbar-actions span.small');
  if (actualizado) actualizado.lastChild.textContent = `Actualizado a las ${datos.actualizado}`;

  // Estado de los servicios del backend de la app
  const ESTADOS = {
    true: ['text-success', 'bg-success', 'Operativo'],
    false: ['text-danger', 'bg-danger', 'Sin respuesta'],
    null: ['text-secondary', 'bg-secondary', 'Sin configurar']
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
  $$('.report-item', cardInformes).forEach(n => n.remove());
  const pie = $('.card-footer', cardInformes);
  datos.informes.forEach(inf => {
    const item = el('div', 'report-item');
    const vista = el('span', 'thumb-sm');
    vista.appendChild(icono(inf.formato === 'PDF' ? 'bi-filetype-pdf' : 'bi-filetype-csv'));
    const info = el('div', 'flex-grow-1');
    info.append(el('div', 'fw-semibold', inf.titulo), el('div', 'cell-sub', `${inf.formato} · ${inf.tamano}`));
    const descargar = el('a', 'btn btn-sm btn-light');
    descargar.href = `/api/informes/${inf.id}/descargar`;
    descargar.setAttribute('aria-label', 'Descargar');
    descargar.appendChild(icono('bi-download'));
    item.append(vista, info, descargar);
    pie.before(item);
  });
  pie.textContent = `Son ${datos.equipos} equipos con datos sincronizados.`;

  // Versiones de la app en uso
  const filas = datos.versiones.map(v => {
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
    filas.push(el('div', 'alert alert-warning small mt-3 mb-0',
      `${datos.desactualizados.equipos} equipos con versión desactualizada no reciben actividades nuevas.`));
  }
  $('#versiones .card-body').replaceChildren(...filas);

  // Registro de eventos
  $$('.event-item', cardEventos).forEach(n => n.remove());
  datos.eventos.forEach(ev => {
    const item = el('div', 'event-item');
    item.append(statusSpan(ev.nivel), el('span', '', ev.mensaje), el('span', 'event-time', ev.fecha));
    cardEventos.appendChild(item);
  });
  if (!datos.eventos.length) cardEventos.appendChild(el('div', 'event-item text-secondary', 'Sin eventos registrados.'));
}

/* ---------- Arranque según la página ---------- */
const INICIALIZADORES = {
  'index.html': iniciarLogin,
  'crear-usuario.html': iniciarRegistro,
  'inicio.html': iniciarInicio,
  'actividades.html': iniciarActividades,
  'borradores.html': iniciarBorradores,
  'actividad-detalle.html': iniciarDetalle,
  'constructor.html': iniciarConstructor,
  'recursos.html': iniciarRecursos,
  'instituciones.html': iniciarInstituciones,
  'institucion-nueva.html': iniciarInstitucionNueva,
  'usuarios.html': iniciarUsuarios,
  'historial.html': iniciarHistorial,
  'monitoreo.html': iniciarMonitoreo
};
INICIALIZADORES[PAGINA]?.();

/* ---------- Avisos de demostración ---------- */
// Van al final: algunas páginas cambian sus avisos por el resultado real de la acción.
$$('[data-demo]').forEach(link => link.addEventListener('click', e => {
  e.preventDefault();
  showToast(link.dataset.demo);
}));

$$('[data-toast]').forEach(btn => btn.addEventListener('click', () => showToast(btn.dataset.toast)));

/* =========================================================
   Numi · Panel docente
   Interacciones del panel y conexión con el servidor Flask (API en /api/...)
   ========================================================= */

const MATERIAS = ['Matemáticas', 'Español', 'Ciencias', 'Sociales', 'Inglés'];
const CLAVES_MATERIA = ['matematicas', 'español', 'ciencias', 'sociales', 'ingles'];
const BAR_CLASS = ['bar-mat', 'bar-esp', 'bar-cie', 'bar-soc', 'bar-ing'];

const ESTADO_CLASS = { 'Al día': 'status-success', 'Sin sincronizar': 'status-info', 'Inactivo': 'status-danger', 'Activa': 'status-success', 'Inactiva': 'status-muted' };

const PAGINA = window.location.pathname.split('/').pop() || 'index.html';
const params = new URLSearchParams(window.location.search);
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));

/* ---------- Datos que llegan del servidor ---------- */
const estado = {
  yo: null,          // perfil del docente (/api/me)
  grupos: {},        // grupos a cargo, por id
  activo: null,      // id del grupo activo (lo guarda la sesión en el servidor)
  estudiantes: null  // lista del grupo activo (se pide una vez y se filtra aquí)
};

const grupo = () => estado.grupos[estado.activo];

/* ---------- Utilidades ---------- */
function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function iniciales(nombre) {
  return nombre.split(' ').filter(Boolean).slice(0, 2).map(p => p[0]).join('').toUpperCase();
}

function showToast(message) {
  let area = $('#toastArea');
  if (!area) {
    area = el('div', 'toast-container position-fixed bottom-0 end-0 p-3');
    area.id = 'toastArea';
    document.body.appendChild(area);
  }
  const toast = el('div', 'toast align-items-center text-bg-dark border-0');
  toast.setAttribute('role', 'status');
  toast.innerHTML = '<div class="d-flex"><div class="toast-body"></div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Cerrar"></button></div>';
  $('.toast-body', toast).textContent = message;
  area.appendChild(toast);
  new bootstrap.Toast(toast, { delay: 3500 }).show();
  toast.addEventListener('hidden.bs.toast', () => toast.remove());
}

function statusBadge(estadoTexto) {
  return el('span', `status ${ESTADO_CLASS[estadoTexto] || 'status-muted'}`, estadoTexto);
}

function mostrarError(datos) {
  showToast(datos.error || 'Ocurrió un error inesperado.');
}

/* ---------- Comunicación con el servidor (Flask) ---------- */
// Devuelve { ok, status, datos }. Si la sesión terminó (401) vuelve al login.
async function api(url, { metodo = 'GET', cuerpo } = {}) {
  const opciones = { method: metodo, headers: {} };
  if (cuerpo !== undefined) {
    opciones.headers['Content-Type'] = 'application/json';
    opciones.body = JSON.stringify(cuerpo);
  }
  try {
    const resp = await fetch(url, opciones);
    const datos = await resp.json().catch(() => ({}));
    if (resp.status === 401 && PAGINA !== 'index.html') window.location.href = 'index.html';
    return { ok: resp.ok, status: resp.status, datos };
  } catch {
    return { ok: false, status: 0, datos: { error: 'No hay conexión con el servidor. Abre el panel desde Flask (python app.py).' } };
  }
}

// Descarga un archivo (Excel o PDF). Si el servidor responde con un error, lo muestra.
async function descargarArchivo(url) {
  try {
    const resp = await fetch(url);
    if (!resp.ok) {
      mostrarError(await resp.json().catch(() => ({})));
      return;
    }
    const nombre = /filename="?([^";]+)"?/.exec(resp.headers.get('Content-Disposition') || '')?.[1] || 'numi';
    const enlace = el('a');
    enlace.href = URL.createObjectURL(await resp.blob());
    enlace.download = nombre;
    document.body.appendChild(enlace);
    enlace.click();
    enlace.remove();
    setTimeout(() => URL.revokeObjectURL(enlace.href), 1000);
  } catch {
    showToast('No hay conexión con el servidor.');
  }
}

/* ---------- Inicio de sesión ---------- */
function iniciarLogin() {
  const loginForm = $('#loginForm');
  loginForm.addEventListener('submit', async e => {
    e.preventDefault();
    $('#loginError')?.remove();
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
      window.location.href = 'panel.html';
      return;
    }
    const aviso = el('div', 'alert alert-danger d-flex align-items-center gap-2');
    aviso.id = 'loginError';
    aviso.setAttribute('role', 'alert');
    aviso.append(el('i', 'bi bi-shield-lock'), el('span', '', datos.error || 'No se pudo iniciar sesión.'));
    loginForm.before(aviso);
    boton.disabled = false;
  });
  $('#togglePassword').addEventListener('click', e => {
    const input = $('#password');
    const visible = input.type === 'text';
    input.type = visible ? 'password' : 'text';
    e.currentTarget.innerHTML = visible ? '<i class="bi bi-eye"></i>' : '<i class="bi bi-eye-slash"></i>';
  });
  const olvide = $$('a[href="#"]').find(a => a.textContent.includes('Olvidé'));
  olvide?.addEventListener('click', e => {
    e.preventDefault();
    showToast('Pide a la coordinación de tu sede que active de nuevo tu cuenta: recibirás una contraseña temporal.');
  });
}

/* ---------- Modales compartidos: perfil y cambio de grupo ---------- */
function crearModalesCompartidos() {
  if (!$('.group-bar')) return;

  document.body.insertAdjacentHTML('beforeend', `
    <div class="modal fade" id="modalPerfil" tabindex="-1" aria-labelledby="perfilTitulo" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered modal-sm">
        <div class="modal-content">
          <div class="modal-body p-4 text-center">
            <button type="button" class="btn-close position-absolute top-0 end-0 m-3" data-bs-dismiss="modal" aria-label="Cerrar"></button>
            <span class="avatar avatar-lg mx-auto mb-2" style="background: var(--numi-primary); color: #fff;" data-perfil="iniciales">LM</span>
            <h2 class="h6 fw-bold mb-0" id="perfilTitulo" data-perfil="nombre_completo">Prof. Luisa Muñoz</h2>
            <p class="small text-secondary mb-1" data-perfil="correo">luisa.munoz@ielaaldea.edu.co</p>
            <p class="small text-secondary" data-perfil="ubicacion">Sede principal · San Cristóbal</p>
            <div class="text-start border rounded-4 p-3 mb-3" style="background: var(--numi-primary-soft)">
              <div class="small fw-bold text-uppercase text-secondary mb-1" style="font-size: .7rem; letter-spacing: .08em">Grupo activo</div>
              <div class="fw-bold" data-group="nombre"></div>
              <div class="small text-secondary"><span data-group="estudiantes"></span> estudiantes · código <span data-group="codigo"></span></div>
            </div>
            <a href="mis-datos.html" class="d-flex justify-content-between align-items-center text-start border rounded-4 p-3 mb-2 text-decoration-none text-body">
              <span><span class="fw-bold d-block">Mis datos</span><span class="small text-secondary">Nombre, correo institucional y documento.</span></span>
              <i class="bi bi-chevron-double-right text-primary"></i>
            </a>
            <div class="text-start border rounded-4 p-3 mb-3">
              <span class="fw-bold d-block">Institución</span><span class="small text-secondary" data-perfil="institucion_lectura">IE La Aldea · solo lectura.</span>
            </div>
            <a href="index.html" class="btn btn-outline-danger w-100"><i class="bi bi-box-arrow-left me-1"></i> Cerrar sesión</a>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="modalGrupo" tabindex="-1" aria-labelledby="grupoTitulo" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <div>
              <h2 class="modal-title fs-5" id="grupoTitulo">Cambiar de grupo</h2>
              <p class="small text-secondary mb-0">El panel, los estudiantes, las actividades y los reportes pasan al grupo que elijas.</p>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
          </div>
          <div class="modal-body" id="listaGrupos"></div>
          <div class="modal-footer justify-content-start small text-secondary">
            <i class="bi bi-question-circle"></i> ¿Falta un grupo? La coordinación de la sede lo habilita con el código de la institución.
          </div>
        </div>
      </div>
    </div>`);

  $('#modalGrupo').addEventListener('show.bs.modal', renderListaGrupos);
}

function renderListaGrupos() {
  const lista = $('#listaGrupos');
  lista.replaceChildren();

  Object.values(estado.grupos).forEach(g => {
    const actual = g.id === estado.activo;
    const row = el('div', `group-option${actual ? ' is-current' : ''}`);
    const info = el('div', 'flex-grow-1');
    info.append(el('div', 'fw-bold', g.nombre), el('div', 'small text-secondary', `${g.estudiantes} estudiantes · avance ${g.avance}% · ${g.activos} activos · código ${g.codigo}`));
    row.append(el('span', 'group-badge', g.grado), info);

    if (actual) {
      row.append(el('span', 'status status-success', 'Grupo actual'));
    } else {
      const btn = el('button', 'btn btn-primary btn-sm', 'Entrar');
      btn.type = 'button';
      btn.addEventListener('click', async () => {
        const { ok, datos } = await api('/api/grupo-activo', { metodo: 'POST', cuerpo: { grupo_id: g.id } });
        if (!ok) return mostrarError(datos);
        estado.activo = g.id;
        estado.estudiantes = null;
        bootstrap.Modal.getInstance($('#modalGrupo')).hide();
        renderTodo();
        showToast(`Ahora ves ${g.nombre}.`);
      });
      row.append(btn);
    }
    lista.appendChild(row);
  });
}

/* ---------- Perfil del docente y encabezado del grupo ---------- */
function renderPerfil() {
  const yo = estado.yo;
  const valores = {
    iniciales: yo.iniciales,
    nombre_completo: yo.nombre_completo,
    correo: yo.correo,
    ubicacion: `${yo.sede} · ${yo.comuna}`,
    institucion_lectura: `${yo.institucion} · solo lectura.`
  };
  $$('[data-perfil]').forEach(node => { node.textContent = valores[node.dataset.perfil]; });

  const tarjeta = $('.teacher-card');
  if (tarjeta) {
    $('.avatar', tarjeta).textContent = yo.iniciales;
    $('.d-block.fw-bold', tarjeta).textContent = yo.nombre_completo;
    $('.small.text-secondary', tarjeta).lastChild.textContent = ` · ${yo.institucion}`;
  }
}

function renderGrupo() {
  const g = grupo();
  $$('[data-group]').forEach(node => {
    const value = g[node.dataset.group];
    if (value !== undefined) node.textContent = value;
  });
}

/* ---------- Panel ---------- */
async function renderPanel() {
  if (!$('#statActivos')) return;
  const { ok, datos } = await api('/api/panel');
  if (!ok) return mostrarError(datos);
  $('#statActivos').textContent = datos.activos;
  $('#statSinConexion').textContent = datos.sin_conexion;
  $('#statRacha').textContent = datos.racha;
  $('#statAvance').textContent = `${datos.avance}%`;
  const ring = $('#ringAvance');
  ring.style.setProperty('--value', datos.avance);
  $('span', ring).textContent = `${datos.avance}%`;

  $$('#materias .subject-row').forEach((row, i) => {
    $('[data-val]', row).textContent = `${datos.materias[i]}%`;
    $('.progress-bar', row).style.width = `${datos.materias[i]}%`;
  });

  const atencion = $('#atencion');
  atencion.replaceChildren();
  datos.atencion.forEach(([nombre, detalle, tipo, etiqueta]) => {
    const item = el('div', 'attention-item');
    const info = el('div', 'flex-grow-1');
    info.append(el('div', 'fw-bold', nombre), el('div', 'cell-sub', detalle));
    item.append(el('span', 'avatar', iniciales(nombre)), info, el('span', `status status-${tipo}`, etiqueta));
    atencion.appendChild(item);
  });
  if (!datos.atencion.length) atencion.appendChild(el('div', 'attention-item text-secondary', 'Nadie requiere atención por ahora.'));
}

/* ---------- Estudiantes ---------- */
async function renderEstudiantes() {
  const tbody = $('#tablaEstudiantes');
  if (!tbody) return;
  if (!estado.estudiantes) {
    tbody.replaceChildren();
    const { ok, datos } = await api('/api/estudiantes');
    if (!ok) return mostrarError(datos);
    estado.estudiantes = datos;
  }
  const alumnos = estado.estudiantes;
  const q = $('#buscarEst').value.trim().toLowerCase();
  const materia = $('#materiaEst').value;
  const estadoFiltro = $('#estadoEst').value;

  $('#colAvance').textContent = materia === '' ? 'Avance' : `Avance · ${MATERIAS[materia]}`;
  tbody.replaceChildren();

  const visibles = alumnos.filter(a => a.nombre.toLowerCase().includes(q) && (!estadoFiltro || a.estado === estadoFiltro));
  visibles.forEach(alumno => {
    const valor = materia === '' ? alumno.avance : alumno.materias[materia];
    const tr = el('tr');

    const tdNombre = el('td');
    const wrap = el('div', 'd-flex align-items-center gap-2');
    wrap.append(el('span', 'avatar', iniciales(alumno.nombre)), el('span', 'cell-title', alumno.nombre));
    tdNombre.appendChild(wrap);

    const tdAvance = el('td');
    const barWrap = el('div', 'd-flex align-items-center gap-2');
    const prog = el('div', 'progress mini-progress flex-grow-1');
    const bar = el('div', 'progress-bar');
    bar.style.width = `${valor}%`;
    prog.appendChild(bar);
    barWrap.append(prog, el('span', 'small fw-bold', `${valor}%`));
    tdAvance.appendChild(barWrap);

    const tdRacha = el('td', 'text-nowrap');
    tdRacha.innerHTML = '<i class="bi bi-fire text-warning me-1"></i>';
    tdRacha.append(alumno.racha);

    const tdEstado = el('td');
    tdEstado.appendChild(statusBadge(alumno.estado));

    const tdBtn = el('td', 'text-end');
    const btn = el('button', 'btn btn-sm btn-soft text-nowrap', 'Ver estudiante');
    btn.type = 'button';
    btn.addEventListener('click', () => abrirFicha(alumno));
    tdBtn.appendChild(btn);

    tr.append(tdNombre, tdAvance, tdRacha, tdEstado, tdBtn);
    tbody.appendChild(tr);
  });

  if (!visibles.length) {
    const tr = el('tr');
    const td = el('td', 'text-center text-secondary py-4', alumnos.length ? 'No hay estudiantes con esos filtros.' : 'Todavía no hay estudiantes en este grupo. Comparte el código desde Gestión.');
    td.colSpan = 5;
    tr.appendChild(td);
    tbody.appendChild(tr);
  }
  $('#contadorEstudiantes').textContent = `${visibles.length} de ${alumnos.length} estudiantes`;
}

let fichaActual = null;
let temporizadorNota = null;

async function abrirFicha(alumno) {
  const { ok, datos: ficha } = await api(`/api/estudiantes/${alumno.id}`);
  if (!ok) return mostrarError(ficha);
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
    const row = el('div', 'subject-row');
    const head = el('div', 'd-flex justify-content-between small fw-bold mb-1');
    head.append(el('span', '', MATERIAS[i]), el('span', '', `${valor}%`));
    const prog = el('div', 'progress');
    const bar = el('div', `progress-bar ${BAR_CLASS[i]}`);
    bar.style.width = `${valor}%`;
    prog.appendChild(bar);
    row.append(head, prog);
    materias.appendChild(row);
  });

  const lista = (id, items, vacio) => {
    const ul = $(id);
    ul.replaceChildren();
    items.forEach(([nombre, valor]) => {
      const li = el('li', 'list-group-item d-flex justify-content-between align-items-center px-0');
      const cls = valor === 'Completada' ? 'status status-success' : valor === 'Sin empezar' ? 'status status-muted' : 'small fw-bold';
      li.append(el('span', '', nombre), el('span', cls, valor));
      ul.appendChild(li);
    });
    if (!items.length) ul.appendChild(el('li', 'list-group-item px-0 text-secondary small', vacio));
  };
  lista('#fichaActividades', ficha.actividades, 'No hay actividades activas para el grupo.');
  lista('#fichaEvaluacion', ficha.evaluacion, 'Todavía no ha respondido el banco de preguntas.');

  bootstrap.Modal.getOrCreateInstance('#modalFicha').show();
}

// La nota del docente se guarda sola mientras escribe (no hay botón Guardar)
async function guardarNota() {
  clearTimeout(temporizadorNota);
  if (!fichaActual) return;
  const nota = $('#fichaNota').value;
  if (nota.trim() === fichaActual.nota.trim()) return;
  const { ok, datos } = await api(`/api/estudiantes/${fichaActual.id}/nota`, { metodo: 'PUT', cuerpo: { nota } });
  if (!ok) return mostrarError(datos);
  fichaActual.nota = datos.nota;
  showToast('Nota guardada.');
}

function iniciarEstudiantes() {
  $('#filtrosEstudiantes').addEventListener('submit', e => e.preventDefault());
  $$('#filtrosEstudiantes input, #filtrosEstudiantes select').forEach(c => c.addEventListener('input', renderEstudiantes));
  $('.section-actions [data-toast]').addEventListener('click', () => descargarArchivo('/api/estudiantes/exportar'));
  $('#modalFicha .modal-footer [data-toast]').addEventListener('click', () => {
    if (fichaActual) descargarArchivo(`/api/estudiantes/${fichaActual.id}/informe`);
  });
  $('#fichaNota').addEventListener('input', () => {
    clearTimeout(temporizadorNota);
    temporizadorNota = setTimeout(guardarNota, 1000);
  });
  $('#fichaNota').addEventListener('blur', guardarNota);
  $('#modalFicha').addEventListener('hide.bs.modal', guardarNota);
}

/* ---------- Actividades ---------- */
let actividades = [];

function filtrarActividades() {
  const tabla = $('#tablaActividades');
  const q = $('#buscarAct').value.trim().toLowerCase();
  const materia = $('#materiaAct').value;
  const estadoFiltro = $('#estadoAct').value;
  let visibles = 0;
  $$('tbody tr', tabla).forEach(tr => {
    const activa = $('input[role="switch"]', tr).checked ? 'Activa' : 'Inactiva';
    const ok = tr.textContent.toLowerCase().includes(q)
      && (!materia || tr.dataset.materia === materia)
      && (!estadoFiltro || activa === estadoFiltro);
    tr.classList.toggle('d-none', !ok);
    if (ok) visibles++;
  });
  $('#contadorActividades').textContent = visibles;
}

function filaActividad(act) {
  const tr = el('tr');
  Object.assign(tr.dataset, { act: act.id, materia: act.materia });

  const tdNombre = el('td');
  const wrap = el('div', 'd-flex align-items-center gap-3');
  const textos = el('div');
  const titulo = el('div', 'cell-title', act.nombre);
  if (act.mas_errores) titulo.append(' ', el('span', 'badge text-bg-danger-subtle text-danger-emphasis ms-1', 'Más errores'));
  textos.append(titulo, el('div', 'cell-sub', act.descripcion.replace(/\.$/, '')));
  wrap.append(el('span', `subject-icon ${BAR_CLASS[act.materia_indice]}`, act.materia[0]), textos);
  tdNombre.appendChild(wrap);

  const tdEstado = el('td');
  tdEstado.dataset.estado = '';
  tdEstado.appendChild(statusBadge(act.activa ? 'Activa' : 'Inactiva'));

  const tdDetalle = el('td');
  const ver = el('button', 'btn btn-sm btn-soft text-nowrap', 'Ver detalle ');
  ver.type = 'button';
  ver.dataset.verActividad = '';
  ver.appendChild(el('i', 'bi bi-chevron-right'));
  tdDetalle.appendChild(ver);

  const tdSwitch = el('td', 'text-end');
  const caja = el('div', 'form-check form-switch d-inline-flex justify-content-end gap-2 mb-0');
  const sw = el('input', 'form-check-input');
  sw.type = 'checkbox';
  sw.setAttribute('role', 'switch');
  sw.setAttribute('aria-label', 'Activa para el grupo');
  sw.checked = act.activa;
  caja.append(sw, el('span', 'small text-nowrap d-none d-md-inline', 'Activa para el grupo'));
  tdSwitch.appendChild(caja);
  tr.append(tdNombre, el('td', '', act.materia), tdEstado, tdDetalle, tdSwitch);

  sw.addEventListener('change', async () => {
    sw.disabled = true;
    const { ok, datos } = await api(`/api/actividades/${encodeURIComponent(act.id)}`, { metodo: 'PATCH', cuerpo: { activa: sw.checked } });
    sw.disabled = false;
    if (!ok) {
      sw.checked = !sw.checked;
      return mostrarError(datos);
    }
    act.activa = sw.checked;
    tdEstado.replaceChildren(statusBadge(act.activa ? 'Activa' : 'Inactiva'));
    showToast(act.activa ? `«${act.nombre}» quedó activa para ${grupo().nombre}.` : `«${act.nombre}» ya no aparece en los celulares de ${grupo().nombre}.`);
    filtrarActividades();
  });

  ver.addEventListener('click', () => {
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
      const cls = valor === 'Completada' ? 'status status-success' : valor === 'Sin empezar' ? 'status status-muted' : 'small fw-bold';
      li.append(el('span', '', nombre), el('span', cls, valor));
      ul.appendChild(li);
    });

    bootstrap.Modal.getOrCreateInstance('#modalActividad').show();
  });
  return tr;
}

async function renderActividades() {
  const tabla = $('#tablaActividades');
  if (!tabla) return;
  const tbody = $('tbody', tabla);
  tbody.replaceChildren();
  const { ok, datos } = await api('/api/actividades');
  if (!ok) return mostrarError(datos);
  actividades = datos;
  tbody.append(...actividades.map(filaActividad));
  filtrarActividades();
}

function iniciarActividades() {
  $('#filtrosActividades').addEventListener('submit', e => e.preventDefault());
  $$('#filtrosActividades input, #filtrosActividades select').forEach(c => c.addEventListener('input', filtrarActividades));
}

/* ---------- Reportes ---------- */
let periodoActual = null;

async function renderReportes() {
  const grafico = $('#graficoMaterias');
  if (!grafico) return;
  const { ok, datos } = await api(`/api/reportes?periodo=${encodeURIComponent($('#periodo').value)}`);
  if (!ok) return mostrarError(datos);
  periodoActual = datos.periodo;

  $('#repPromedio').textContent = `${datos.promedio}%`;
  $('#repMinimo').textContent = `${datos.minimo}%`;
  $('#repMinimoNombre').textContent = datos.minimo_nombre;
  $$('[data-periodo-nombre]').forEach(n => { n.textContent = datos.periodo.nombre; });

  grafico.replaceChildren();
  datos.materias.forEach((valor, i) => {
    const col = el('div', 'bar-col');
    const bar = el('div', `bar ${BAR_CLASS[i]}`);
    bar.style.height = `${valor * 1.6}px`;
    col.append(el('span', 'bar-value', `${valor}%`), bar, el('span', 'bar-label', MATERIAS[i]));
    grafico.appendChild(col);
  });

  const tbody = $('#tablaReporte');
  tbody.replaceChildren();
  datos.estudiantes.forEach(([nombre, valor]) => {
    const tr = el('tr');
    const td1 = el('td');
    const wrap = el('div', 'd-flex align-items-center gap-2');
    wrap.append(el('span', 'avatar', iniciales(nombre)), el('span', 'cell-title', nombre));
    td1.appendChild(wrap);
    const td2 = el('td', 'text-end fw-bold', `${valor}%`);
    tr.append(td1, td2);
    tbody.appendChild(tr);
  });
}

function iniciarReportes() {
  const modal = $('#modalGenerar');
  const [botonExcel, botonPdf] = [$('.modal-footer .btn-outline-primary', modal), $('.modal-footer .btn-primary', modal)];
  // El aviso "Descargando…" solo se muestra si el reporte se puede generar
  const avisos = { xlsx: botonExcel.dataset.toast, pdf: botonPdf.dataset.toast };
  delete botonExcel.dataset.toast;
  delete botonPdf.dataset.toast;

  const fechasDelPeriodo = async () => {
    if (!periodoActual || periodoActual.clave !== $('#genPeriodo').value) {
      const { ok, datos } = await api(`/api/reportes?periodo=${encodeURIComponent($('#genPeriodo').value)}`);
      if (!ok) return;
      periodoActual = datos.periodo;
    }
    $('#genDesde').value = periodoActual.desde;
    $('#genHasta').value = periodoActual.hasta;
  };

  $('#periodo').addEventListener('change', renderReportes);
  modal.addEventListener('show.bs.modal', () => {
    $('#genPeriodo').value = $('#periodo').value;
    fechasDelPeriodo();
  });
  $('#genPeriodo').addEventListener('change', fechasDelPeriodo);

  const generar = formato => {
    const materias = ['#mMat', '#mEsp', '#mCie', '#mSoc', '#mIng'].map((id, i) => ($(id).checked ? CLAVES_MATERIA[i] : null)).filter(Boolean);
    const incluir = [['#iAvance', 'avance'], ['#iDetalle', 'detalle'], ['#iEval', 'evaluacion'], ['#iNotas', 'notas'], ['#iRacha', 'racha']]
      .filter(([id]) => $(id).checked).map(([, clave]) => clave);
    if (!materias.length) return showToast('Elige al menos una materia.');
    if (!incluir.length) return showToast('Elige al menos un contenido para incluir en el archivo.');
    const consulta = new URLSearchParams({
      formato,
      periodo: $('#genPeriodo').value,
      desde: $('#genDesde').value,
      hasta: $('#genHasta').value,
      estado: $('#genEstado').selectedIndex > 0 ? $('#genEstado').value : '',
      materias: materias.join(','),
      incluir: incluir.join(',')
    });
    showToast(avisos[formato]);
    descargarArchivo(`/api/reportes/descargar?${consulta}`);
  };
  botonExcel.addEventListener('click', () => generar('xlsx'));
  botonPdf.addEventListener('click', () => generar('pdf'));

  if (params.get('generar') === '1') bootstrap.Modal.getOrCreateInstance(modal).show();
}

/* ---------- Gestión del grupo ---------- */
function pintarGestion(datos) {
  $('#codigoGrupo').textContent = datos.codigo;
  $('#usosCodigo').textContent = datos.usos;
  $('#usosCodigo').parentElement.firstChild.textContent = `${datos.vence} · `;
  $('#switchIA').checked = datos.ia;
  $('#switchIA').disabled = !datos.ia_disponible && !datos.ia;
  $('#labelIA').textContent = datos.ia ? 'Activado' : 'Desactivado';
  $('#paqueteInfo').textContent = datos.paquete;
  if (grupo()) grupo().codigo = datos.codigo;
}

async function renderGestion() {
  if (!$('#codigoGrupo')) return;
  const { ok, datos } = await api('/api/gestion');
  if (!ok) return mostrarError(datos);
  pintarGestion(datos);
}

function iniciarGestion() {
  $('#btnCopiar').addEventListener('click', () => {
    const codigo = $('#codigoGrupo').textContent;
    const done = () => showToast(`Código ${codigo} copiado.`);
    if (navigator.clipboard) navigator.clipboard.writeText(codigo).then(done, done);
    else done();
  });

  $('#btnNuevoCodigo').addEventListener('click', async () => {
    const { ok, datos } = await api('/api/gestion/codigo', { metodo: 'POST' });
    if (!ok) return mostrarError(datos);
    pintarGestion(datos);
    renderGrupo();
    showToast('Se generó un código nuevo. El anterior deja de funcionar.');
  });

  $('#switchIA').addEventListener('change', async e => {
    const activada = e.target.checked;
    const { ok, datos } = await api('/api/gestion/ia', { metodo: 'PATCH', cuerpo: { activada } });
    if (!ok) {
      e.target.checked = !activada;
      return mostrarError(datos);
    }
    pintarGestion(datos);
    showToast(activada ? 'Asistente de IA activado para el grupo.' : 'Asistente de IA desactivado para el grupo.');
  });

  $('#btnActualizar').addEventListener('click', async e => {
    const btn = e.currentTarget;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Actualizando';
    const { ok, datos } = await api('/api/gestion/paquete', { metodo: 'POST' });
    btn.disabled = false;
    btn.innerHTML = '<i class="bi bi-arrow-clockwise me-1"></i> Actualizar';
    if (!ok) return mostrarError(datos);
    pintarGestion(datos);
    showToast('El paquete de conocimiento ya está al día.');
  });
}

/* ---------- Mis datos ---------- */
function renderMisDatos() {
  const cont = $('#gruposACargo');
  if (!cont) return;
  const yo = estado.yo;
  const tarjeta = $('.col-lg-4 .card');
  $('.avatar', tarjeta).textContent = yo.iniciales;
  $('h3', tarjeta).textContent = yo.nombre_completo;
  $('p.text-secondary', tarjeta).textContent = yo.rol;
  $('p.small', tarjeta).lastChild.textContent = ` ${yo.correo}`;
  $('#dNombre').value = yo.nombre;
  $('#dApellido').value = yo.apellido;
  $('#dCorreo').value = yo.correo;
  $('#dDoc').value = yo.documento;
  const datosInstitucion = $$('dl.detail-list dd');
  [yo.institucion, yo.sede, yo.comuna, yo.rol].forEach((valor, i) => { if (datosInstitucion[i]) datosInstitucion[i].textContent = valor; });

  cont.replaceChildren();
  Object.values(estado.grupos).forEach(g => {
    const actual = g.id === estado.activo;
    const row = el('div', `group-option${actual ? ' is-current' : ''}`);
    const info = el('div', 'flex-grow-1');
    info.append(el('div', 'fw-bold', g.nombre), el('div', 'small text-secondary', `${g.estudiantes} estudiantes · código ${g.codigo}`));
    row.append(el('span', 'group-badge', g.grado), info);
    if (actual) row.append(el('span', 'status status-success', 'Grupo activo'));
    cont.appendChild(row);
  });
}

/* ---------- Arranque ---------- */
function renderTodo() {
  renderGrupo();
  renderPanel();
  renderEstudiantes();
  renderActividades();
  renderReportes();
  renderGestion();
  renderMisDatos();
}

async function iniciarPanel() {
  crearModalesCompartidos();
  if ($('#tablaEstudiantes')) iniciarEstudiantes();
  if ($('#tablaActividades')) iniciarActividades();
  if ($('#periodo')) iniciarReportes();
  if ($('#codigoGrupo')) iniciarGestion();

  const { ok, datos } = await api('/api/me');
  if (!ok) return mostrarError(datos);
  estado.yo = datos;
  estado.grupos = Object.fromEntries(datos.grupos.map(g => [g.id, g]));
  estado.activo = datos.grupo_activo;
  renderPerfil();
  if (!estado.activo) {
    showToast('No tienes grupos asignados. La coordinación de la sede los habilita.');
    return;
  }
  renderTodo();
}

if (PAGINA === 'index.html') iniciarLogin();
else iniciarPanel();

// Avisos de demostración (al final: algunas páginas los cambian por la acción real)
$$('[data-toast]').forEach(btn => btn.addEventListener('click', () => showToast(btn.dataset.toast)));

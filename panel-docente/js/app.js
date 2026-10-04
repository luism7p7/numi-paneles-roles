/* =========================================================
   Numi · Panel docente
   Datos de ejemplo e interacciones del prototipo
   ========================================================= */

const MATERIAS = ['Matemáticas', 'Español', 'Ciencias', 'Sociales', 'Inglés'];
const BAR_CLASS = ['bar-mat', 'bar-esp', 'bar-cie', 'bar-soc', 'bar-ing'];

const GRUPOS = {
  '3A': {
    grado: '3°', corto: '3° A', nombre: 'Grado 3° — grupo A', estudiantes: 24, codigo: '7K4M-92',
    avance: 61, activos: 18, sinConexion: 6, racha: '4 d',
    materias: [72, 68, 59, 54, 41],
    atencion: [['Samuel Ríos', '12 días sin entrar', 'danger', 'Inactivo'], ['Mariana Ospina', 'Inglés en 18%', 'warning', 'Bajo avance'], ['Kevin Zapata', 'Sin sincronizar', 'info', 'Sincronizar']],
    reporte: { materias: [64, 60, 52, 48, 37], estudiantes: [['Valentina Cano', 74], ['Mariana Ospina', 58], ['Juan David Mesa', 47], ['Samuel Ríos', 24]] },
    alumnos: [
      { nombre: 'Mariana Ospina',  avance: 64, racha: '6 d',  estado: 'Al día',          materias: [84, 79, 71, 66, 18], actividades: [['Los números', 'Completada'], ['Arma la palabra', '62%'], ['Escucha y elige', 'Sin empezar']], evaluacion: [['Banco MCQ · inglés', '3 de 10 correctas'], ['Banco MCQ · matemáticas', '8 de 10 correctas']] },
      { nombre: 'Samuel Ríos',     avance: 22, racha: '0 d',  estado: 'Inactivo',        materias: [32, 28, 19, 22, 11], actividades: [['Los números', '41%'], ['Arma la palabra', 'Sin empezar'], ['Las plantas', 'Sin empezar']], evaluacion: [['Banco MCQ · matemáticas', '2 de 10 correctas'], ['Banco MCQ · español', '3 de 10 correctas']] },
      { nombre: 'Kevin Zapata',    avance: 61, racha: '3 d',  estado: 'Sin sincronizar', materias: [68, 72, 64, 58, 44], actividades: [['Los números', 'Completada'], ['Cuerpo humano', '70%'], ['Parejas', 'Sin empezar']], evaluacion: [['Banco MCQ · ciencias', '6 de 10 correctas'], ['Banco MCQ · inglés', '4 de 10 correctas']] },
      { nombre: 'Valentina Cano',  avance: 84, racha: '11 d', estado: 'Al día',          materias: [91, 88, 85, 80, 76], actividades: [['Los números', 'Completada'], ['Arma la palabra', 'Completada'], ['Las plantas', '88%']], evaluacion: [['Banco MCQ · matemáticas', '10 de 10 correctas'], ['Banco MCQ · inglés', '8 de 10 correctas']] },
      { nombre: 'Juan David Mesa', avance: 51, racha: '2 d',  estado: 'Al día',          materias: [55, 61, 49, 52, 38], actividades: [['Los números', '74%'], ['Oraciones', '50%'], ['Parejas', 'Sin empezar']], evaluacion: [['Banco MCQ · español', '6 de 10 correctas'], ['Banco MCQ · sociales', '5 de 10 correctas']] },
      { nombre: 'Sofía Restrepo',  avance: 68, racha: '5 d',  estado: 'Al día',          materias: [77, 70, 73, 69, 51], actividades: [['Las plantas', 'Completada'], ['Arma la palabra', '68%'], ['Escucha y elige', '30%']], evaluacion: [['Banco MCQ · ciencias', '8 de 10 correctas'], ['Banco MCQ · inglés', '5 de 10 correctas']] }
    ]
  },
  '4B': {
    grado: '4°', corto: '4° B', nombre: 'Grado 4° — grupo B', estudiantes: 21, codigo: 'P8T2-46',
    avance: 67, activos: 16, sinConexion: 3, racha: '5 d',
    materias: [74, 71, 66, 63, 49],
    atencion: [['Andrés Quintero', '9 días sin entrar', 'danger', 'Inactivo'], ['Laura Betancur', 'Inglés en 24%', 'warning', 'Bajo avance'], ['Emanuel Duque', 'Sin sincronizar', 'info', 'Sincronizar']],
    reporte: { materias: [64, 59, 66, 56, 43], estudiantes: [['Camila Herrera', 79], ['Laura Betancur', 61], ['Tomás Álvarez', 52], ['Andrés Quintero', 35]] },
    alumnos: [
      { nombre: 'Laura Betancur',  avance: 61, racha: '4 d', estado: 'Al día',          materias: [70, 68, 72, 65, 24], actividades: [['Las plantas', 'Completada'], ['Oraciones', '66%'], ['Parejas', '20%']], evaluacion: [['Banco MCQ · inglés', '3 de 10 correctas'], ['Banco MCQ · ciencias', '8 de 10 correctas']] },
      { nombre: 'Andrés Quintero', avance: 35, racha: '0 d', estado: 'Inactivo',        materias: [40, 38, 36, 33, 28], actividades: [['Los números', '45%'], ['Oraciones', 'Sin empezar'], ['Cuerpo humano', 'Sin empezar']], evaluacion: [['Banco MCQ · matemáticas', '4 de 10 correctas'], ['Banco MCQ · español', '3 de 10 correctas']] },
      { nombre: 'Emanuel Duque',   avance: 58, racha: '2 d', estado: 'Sin sincronizar', materias: [62, 60, 58, 55, 45], actividades: [['Los números', 'Completada'], ['Cuerpo humano', '58%'], ['Parejas', '35%']], evaluacion: [['Banco MCQ · ciencias', '6 de 10 correctas'], ['Banco MCQ · inglés', '5 de 10 correctas']] },
      { nombre: 'Camila Herrera',  avance: 79, racha: '9 d', estado: 'Al día',          materias: [85, 82, 80, 76, 70], actividades: [['Los números', 'Completada'], ['Arma la palabra', 'Completada'], ['Las plantas', '90%']], evaluacion: [['Banco MCQ · matemáticas', '9 de 10 correctas'], ['Banco MCQ · inglés', '7 de 10 correctas']] },
      { nombre: 'Tomás Álvarez',   avance: 52, racha: '3 d', estado: 'Al día',          materias: [58, 55, 52, 50, 44], actividades: [['Los números', '70%'], ['Oraciones', '48%'], ['Las plantas', 'Sin empezar']], evaluacion: [['Banco MCQ · español', '5 de 10 correctas'], ['Banco MCQ · sociales', '6 de 10 correctas']] }
    ]
  },
  '5A': {
    grado: '5°', corto: '5° A', nombre: 'Grado 5° — grupo A', estudiantes: 19, codigo: 'R5Q7-13',
    avance: 58, activos: 13, sinConexion: 5, racha: '3 d',
    materias: [64, 62, 57, 55, 38],
    atencion: [['Brayan Muñoz', '15 días sin entrar', 'danger', 'Inactivo'], ['Isabela Torres', 'Inglés en 16%', 'warning', 'Bajo avance'], ['Sara Gómez', 'Sin sincronizar', 'info', 'Sincronizar']],
    reporte: { materias: [57, 56, 50, 49, 34], estudiantes: [['Mateo Arango', 72], ['Isabela Torres', 55], ['Daniela Ruiz', 48], ['Brayan Muñoz', 27]] },
    alumnos: [
      { nombre: 'Isabela Torres', avance: 55, racha: '4 d', estado: 'Al día',          materias: [66, 62, 60, 58, 16], actividades: [['Oraciones', 'Completada'], ['Las plantas', '60%'], ['Parejas', '15%']], evaluacion: [['Banco MCQ · inglés', '2 de 10 correctas'], ['Banco MCQ · español', '7 de 10 correctas']] },
      { nombre: 'Brayan Muñoz',   avance: 27, racha: '0 d', estado: 'Inactivo',        materias: [32, 30, 28, 25, 20], actividades: [['Los números', '30%'], ['Cuerpo humano', 'Sin empezar'], ['Parejas', 'Sin empezar']], evaluacion: [['Banco MCQ · matemáticas', '3 de 10 correctas'], ['Banco MCQ · ciencias', '2 de 10 correctas']] },
      { nombre: 'Sara Gómez',     avance: 50, racha: '2 d', estado: 'Sin sincronizar', materias: [55, 54, 50, 48, 40], actividades: [['Los números', 'Completada'], ['Arma la palabra', '52%'], ['Las plantas', 'Sin empezar']], evaluacion: [['Banco MCQ · matemáticas', '6 de 10 correctas'], ['Banco MCQ · sociales', '5 de 10 correctas']] },
      { nombre: 'Mateo Arango',   avance: 72, racha: '8 d', estado: 'Al día',          materias: [78, 75, 72, 70, 64], actividades: [['Los números', 'Completada'], ['Cuerpo humano', 'Completada'], ['Parejas', '70%']], evaluacion: [['Banco MCQ · ciencias', '9 de 10 correctas'], ['Banco MCQ · inglés', '7 de 10 correctas']] },
      { nombre: 'Daniela Ruiz',   avance: 48, racha: '3 d', estado: 'Al día',          materias: [52, 50, 49, 47, 40], actividades: [['Oraciones', '55%'], ['Las plantas', '45%'], ['Los números', '62%']], evaluacion: [['Banco MCQ · español', '5 de 10 correctas'], ['Banco MCQ · inglés', '4 de 10 correctas']] }
    ]
  }
};

const ACTIVIDADES = {
  'los-numeros':       { nombre: 'Los números',       materia: 'Matemáticas', descripcion: 'Reconocer del 1 al 20.',                         avance: 88 },
  'quien-tiene-mas':   { nombre: '¿Quién tiene más?', materia: 'Matemáticas', descripcion: 'Comparar cantidades. Es la actividad con más errores del grupo.', avance: 71 },
  'arma-la-palabra':   { nombre: 'Arma la palabra',   materia: 'Español',     descripcion: 'Ordenar sílabas para formar palabras.',          avance: 74 },
  'las-plantas':       { nombre: 'Las plantas',       materia: 'Ciencias',    descripcion: 'Partes y funciones de las plantas.',             avance: 66 },
  'parejas':           { nombre: 'Parejas',           materia: 'Inglés',      descripcion: 'Memory match en inglés.',                        avance: 39 },
  'cuerpo-humano':     { nombre: 'Cuerpo humano',     materia: 'Ciencias',    descripcion: 'Identificar las partes del cuerpo.',             avance: 58 },
  'oraciones':         { nombre: 'Oraciones',         materia: 'Español',     descripcion: 'Construir frases con sentido.',                  avance: 52 },
  'pasado-y-presente': { nombre: 'Pasado y presente', materia: 'Sociales',    descripcion: 'Historia de Medellín.',                          avance: 0 }
};

const PERIODOS = {
  p1:   { nombre: 'Periodo 1',  ajuste: 0 },
  p2:   { nombre: 'Periodo 2',  ajuste: 3 },
  s1:   { nombre: 'Semestre 1', ajuste: 4 },
  anio: { nombre: 'Año 2026',   ajuste: 6 }
};

const ESTADO_CLASS = { 'Al día': 'status-success', 'Sin sincronizar': 'status-info', 'Inactivo': 'status-danger', 'Activa': 'status-success', 'Inactiva': 'status-muted' };

const params = new URLSearchParams(window.location.search);
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));

/* ---------- Grupo activo (se recuerda entre páginas) ---------- */
let grupoMemoria = '3A';

function getGrupoKey() {
  try {
    const saved = localStorage.getItem('numi-grupo');
    if (saved && GRUPOS[saved]) return saved;
  } catch (e) { /* almacenamiento no disponible */ }
  return grupoMemoria;
}

function setGrupoKey(key) {
  grupoMemoria = key;
  try { localStorage.setItem('numi-grupo', key); } catch (e) { /* almacenamiento no disponible */ }
}

const grupo = () => GRUPOS[getGrupoKey()];

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
  const area = $('#toastArea');
  if (!area) return;
  const toast = el('div', 'toast align-items-center text-bg-dark border-0');
  toast.setAttribute('role', 'status');
  toast.innerHTML = '<div class="d-flex"><div class="toast-body"></div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Cerrar"></button></div>';
  $('.toast-body', toast).textContent = message;
  area.appendChild(toast);
  new bootstrap.Toast(toast, { delay: 3500 }).show();
  toast.addEventListener('hidden.bs.toast', () => toast.remove());
}

function statusBadge(estado) {
  return el('span', `status ${ESTADO_CLASS[estado] || 'status-muted'}`, estado);
}

$$('[data-toast]').forEach(btn => btn.addEventListener('click', () => showToast(btn.dataset.toast)));

/* ---------- Inicio de sesión ---------- */
const loginForm = $('#loginForm');
if (loginForm) {
  loginForm.addEventListener('submit', e => {
    e.preventDefault();
    if (!loginForm.checkValidity()) {
      loginForm.classList.add('was-validated');
      return;
    }
    window.location.href = 'panel.html';
  });
  $('#togglePassword').addEventListener('click', e => {
    const input = $('#password');
    const visible = input.type === 'text';
    input.type = visible ? 'password' : 'text';
    e.currentTarget.innerHTML = visible ? '<i class="bi bi-eye"></i>' : '<i class="bi bi-eye-slash"></i>';
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
            <span class="avatar avatar-lg mx-auto mb-2" style="background: var(--numi-primary); color: #fff;">LM</span>
            <h2 class="h6 fw-bold mb-0" id="perfilTitulo">Prof. Luisa Muñoz</h2>
            <p class="small text-secondary mb-1">luisa.munoz@ielaaldea.edu.co</p>
            <p class="small text-secondary">Sede principal · San Cristóbal</p>
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
              <span class="fw-bold d-block">Institución</span><span class="small text-secondary">IE La Aldea · solo lectura.</span>
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
  const actual = getGrupoKey();

  Object.entries(GRUPOS).forEach(([key, g]) => {
    const row = el('div', `group-option${key === actual ? ' is-current' : ''}`);
    const info = el('div', 'flex-grow-1');
    info.append(el('div', 'fw-bold', g.nombre), el('div', 'small text-secondary', `${g.estudiantes} estudiantes · avance ${g.avance}% · ${g.activos} activos · código ${g.codigo}`));
    row.append(el('span', 'group-badge', g.grado), info);

    if (key === actual) {
      row.append(el('span', 'status status-success', 'Grupo actual'));
    } else {
      const btn = el('button', 'btn btn-primary btn-sm', 'Entrar');
      btn.type = 'button';
      btn.addEventListener('click', () => {
        setGrupoKey(key);
        bootstrap.Modal.getInstance($('#modalGrupo')).hide();
        renderTodo();
        showToast(`Ahora ves ${g.nombre}.`);
      });
      row.append(btn);
    }
    lista.appendChild(row);
  });
}

/* ---------- Encabezado del grupo ---------- */
function renderGrupo() {
  const g = grupo();
  $$('[data-group]').forEach(node => {
    const value = g[node.dataset.group];
    if (value !== undefined) node.textContent = value;
  });
}

/* ---------- Panel ---------- */
function renderPanel() {
  if (!$('#statActivos')) return;
  const g = grupo();
  $('#statActivos').textContent = g.activos;
  $('#statSinConexion').textContent = g.sinConexion;
  $('#statRacha').textContent = g.racha;
  $('#statAvance').textContent = `${g.avance}%`;
  const ring = $('#ringAvance');
  ring.style.setProperty('--value', g.avance);
  $('span', ring).textContent = `${g.avance}%`;

  $$('#materias .subject-row').forEach((row, i) => {
    $('[data-val]', row).textContent = `${g.materias[i]}%`;
    $('.progress-bar', row).style.width = `${g.materias[i]}%`;
  });

  const atencion = $('#atencion');
  atencion.replaceChildren();
  g.atencion.forEach(([nombre, detalle, tipo, etiqueta]) => {
    const item = el('div', 'attention-item');
    const info = el('div', 'flex-grow-1');
    info.append(el('div', 'fw-bold', nombre), el('div', 'cell-sub', detalle));
    item.append(el('span', 'avatar', iniciales(nombre)), info, el('span', `status status-${tipo}`, etiqueta));
    atencion.appendChild(item);
  });
}

/* ---------- Estudiantes ---------- */
function renderEstudiantes() {
  const tbody = $('#tablaEstudiantes');
  if (!tbody) return;
  const g = grupo();
  const q = $('#buscarEst').value.trim().toLowerCase();
  const materia = $('#materiaEst').value;
  const estado = $('#estadoEst').value;

  $('#colAvance').textContent = materia === '' ? 'Avance' : `Avance · ${MATERIAS[materia]}`;
  tbody.replaceChildren();

  const visibles = g.alumnos.filter(a => a.nombre.toLowerCase().includes(q) && (!estado || a.estado === estado));
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
    const td = el('td', 'text-center text-secondary py-4', 'No hay estudiantes con esos filtros.');
    td.colSpan = 5;
    tr.appendChild(td);
    tbody.appendChild(tr);
  }
  $('#contadorEstudiantes').textContent = `${visibles.length} de ${g.estudiantes} estudiantes`;
}

function abrirFicha(alumno) {
  $('#fichaIniciales').textContent = iniciales(alumno.nombre);
  $('#fichaNombre').textContent = alumno.nombre;
  $('#fichaAvance').textContent = `${alumno.avance}%`;
  $('#fichaRacha').textContent = alumno.racha;
  $('#fichaEstado').replaceChildren(statusBadge(alumno.estado));
  $('#fichaNota').value = '';

  const materias = $('#fichaMaterias');
  materias.replaceChildren();
  alumno.materias.forEach((valor, i) => {
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

  const lista = (id, items) => {
    const ul = $(id);
    ul.replaceChildren();
    items.forEach(([nombre, valor]) => {
      const li = el('li', 'list-group-item d-flex justify-content-between align-items-center px-0');
      const cls = valor === 'Completada' ? 'status status-success' : valor === 'Sin empezar' ? 'status status-muted' : 'small fw-bold';
      li.append(el('span', '', nombre), el('span', cls, valor));
      ul.appendChild(li);
    });
  };
  lista('#fichaActividades', alumno.actividades);
  lista('#fichaEvaluacion', alumno.evaluacion);

  bootstrap.Modal.getOrCreateInstance('#modalFicha').show();
}

if ($('#filtrosEstudiantes')) {
  $('#filtrosEstudiantes').addEventListener('submit', e => e.preventDefault());
  $$('#filtrosEstudiantes input, #filtrosEstudiantes select').forEach(c => c.addEventListener('input', renderEstudiantes));
}

/* ---------- Actividades ---------- */
const tablaActividades = $('#tablaActividades');
if (tablaActividades) {
  const filtrar = () => {
    const q = $('#buscarAct').value.trim().toLowerCase();
    const materia = $('#materiaAct').value;
    const estado = $('#estadoAct').value;
    let visibles = 0;
    $$('tbody tr', tablaActividades).forEach(tr => {
      const activa = $('input[role="switch"]', tr).checked ? 'Activa' : 'Inactiva';
      const ok = tr.textContent.toLowerCase().includes(q)
        && (!materia || tr.dataset.materia === materia)
        && (!estado || activa === estado);
      tr.classList.toggle('d-none', !ok);
      if (ok) visibles++;
    });
    $('#contadorActividades').textContent = visibles;
  };

  $('#filtrosActividades').addEventListener('submit', e => e.preventDefault());
  $$('#filtrosActividades input, #filtrosActividades select').forEach(c => c.addEventListener('input', filtrar));

  $$('tbody tr', tablaActividades).forEach(tr => {
    const act = ACTIVIDADES[tr.dataset.act];
    const sw = $('input[role="switch"]', tr);

    sw.addEventListener('change', () => {
      const estado = sw.checked ? 'Activa' : 'Inactiva';
      $('[data-estado]', tr).replaceChildren(statusBadge(estado));
      showToast(sw.checked ? `«${act.nombre}» quedó activa para ${grupo().nombre}.` : `«${act.nombre}» ya no aparece en los celulares de ${grupo().nombre}.`);
      filtrar();
    });

    $('[data-ver-actividad]', tr).addEventListener('click', () => {
      const activa = sw.checked;
      $('#actTitulo').textContent = act.nombre;
      $('#actDescripcion').textContent = act.descripcion;
      $('#actMateria').textContent = act.materia;
      $('#actEstado').replaceChildren(statusBadge(activa ? 'Activa' : 'Inactiva'));
      $('#actAvanceTxt').textContent = `${act.avance}%`;
      $('#actAvanceBar').style.width = `${act.avance}%`;

      const ul = $('#actEstudiantes');
      ul.replaceChildren();
      const fichas = grupo().alumnos
        .map(a => [a.nombre, (a.actividades.find(([n]) => n === act.nombre) || [])[1]])
        .filter(([, valor]) => valor);
      if (!fichas.length) {
        ul.appendChild(el('li', 'list-group-item px-0 text-secondary small', 'Ninguna ficha de ejemplo la tiene registrada.'));
      }
      fichas.forEach(([nombre, valor]) => {
        const li = el('li', 'list-group-item d-flex justify-content-between align-items-center px-0');
        const cls = valor === 'Completada' ? 'status status-success' : valor === 'Sin empezar' ? 'status status-muted' : 'small fw-bold';
        li.append(el('span', '', nombre), el('span', cls, valor));
        ul.appendChild(li);
      });

      bootstrap.Modal.getOrCreateInstance('#modalActividad').show();
    });
  });
}

/* ---------- Reportes ---------- */
function renderReportes() {
  const grafico = $('#graficoMaterias');
  if (!grafico) return;
  const g = grupo();
  const periodoKey = $('#periodo').value;
  const periodo = PERIODOS[periodoKey];
  const ajustar = v => Math.min(100, v + periodo.ajuste);

  // Valores exactos del prototipo para el Semestre 1 de 3° A
  const usaSemestre3A = getGrupoKey() === '3A' && periodoKey === 's1';
  const materias = usaSemestre3A ? [68, 64, 56, 51, 39] : g.reporte.materias.map(ajustar);
  const semestre3A = [79, 61, 49, 23];
  const estudiantes = g.reporte.estudiantes.map(([n, v], i) => [n, usaSemestre3A ? semestre3A[i] : ajustar(v)]);

  const promedio = Math.round(materias.reduce((a, b) => a + b, 0) / materias.length);
  const minimo = Math.min(...materias);
  $('#repPromedio').textContent = `${promedio}%`;
  $('#repMinimo').textContent = `${minimo}%`;
  $('#repMinimoNombre').textContent = MATERIAS[materias.indexOf(minimo)];
  $$('[data-periodo-nombre]').forEach(n => { n.textContent = periodo.nombre; });

  grafico.replaceChildren();
  materias.forEach((valor, i) => {
    const col = el('div', 'bar-col');
    const bar = el('div', `bar ${BAR_CLASS[i]}`);
    bar.style.height = `${valor * 1.6}px`;
    col.append(el('span', 'bar-value', `${valor}%`), bar, el('span', 'bar-label', MATERIAS[i]));
    grafico.appendChild(col);
  });

  const tbody = $('#tablaReporte');
  tbody.replaceChildren();
  estudiantes.forEach(([nombre, valor]) => {
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

if ($('#periodo')) {
  $('#periodo').addEventListener('change', renderReportes);
  $('#modalGenerar').addEventListener('show.bs.modal', () => {
    $('#genPeriodo').value = $('#periodo').value;
  });
  if (params.get('generar') === '1') bootstrap.Modal.getOrCreateInstance('#modalGenerar').show();
}

/* ---------- Gestión del grupo ---------- */
const codigosNuevos = {};

function renderGestion() {
  if (!$('#codigoGrupo')) return;
  const key = getGrupoKey();
  $('#codigoGrupo').textContent = codigosNuevos[key] || grupo().codigo;
  $('#usosCodigo').textContent = codigosNuevos[key] ? '30 de 30 usos disponibles' : '18 de 30 usos disponibles';
}

if ($('#btnCopiar')) {
  $('#btnCopiar').addEventListener('click', () => {
    const codigo = $('#codigoGrupo').textContent;
    const done = () => showToast(`Código ${codigo} copiado.`);
    if (navigator.clipboard) navigator.clipboard.writeText(codigo).then(done, done);
    else done();
  });

  $('#btnNuevoCodigo').addEventListener('click', () => {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    const pick = n => Array.from({ length: n }, () => chars[Math.floor(Math.random() * chars.length)]).join('');
    codigosNuevos[getGrupoKey()] = `${pick(4)}-${Math.floor(10 + Math.random() * 90)}`;
    renderGestion();
    showToast('Se generó un código nuevo. El anterior deja de funcionar.');
  });

  $('#switchIA').addEventListener('change', e => {
    $('#labelIA').textContent = e.target.checked ? 'Activado' : 'Desactivado';
    showToast(e.target.checked ? 'Asistente de IA activado para el grupo.' : 'Asistente de IA desactivado para el grupo.');
  });

  $('#btnActualizar').addEventListener('click', e => {
    const btn = e.currentTarget;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Actualizando';
    setTimeout(() => {
      btn.disabled = false;
      btn.innerHTML = '<i class="bi bi-arrow-clockwise me-1"></i> Actualizar';
      $('#paqueteInfo').textContent = 'v2.1 · 340 MB · actualizado hoy';
      showToast('El paquete de conocimiento ya está al día.');
    }, 1200);
  });
}

/* ---------- Mis datos: grupos a cargo ---------- */
function renderMisDatos() {
  const cont = $('#gruposACargo');
  if (!cont) return;
  cont.replaceChildren();
  const actual = getGrupoKey();
  Object.entries(GRUPOS).forEach(([key, g]) => {
    const row = el('div', `group-option${key === actual ? ' is-current' : ''}`);
    const info = el('div', 'flex-grow-1');
    info.append(el('div', 'fw-bold', g.nombre), el('div', 'small text-secondary', `${g.estudiantes} estudiantes · código ${g.codigo}`));
    row.append(el('span', 'group-badge', g.grado), info);
    if (key === actual) row.append(el('span', 'status status-success', 'Grupo activo'));
    cont.appendChild(row);
  });
}

/* ---------- Arranque ---------- */
function renderTodo() {
  renderGrupo();
  renderPanel();
  renderEstudiantes();
  renderReportes();
  renderGestion();
  renderMisDatos();
}

crearModalesCompartidos();
renderTodo();

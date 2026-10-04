/* =========================================================
   Numi · Panel administrativo
   Interacciones del prototipo (modales, filtros y mensajes)
   ========================================================= */

const ACTIVIDADES = {
  'los-numeros':         { nombre: 'Los números',         materia: 'Matemáticas',        grado: '1°', tipo: 'Arrastrar y soltar',   estado: 'Publicada',   resuelta: '612' },
  'arma-la-palabra':     { nombre: 'Arma la palabra',     materia: 'Español',            grado: '3°', tipo: 'Ordenar sílabas',      estado: 'Publicada',   resuelta: '274' },
  'heroes-de-la-ciudad': { nombre: 'Héroes de la ciudad', materia: 'Sociales',           grado: '4°', tipo: 'Selección múltiple',   estado: 'Borrador',    resuelta: 'Sin uso registrado' },
  'escucha-y-elige':     { nombre: 'Escucha y elige',     materia: 'Inglés',             grado: '5°', tipo: 'Comprensión auditiva', estado: 'Publicada',   resuelta: '189' },
  'pasado-y-presente':   { nombre: 'Pasado y presente',   materia: 'Sociales',           grado: '5°', tipo: 'Memory match',         estado: 'Desactivada', resuelta: '43' },
  'vivo-o-no-vivo':      { nombre: '¿Vivo o no vivo?',    materia: 'Ciencias naturales', grado: '2°', tipo: 'Arrastrar',            estado: 'Publicada',   resuelta: 'Sin uso registrado' }
};

const INSTITUCIONES = {
  'la-aldea':    { nombre: 'IE Rural La Aldea',       comuna: 'San Cristóbal',        sedes: 2, estudiantes: 198, grupos: [['Grado 3° — grupo A', 'Luisa Muñoz · 24 estudiantes'], ['Grado 4° — grupo A', 'Andrés Gaviria · 21 estudiantes'], ['Grado 5° — grupo B', null]] },
  'palmitas':    { nombre: 'IE Palmitas',             comuna: 'Palmitas',             sedes: 1, estudiantes: 122, grupos: [['Grado 2° — grupo A', 'Andrés Gaviria · 18 estudiantes'], ['Grado 4° — grupo A', null]] },
  'santa-elena': { nombre: 'IE Santa Elena',          comuna: 'Santa Elena',          sedes: 3, estudiantes: 156, grupos: [['Grado 1° — grupo A', 'Marta Ríos · 22 estudiantes'], ['Grado 3° — grupo B', 'Pedro Cano · 20 estudiantes']] },
  'san-antonio': { nombre: 'IE San Antonio de Prado', comuna: 'San Antonio de Prado', sedes: 2, estudiantes: 66,  grupos: [['Grado 5° — grupo A', 'Jhon Quintero · 19 estudiantes']] }
};

const STATUS_CLASS = {
  Publicada: 'status-success', Activa: 'status-success', Activo: 'status-success',
  Borrador: 'status-warning', Pendiente: 'status-warning',
  Desactivada: 'status-muted', Inactivo: 'status-muted', Inactiva: 'status-muted'
};

const params = new URLSearchParams(window.location.search);
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));

/* ---------- Utilidades de mensajes ---------- */
function showToast(message) {
  const area = $('#toastArea');
  if (!area) return;
  const toast = document.createElement('div');
  toast.className = 'toast align-items-center text-bg-dark border-0';
  toast.setAttribute('role', 'status');
  toast.innerHTML = '<div class="d-flex"><div class="toast-body"></div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Cerrar"></button></div>';
  $('.toast-body', toast).textContent = message;
  area.appendChild(toast);
  new bootstrap.Toast(toast, { delay: 3500 }).show();
  toast.addEventListener('hidden.bs.toast', () => toast.remove());
}

function showFlash(message, type = 'success') {
  const flash = $('#flash');
  if (!flash) return;
  const alert = document.createElement('div');
  alert.className = `alert alert-${type} alert-dismissible fade show d-flex align-items-center gap-2`;
  alert.setAttribute('role', 'alert');
  alert.innerHTML = '<i class="bi bi-check-circle-fill"></i><span></span><button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>';
  $('span', alert).textContent = message;
  flash.replaceChildren(alert);
}

function setStatus(el, estado) {
  el.className = `status ${STATUS_CLASS[estado] || 'status-muted'}`;
  el.textContent = estado;
}

/* ---------- Avisos de demostración ---------- */
$$('[data-demo]').forEach(link => link.addEventListener('click', e => {
  e.preventDefault();
  showToast(link.dataset.demo);
}));

$$('[data-toast]').forEach(btn => btn.addEventListener('click', () => showToast(btn.dataset.toast)));

/* ---------- Inicio de sesión ---------- */
const loginForm = $('#loginForm');
if (loginForm) {
  loginForm.addEventListener('submit', e => {
    e.preventDefault();
    const email = $('#email').value.trim().toLowerCase();
    const error = $('#loginError');
    if (!loginForm.checkValidity()) {
      loginForm.classList.add('was-validated');
      return;
    }
    if (email.endsWith('@medellin.gov.co')) {
      window.location.href = 'inicio.html';
    } else {
      error.classList.remove('d-none');
    }
  });
}

/* ---------- Filtros de tablas ---------- */
$$('[data-table-filter]').forEach(form => {
  const table = $(form.dataset.tableFilter);
  if (!table) return;
  const controls = $$('[data-filter]', form);
  const counter = $('[data-visible]', table.closest('.card'));

  const apply = () => {
    let visible = 0;
    $$('tbody tr', table).forEach(row => {
      if (row.dataset.hidden === 'true') return;
      const ok = controls.every(ctrl => {
        const value = ctrl.value.trim().toLowerCase();
        if (!value) return true;
        if (ctrl.dataset.filter === 'text') return row.textContent.toLowerCase().includes(value);
        return (row.dataset[ctrl.dataset.filter] || '').toLowerCase() === value;
      });
      row.classList.toggle('d-none', !ok);
      if (ok) visible++;
    });
    if (counter) counter.textContent = visible;
  };

  controls.forEach(ctrl => ctrl.addEventListener('input', apply));
  form.addEventListener('submit', e => e.preventDefault());
  form.applyFilters = apply;
});

/* ---------- Actividades: mensajes después de publicar o eliminar ---------- */
const tablaActividades = $('#tablaActividades');
if (tablaActividades) {
  const nuevaFila = $('tr[data-id="vivo-o-no-vivo"]', tablaActividades);
  nuevaFila.dataset.hidden = 'true';
  let total = 48;

  if (params.get('msg') === 'publicada') {
    nuevaFila.classList.remove('d-none');
    delete nuevaFila.dataset.hidden;
    total = 49;
    showFlash('Actividad publicada. Llega al celular del niño en su próxima sincronización.');
  }
  if (params.get('msg') === 'cambios') {
    showFlash('Cambios publicados. Llegan al celular del niño en su próxima sincronización.');
  }

  const eliminada = params.get('eliminada');
  if (eliminada && ACTIVIDADES[eliminada]) {
    const fila = $(`tr[data-id="${eliminada}"]`, tablaActividades);
    if (fila) {
      fila.classList.add('d-none');
      fila.dataset.hidden = 'true';
    }
    total = 47;
    showFlash(`Se eliminó la actividad «${ACTIVIDADES[eliminada].nombre}».`);
  }

  const visibles = $$('tbody tr', tablaActividades).filter(r => !r.classList.contains('d-none')).length;
  $('[data-visible]').textContent = visibles;
  $('[data-total]').textContent = total;
  $('[data-count]').textContent = total;
}

/* ---------- Borradores ---------- */
if ($('#tablaBorradores') && params.get('msg') === 'borrador') {
  $('#tablaBorradores tr[data-id="vivo-o-no-vivo"]').classList.remove('d-none');
  $('#draftCount').textContent = '2 borradores';
  showFlash('Actividad guardada como borrador.');
}

/* ---------- Detalle de actividad ---------- */
if ($('#modalEliminar')) {
  const id = ACTIVIDADES[params.get('id')] ? params.get('id') : 'los-numeros';
  const act = ACTIVIDADES[id];
  document.title = `${act.nombre} · Numi Admin`;
  $$('[data-act]').forEach(el => {
    const key = el.dataset.act;
    if (key === 'estadoBadge') setStatus(el, act.estado);
    else el.textContent = act[key];
  });
  $('#btnEditar').href = `constructor.html?id=${id}`;
  $('#btnConfirmarEliminar').href = `actividades.html?eliminada=${id}`;
}

/* ---------- Constructor de actividades ---------- */
const resourceGrid = $('#resourceGrid');
if (resourceGrid) {
  const id = params.get('id');
  const act = ACTIVIDADES[id];
  const esEdicion = act && id !== 'vivo-o-no-vivo';

  if (act) {
    $('#actNombre').value = act.nombre;
    $('#actMateria').value = act.materia;
    $('#actGrado').value = `Grado ${act.grado}`;
    $('#actTipo').value = act.tipo;
  }
  if (esEdicion) {
    document.title = 'Editar actividad · Numi Admin';
    $('#builderTitle').textContent = 'Editar actividad';
    $('#builderCrumb').innerHTML = '<li class="breadcrumb-item"><a href="actividades.html">Actividades</a></li><li class="breadcrumb-item"></li><li class="breadcrumb-item active" aria-current="page">Editar</li>';
    const crumb = $('#builderCrumb .breadcrumb-item:nth-child(2)');
    const link = document.createElement('a');
    link.href = `actividad-detalle.html?id=${id}`;
    link.textContent = act.nombre;
    crumb.appendChild(link);
    $('#resEstado').textContent = 'Publicada (reemplaza la versión actual)';
    $('#btnContinuar').href = 'actividades.html?msg=cambios';
  }

  // Selección sincronizada entre la cuadrícula y el modal "Más recursos"
  const allChecks = () => $$('input[type="checkbox"]', resourceGrid).concat($$('#tablaRecursosModal input[type="checkbox"]'));
  const selected = new Map();

  const render = () => {
    allChecks().forEach(cb => { cb.checked = selected.has(cb.value); });
    const n = selected.size;
    $('#selCount').textContent = `${n} seleccionado${n === 1 ? '' : 's'}`;
  };

  allChecks().forEach(cb => cb.addEventListener('change', () => {
    if (cb.checked) selected.set(cb.value, cb.dataset.tipo || 'Imagen');
    else selected.delete(cb.value);
    render();
  }));

  $('#buscarRecursoModal').addEventListener('input', e => {
    const q = e.target.value.trim().toLowerCase();
    $$('#tablaRecursosModal tbody tr').forEach(r => r.classList.toggle('d-none', !r.textContent.toLowerCase().includes(q)));
  });

  $('#modalResumen').addEventListener('show.bs.modal', () => {
    $('#resNombre').textContent = $('#actNombre').value || 'Sin nombre';
    $('#resMateria').textContent = $('#actMateria').value;
    $('#resGrado').textContent = $('#actGrado').value;
    $('#resTipo').textContent = $('#actTipo').value;
    $('#resCount').textContent = `${selected.size} recurso${selected.size === 1 ? '' : 's'}`;
    const list = $('#resLista');
    list.replaceChildren();
    selected.forEach((tipo, nombre) => {
      const li = document.createElement('li');
      li.textContent = `${nombre} · ${tipo}`;
      list.appendChild(li);
    });
  });

  render();
}

/* ---------- Instituciones ---------- */
const modalInstitucion = $('#modalInstitucion');
if (modalInstitucion) {
  modalInstitucion.addEventListener('show.bs.modal', e => {
    const inst = INSTITUCIONES[e.relatedTarget?.dataset.inst];
    if (!inst) return;
    $('#modalInstitucionTitulo').textContent = inst.nombre;
    $('#instComuna').textContent = inst.comuna;
    $('#instSedes').textContent = inst.sedes;
    $('#instEstudiantes').textContent = inst.estudiantes;
    const list = $('#instGrupos');
    list.replaceChildren();
    inst.grupos.forEach(([grupo, docente]) => {
      const li = document.createElement('li');
      li.className = 'list-group-item d-flex justify-content-between align-items-center gap-2';
      const name = document.createElement('span');
      name.className = 'fw-semibold';
      name.textContent = grupo;
      const meta = document.createElement('span');
      meta.className = docente ? 'small text-secondary text-end' : 'status status-warning';
      meta.textContent = docente || 'Sin docente asignado';
      li.append(name, meta);
      list.appendChild(li);
    });
  });
  if (params.get('msg') === 'institucion') showFlash('Institución creada. Ya puedes agregar sus grupos.');
}

const formInstitucion = $('#formInstitucion');
if (formInstitucion) {
  formInstitucion.addEventListener('submit', e => {
    e.preventDefault();
    if (!formInstitucion.checkValidity()) {
      formInstitucion.classList.add('was-validated');
      return;
    }
    window.location.href = 'instituciones.html?msg=institucion';
  });
}

/* ---------- Usuarios ---------- */
const tablaUsuarios = $('#tablaUsuarios');
if (tablaUsuarios) {
  const modalEditar = new bootstrap.Modal('#modalEditar');
  const modalConfirmar = new bootstrap.Modal('#modalConfirmarEstado');
  let filaActual = null;

  const estadoDe = fila => fila.dataset.estado;
  const nombreDe = fila => $('[data-field="nombre"]', fila).textContent;

  $$('[data-edit-user]', tablaUsuarios).forEach(btn => btn.addEventListener('click', () => {
    filaActual = btn.closest('tr');
    const [nombre, ...resto] = nombreDe(filaActual).split(' ');
    $('#modalEditarTitulo').textContent = nombreDe(filaActual);
    $('#edNombre').value = nombre;
    $('#edApellido').value = resto.join(' ');
    $('#edCorreo').value = $('.cell-sub', filaActual).textContent;
    $('#edRol').value = filaActual.dataset.rol;
    $('#edInst').value = filaActual.dataset.institucion;
    $('#btnToggleEstado').textContent = estadoDe(filaActual) === 'Inactivo' ? 'Activar usuario' : 'Desactivar usuario';
    $('#btnToggleEstado').className = estadoDe(filaActual) === 'Inactivo' ? 'btn btn-outline-success' : 'btn btn-outline-danger';
    modalEditar.show();
  }));

  $('#btnToggleEstado').addEventListener('click', () => {
    const activar = estadoDe(filaActual) === 'Inactivo';
    const nombre = nombreDe(filaActual);
    $('#modalConfirmarTitulo').textContent = activar ? `¿Activar a ${nombre}?` : `¿Desactivar a ${nombre}?`;
    $('#confirmTexto').textContent = activar
      ? 'Podrá volver a iniciar sesión en Numi con su correo institucional.'
      : 'No podrá iniciar sesión en Numi. El registro no se elimina: queda en la lista de usuarios con estado Inactivo.';
    $('#btnConfirmarEstado').textContent = activar ? 'Activar' : 'Desactivar';
    $('#btnConfirmarEstado').className = activar ? 'btn btn-success' : 'btn btn-danger';
    $('#confirmIcon').className = activar ? 'danger-icon bg-success-subtle text-success' : 'danger-icon';
    modalEditar.hide();
    modalConfirmar.show();
  });

  $('#btnConfirmarEstado').addEventListener('click', () => {
    const activar = estadoDe(filaActual) === 'Inactivo';
    const nuevo = activar ? 'Activo' : 'Inactivo';
    const nombre = nombreDe(filaActual);
    filaActual.dataset.estado = nuevo;
    setStatus($('[data-field="estado"] .status', filaActual), nuevo);
    modalConfirmar.hide();
    showFlash(activar
      ? `Se activó la cuenta de ${nombre}. Ya puede volver a iniciar sesión en Numi.`
      : `Se desactivó la cuenta de ${nombre}. Su registro no se eliminó: sigue en la lista como Inactivo.`);
  });

  $('#formEditar').addEventListener('submit', e => {
    e.preventDefault();
    modalEditar.hide();
    showFlash(`Se guardaron los cambios de ${nombreDe(filaActual)}.`);
  });

  const modalCrearEl = $('#modalCrear');
  $('#formCrear').addEventListener('submit', e => {
    e.preventDefault();
    bootstrap.Modal.getOrCreateInstance(modalCrearEl).hide();
    showFlash(`Se creó la cuenta de ${$('#crNombre').value} ${$('#crApellido').value}. Queda pendiente de aprobación.`);
    e.target.reset();
  });
  if (params.get('crear') === '1') bootstrap.Modal.getOrCreateInstance(modalCrearEl).show();

  // Botón "Revisar" del aviso de docentes pendientes
  $('[data-filter-shortcut]').addEventListener('click', e => {
    const select = $('#estadoUsr');
    select.value = e.currentTarget.dataset.filterShortcut;
    select.dispatchEvent(new Event('input'));
  });
}

/* ---------- Monitoreo: botón de versiones ---------- */
const versiones = $('#versiones');
if (versiones) {
  versiones.addEventListener('shown.bs.collapse', () => { $('#btnVersiones').textContent = 'Ocultar'; });
  versiones.addEventListener('hidden.bs.collapse', () => { $('#btnVersiones').textContent = 'Ver versiones'; });
}

import { Modal } from 'bootstrap';

import { getInstituciones } from '../api/instituciones.api.js';
import {
  cambiarEstado,
  crearUsuario,
  editarUsuario,
  getUsuarios,
  importarUsuarios,
  restablecerPassword,
} from '../api/usuarios.api.js';
import { aplicarFiltros } from '../components/tablas/filtros.js';
import { mostrarPasswordTemporal } from '../components/usuarios/PasswordTemporal.js';
import { crearSelectorGrupos } from '../components/usuarios/SelectorGrupos.js';
import { statusSpan } from '../utils/badges.js';
import { $, el } from '../utils/dom.js';
import { fijarTotal, plural } from '../utils/formatters.js';
import { mostrarError, showFlash, showToast } from '../utils/toast.js';

export function UsuariosPage() {
  return `<header class="topbar">
        <button class="btn btn-light d-lg-none" type="button" data-bs-toggle="offcanvas" data-bs-target="#sidebar" aria-controls="sidebar" aria-label="Abrir menú"><i class="bi bi-list"></i></button>
        <a href="#/inicio" class="btn-back"><i class="bi bi-arrow-left"></i> Volver</a>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="#/inicio">Inicio</a></li>
            <li class="breadcrumb-item active" aria-current="page">Usuarios</li>
          </ol>
        </nav>
        <div class="topbar-actions">
          <button type="button" class="btn btn-outline-secondary btn-sm" data-bs-toggle="modal" data-bs-target="#modalImportar"><i class="bi bi-upload me-1"></i> Importar usuarios</button>
          <button type="button" class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#modalCrear"><i class="bi bi-person-plus me-1"></i> Crear usuario</button>
        </div>
      </header>

<main class="app-content">
        <div class="page-header">
          <div>
            <h1 class="page-title">Usuarios y roles</h1>
            <p class="page-subtitle">Docentes y administradores con acceso a Numi.</p>
          </div>
        </div>

        <div id="flash"></div>

        <div class="alert alert-warning d-flex align-items-center gap-3 flex-wrap" role="alert">
          <i class="bi bi-hourglass-split fs-5"></i>
          <span class="flex-grow-1"><strong>4 docentes</strong> esperan aprobación para entrar a su grupo.</span>
          <button type="button" class="btn btn-sm btn-warning" data-filter-shortcut="Pendiente">Revisar</button>
        </div>

        <form class="filters" data-table-filter="#tablaUsuarios">
          <div class="row g-3 align-items-end">
            <div class="col-md-6 col-xl-3">
              <label class="form-label" for="buscarUsr">Buscar</label>
              <div class="input-group">
                <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
                <input type="search" class="form-control" id="buscarUsr" placeholder="Nombre o correo" data-filter="text">
              </div>
            </div>
            <div class="col-md-6 col-xl-3">
              <label class="form-label" for="rolUsr">Rol</label>
              <select class="form-select" id="rolUsr" data-filter="rol">
                <option value="">Todos los roles</option>
                <option>Docente</option>
                <option>Administrador</option>
              </select>
            </div>
            <div class="col-md-6 col-xl-3">
              <label class="form-label" for="instUsr">Institución</label>
              <select class="form-select" id="instUsr" data-filter="institucion">
                <option value="">Todas las instituciones</option>
              </select>
            </div>
            <div class="col-md-6 col-xl-3">
              <label class="form-label" for="estadoUsr">Estado</label>
              <select class="form-select" id="estadoUsr" data-filter="estado">
                <option value="">Todos los estados</option>
                <option>Activo</option>
                <option>Pendiente</option>
                <option>Inactivo</option>
              </select>
            </div>
          </div>
        </form>

        <div class="card table-card">
          <div class="table-responsive">
            <table class="table table-hover" id="tablaUsuarios">
              <thead>
                <tr><th>Usuario</th><th>Rol</th><th>Institución</th><th>Último acceso</th><th>Estado</th><th class="text-end">Acción</th></tr>
              </thead>
              <tbody>
              </tbody>
            </table>
          </div>
          <div class="table-footer">
            <span><span data-visible>0</span> de 0 usuarios</span>
            <ul class="pagination pagination-sm"></ul>
          </div>
        </div>
      </main>

<div class="modal fade" id="modalEditar" tabindex="-1" aria-labelledby="modalEditarTitulo" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <form class="modal-content" id="formEditar">
        <div class="modal-header">
          <div>
            <p class="small text-secondary mb-0">Editar usuario</p>
            <h2 class="modal-title fs-5" id="modalEditarTitulo">Editar usuario</h2>
          </div>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
        </div>
        <div class="modal-body">
          <div class="row g-3">
            <div class="col-sm-6">
              <label class="form-label" for="edNombre">Nombre</label>
              <input type="text" class="form-control" id="edNombre">
            </div>
            <div class="col-sm-6">
              <label class="form-label" for="edApellido">Apellido</label>
              <input type="text" class="form-control" id="edApellido">
            </div>
            <div class="col-12">
              <label class="form-label" for="edCorreo">Correo institucional</label>
              <input type="email" class="form-control" id="edCorreo">
            </div>
            <div class="col-sm-6">
              <label class="form-label" for="edRol">Rol</label>
              <select class="form-select" id="edRol" disabled>
                <option>Docente</option>
              </select>
            </div>
            <div class="col-sm-6">
              <label class="form-label" for="edInst">Institución</label>
              <select class="form-select" id="edInst"></select>
            </div>
          </div>
        </div>
        <div class="modal-footer justify-content-between">
          <button type="button" class="btn btn-outline-danger" id="btnToggleEstado">Desactivar usuario</button>
          <div class="d-flex gap-2">
            <button type="button" class="btn btn-light" data-bs-dismiss="modal">Cancelar</button>
            <button type="submit" class="btn btn-primary">Guardar cambios</button>
          </div>
        </div>
      </form>
    </div>
  </div>

<div class="modal fade" id="modalConfirmarEstado" tabindex="-1" aria-labelledby="modalConfirmarTitulo" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-body text-center p-4">
          <div class="danger-icon" id="confirmIcon"><i class="bi bi-exclamation-lg"></i></div>
          <h2 class="h5 fw-bold" id="modalConfirmarTitulo">¿Desactivar usuario?</h2>
          <p class="text-secondary mb-0" id="confirmTexto">No podrá iniciar sesión en Numi. El registro no se elimina: queda en la lista de usuarios con estado Inactivo.</p>
        </div>
        <div class="modal-footer justify-content-center border-0 pt-0 pb-4">
          <button type="button" class="btn btn-light" data-bs-dismiss="modal">Cancelar</button>
          <button type="button" class="btn btn-danger" id="btnConfirmarEstado">Desactivar</button>
        </div>
      </div>
    </div>
  </div>

<div class="modal fade" id="modalCrear" tabindex="-1" aria-labelledby="modalCrearTitulo" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <form class="modal-content" id="formCrear">
        <div class="modal-header">
          <h2 class="modal-title fs-5" id="modalCrearTitulo">Crear usuario</h2>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
        </div>
        <div class="modal-body">
          <div class="row g-3">
            <div class="col-sm-6">
              <label class="form-label" for="crNombre">Nombre</label>
              <input type="text" class="form-control" id="crNombre" required>
            </div>
            <div class="col-sm-6">
              <label class="form-label" for="crApellido">Apellido</label>
              <input type="text" class="form-control" id="crApellido" required>
            </div>
            <div class="col-12">
              <label class="form-label" for="crCorreo">Correo institucional</label>
              <input type="email" class="form-control" id="crCorreo" placeholder="nombre@ie.edu.co" required>
            </div>
            <div class="col-sm-6">
              <label class="form-label" for="crRol">Rol</label>
              <select class="form-select" id="crRol" disabled><option>Docente</option></select>
            </div>
            <div class="col-sm-6">
              <label class="form-label" for="crInst">Institución</label>
              <select class="form-select" id="crInst"></select>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-light" data-bs-dismiss="modal">Cancelar</button>
          <button type="submit" class="btn btn-primary">Crear cuenta</button>
        </div>
      </form>
    </div>
  </div>

<div class="modal fade" id="modalImportar" tabindex="-1" aria-labelledby="modalImportarTitulo" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <div>
            <h2 class="modal-title fs-5" id="modalImportarTitulo">Importar usuarios</h2>
            <p class="small text-secondary mb-0">Crea varias cuentas a la vez desde un archivo CSV o JSON.</p>
          </div>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
        </div>
        <div class="modal-body">
          <div class="row g-3 mb-3">
            <div class="col-sm-6">
              <label class="form-label" for="impRol">Rol</label>
              <select class="form-select" id="impRol" disabled><option>Docente</option></select>
            </div>
            <div class="col-sm-6">
              <label class="form-label" for="impInst">Institución</label>
              <select class="form-select" id="impInst"></select>
            </div>
          </div>
          <div class="dropzone">
            <i class="bi bi-file-earmark-arrow-up d-block mb-2"></i>
            <p class="fw-semibold mb-2 text-dark">Arrastra aquí tu archivo .csv o .json</p>
            <label class="btn btn-soft btn-sm">Seleccionar archivo <input type="file" class="d-none" accept=".csv,.json"></label>
          </div>
          <p class="small fw-semibold mt-3 mb-1">Columnas del archivo, en este orden</p>
          <div class="d-flex gap-2 flex-wrap">
            <code class="bg-light px-2 py-1 rounded">nombre</code>
            <code class="bg-light px-2 py-1 rounded">apellido</code>
            <code class="bg-light px-2 py-1 rounded">correo_institucional</code>
          </div>
          <p class="small text-secondary mt-3 mb-0">Demostración: en el prototipo el archivo no se carga ni se procesa.</p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-light" data-bs-dismiss="modal">Cancelar</button>
          <button type="button" class="btn btn-primary" data-bs-dismiss="modal">Importar usuarios</button>
        </div>
      </div>
    </div>
  </div>`;
}

function llenarSelect(select, opciones, conservarPrimera = false) {
  const primera = conservarPrimera ? [select.options[0]] : [];
  select.replaceChildren(...primera, ...opciones.map((texto) => el('option', '', texto)));
}

export function mountUsuariosPage({ query }) {
  const tablaUsuarios = $('#tablaUsuarios');
  const tbody = $('tbody', tablaUsuarios);
  const modalEditar = new Modal('#modalEditar');
  const modalConfirmar = new Modal('#modalConfirmarEstado');
  const modalCrearEl = $('#modalCrear');
  const modalImportar = $('#modalImportar');
  const botonImportar = $('.modal-footer .btn-primary', modalImportar);
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
    let datos;
    try {
      datos = await restablecerPassword(actual.id);
    } catch (error) {
      prepararRestablecer();
      return mostrarError(error);
    }
    prepararRestablecer();
    modalEditar.hide();
    mostrarPasswordTemporal(actual.nombre_completo, datos.password_temporal);
  });

  const abrirEditar = (u) => {
    actual = u;
    $('#modalEditarTitulo').textContent = u.nombre_completo;
    $('#edNombre').value = u.nombre;
    $('#edApellido').value = u.apellido;
    $('#edCorreo').value = u.correo;
    $('#edRol').replaceChildren(new Option(u.rol, u.rol)); // el rol de una cuenta no se cambia
    $('#edInst').value = u.institucion;
    gruposEditar.abrir(
      u.id,
      u.grupos.map((g) => g.id),
    );
    const activar = u.estado !== 'Activo';
    $('#btnToggleEstado').textContent = activar ? 'Activar usuario' : 'Desactivar usuario';
    $('#btnToggleEstado').className = activar ? 'btn btn-outline-success' : 'btn btn-outline-danger';
    prepararRestablecer();
    bloqueContrasena.classList.toggle('d-none', u.estado !== 'Activo'); // solo cuentas activas
    modalEditar.show();
  };

  const filaUsuario = (u) => {
    const tr = el('tr');
    Object.assign(tr.dataset, { user: u.id, rol: u.rol, institucion: u.institucion, estado: u.estado });
    const tdUsuario = el('td');
    const envoltura = el('div', 'd-flex align-items-center gap-2');
    const textos = el('div');
    const nombre = el('div', 'cell-title', u.nombre_completo);
    nombre.dataset.field = 'nombre';
    textos.append(nombre, el('div', 'cell-sub', u.correo));
    envoltura.append(el('span', 'avatar', u.iniciales), textos);
    tdUsuario.appendChild(envoltura);
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
    if (u.grupos.length) tdInstitucion.append(el('div', 'cell-sub', u.grupos.map((g) => g.corto).join(' · ')));
    tr.append(tdUsuario, el('td', '', u.rol), tdInstitucion, el('td', 'text-nowrap', u.ultimo_acceso), tdEstado, tdAccion);
    return tr;
  };

  const cargar = async (reiniciar = true) => {
    let datos;
    try {
      datos = await getUsuarios();
    } catch (error) {
      return mostrarError(error);
    }
    tbody.replaceChildren(...datos.map(filaUsuario));
    const pendientes = datos.filter((u) => u.estado === 'Pendiente').length;
    const aviso = $('.alert-warning', $('main'));
    aviso.classList.toggle('d-none', !pendientes);
    $('strong', aviso).textContent = plural(pendientes, 'docente', 'docentes');
    $('span.flex-grow-1', aviso).lastChild.textContent = pendientes === 1 ? ' espera aprobación para entrar a su grupo.' : ' esperan aprobación para entrar a su grupo.';
    fijarTotal($('[data-visible]', tablaUsuarios.closest('.card')), datos.length, 'usuarios');
    aplicarFiltros('#tablaUsuarios', reiniciar);
  };

  $('#btnToggleEstado').addEventListener('click', () => {
    const activar = actual.estado !== 'Activo';
    const nombre = actual.nombre_completo;
    $('#modalConfirmarTitulo').textContent = activar ? `¿Activar a ${nombre}?` : `¿Desactivar a ${nombre}?`;
    $('#confirmTexto').textContent = activar
      ? actual.estado === 'Pendiente'
        ? 'Se aprueba la cuenta y podrá iniciar sesión en Numi. Si no tiene contraseña, se genera una temporal.'
        : 'Podrá volver a iniciar sesión en Numi con su correo institucional.'
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
    let datos;
    try {
      datos = await cambiarEstado(actual.id, activar ? 'Activo' : 'Inactivo');
    } catch (error) {
      modalConfirmar.hide();
      return mostrarError(error);
    }
    modalConfirmar.hide();
    showFlash(
      activar
        ? `Se activó la cuenta de ${nombre}. Ya puede iniciar sesión en Numi.`
        : `Se desactivó la cuenta de ${nombre}. Su registro no se eliminó: sigue en la lista como Inactivo.`,
    );
    // La contraseña temporal va en su propia ventana para que no pase desapercibida
    if (datos.password_temporal) mostrarPasswordTemporal(nombre, datos.password_temporal);
    cargar(false);
  });

  $('#formEditar').addEventListener('submit', async (e) => {
    e.preventDefault();
    let usuario;
    try {
      usuario = await editarUsuario(actual.id, {
        nombre: $('#edNombre').value,
        apellido: $('#edApellido').value,
        correo: $('#edCorreo').value,
        rol: $('#edRol').value,
        institucion: $('#edInst').value,
        grupos: gruposEditar.ids(),
      });
    } catch (error) {
      return mostrarError(error);
    }
    modalEditar.hide();
    showFlash(`Se guardaron los cambios de ${usuario.nombre_completo}.`);
    cargar(false);
  });

  $('#formCrear').addEventListener('submit', async (e) => {
    e.preventDefault();
    let usuario;
    try {
      usuario = await crearUsuario({
        nombre: $('#crNombre').value,
        apellido: $('#crApellido').value,
        correo: $('#crCorreo').value,
        rol: $('#crRol').value,
        institucion: $('#crInst').value,
        grupos: gruposCrear.ids(),
      });
    } catch (error) {
      return mostrarError(error);
    }
    Modal.getOrCreateInstance(modalCrearEl).hide();
    showFlash(`Se creó la cuenta de ${usuario.nombre_completo}. Queda pendiente de aprobación.`);
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
  zona.addEventListener('dragover', (e) => e.preventDefault());
  zona.addEventListener('drop', (e) => {
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
    let datos;
    try {
      datos = await importarUsuarios(formulario);
    } catch (error) {
      archivoImportar.value = '';
      archivoImportar.dispatchEvent(new Event('change'));
      return mostrarError(error);
    }
    archivoImportar.value = '';
    archivoImportar.dispatchEvent(new Event('change'));
    let mensaje = `Se ${datos.creados === 1 ? 'creó' : 'crearon'} ${plural(datos.creados, 'cuenta', 'cuentas')} pendientes de aprobación.`;
    if (datos.omitidos.length) mensaje += ` Omitidas: ${datos.omitidos.join('; ')}.`;
    showFlash(mensaje, datos.creados ? 'success' : 'warning');
    cargar();
  });

  // Botón "Revisar" del aviso de docentes pendientes
  $('[data-filter-shortcut]').addEventListener('click', (e) => {
    const select = $('#estadoUsr');
    select.value = e.currentTarget.dataset.filterShortcut;
    select.dispatchEvent(new Event('input', { bubbles: true }));
  });

  // Instituciones reales en los selectores
  getInstituciones()
    .then((datos) => {
      instituciones = datos;
      const nombres = datos.map((i) => i.nombre).sort((a, b) => a.localeCompare(b));
      llenarSelect($('#instUsr'), [...nombres, 'Todas'], true);
      llenarSelect($('#edInst'), [...nombres, 'Todas']);
      llenarSelect($('#crInst'), nombres);
      llenarSelect($('#impInst'), nombres);
      // Si "Crear usuario" ya estaba abierto (#/usuarios?crear=1), carga sus grupos ahora
      if (modalCrearEl.classList.contains('show')) gruposCrear.abrir(null, []);
    })
    .catch(() => {});

  if (query.get('crear') === '1') Modal.getOrCreateInstance(modalCrearEl).show();
  return cargar().then(() => {
    if (query.get('estado') === 'Pendiente') $('[data-filter-shortcut]').click();
  });
}

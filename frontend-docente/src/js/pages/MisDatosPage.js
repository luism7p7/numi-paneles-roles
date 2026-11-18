import { estado } from '../state/docente.store.js';
import { $, $$, el } from '../utils/dom.js';

export function MisDatosPage() {
  return `<div class="section-bar">
        <a href="#/panel" class="btn-back"><i class="bi bi-arrow-left"></i> Volver</a>
        <h2 class="section-title">Mis datos</h2>
        <div class="section-actions"><span class="status status-muted"><i class="bi bi-lock-fill"></i> Solo lectura</span></div>
      </div>

<main class="app-content">
        <div class="row g-4">
          <!-- Tarjeta de perfil -->
          <div class="col-lg-4">
            <div class="card text-center p-4 h-100">
              <span class="avatar avatar-lg mx-auto mb-3" style="background: var(--numi-primary); color: #fff;">—</span>
              <h3 class="h5 fw-bold mb-0">—</h3>
              <p class="text-secondary mb-3">Docente</p>
              <p class="small mb-0"><i class="bi bi-envelope me-1 text-primary"></i> —</p>
            </div>
          </div>

          <!-- Datos personales -->
          <div class="col-lg-8">
            <div class="card h-100">
              <div class="card-header"><h3 class="card-title">Datos personales</h3></div>
              <div class="card-body p-4">
                <div class="row g-3">
                  <div class="col-sm-6">
                    <label class="form-label" for="dNombre">Nombre</label>
                    <input type="text" class="form-control" id="dNombre" value="" readonly>
                  </div>
                  <div class="col-sm-6">
                    <label class="form-label" for="dApellido">Apellido</label>
                    <input type="text" class="form-control" id="dApellido" value="" readonly>
                  </div>
                  <div class="col-sm-6">
                    <label class="form-label" for="dCorreo">Correo institucional</label>
                    <input type="email" class="form-control" id="dCorreo" value="" readonly>
                  </div>
                  <div class="col-sm-6">
                    <label class="form-label" for="dDoc">Documento de identidad</label>
                    <input type="text" class="form-control" id="dDoc" value="C.C. ••••••••••" readonly>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Institución -->
          <div class="col-lg-6">
            <div class="card h-100">
              <div class="card-header"><h3 class="card-title">Institución</h3></div>
              <div class="card-body p-4">
                <dl class="row detail-list mb-0">
                  <dt class="col-6">Institución</dt><dd class="col-6">—</dd>
                  <dt class="col-6">Sede</dt><dd class="col-6">—</dd>
                  <dt class="col-6">Comuna o corregimiento</dt><dd class="col-6">—</dd>
                  <dt class="col-6">Rol</dt><dd class="col-6 mb-0">Docente</dd>
                </dl>
              </div>
            </div>
          </div>

          <!-- Grupos a cargo -->
          <div class="col-lg-6">
            <div class="card h-100">
              <div class="card-header"><h3 class="card-title">Grupos a cargo</h3></div>
              <div class="card-body p-4" id="gruposACargo"><!-- Lo completa app.js --></div>
            </div>
          </div>
        </div>

        <div class="notice mt-4 mb-0">
          <i class="bi bi-info-circle"></i>
          <div>Esta pantalla es solo informativa. Tus datos los administra la coordinación de tu sede.</div>
        </div>
      </main>`;
}

export function mountMisDatosPage() {
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
  [yo.institucion, yo.sede, yo.comuna, yo.rol].forEach((valor, i) => {
    if (datosInstitucion[i]) datosInstitucion[i].textContent = valor;
  });

  const contenedor = $('#gruposACargo');
  contenedor.replaceChildren();
  Object.values(estado.grupos).forEach((g) => {
    const actual = g.id === estado.activo;
    const fila = el('div', `group-option${actual ? ' is-current' : ''}`);
    const info = el('div', 'flex-grow-1');
    info.append(el('div', 'fw-bold', g.nombre), el('div', 'small text-secondary', `${g.estudiantes} estudiantes · código ${g.codigo}`));
    fila.append(el('span', 'group-badge', g.grado), info);
    if (actual) fila.append(el('span', 'status status-success', 'Grupo activo'));
    contenedor.appendChild(fila);
  });
}

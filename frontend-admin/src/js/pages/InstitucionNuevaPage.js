import { crearInstitucion } from '../api/instituciones.api.js';
import { $ } from '../utils/dom.js';
import { mostrarError } from '../utils/toast.js';

export function InstitucionNuevaPage() {
  return `<header class="topbar">
        <button class="btn btn-light d-lg-none" type="button" data-bs-toggle="offcanvas" data-bs-target="#sidebar" aria-controls="sidebar" aria-label="Abrir menú"><i class="bi bi-list"></i></button>
        <a href="#/instituciones" class="btn-back"><i class="bi bi-arrow-left"></i> Volver</a>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="#/instituciones">Instituciones</a></li>
            <li class="breadcrumb-item active" aria-current="page">Nueva</li>
          </ol>
        </nav>
        <div class="topbar-actions">
          <a href="#/instituciones" class="btn btn-light btn-sm">Cancelar</a>
          <button type="submit" form="formInstitucion" class="btn btn-primary btn-sm"><i class="bi bi-check-lg me-1"></i> Crear institución</button>
        </div>
      </header>

<main class="app-content">
        <div class="page-header">
          <div>
            <h1 class="page-title">Crear institución</h1>
            <p class="page-subtitle">Registra una nueva institución educativa en Numi.</p>
          </div>
        </div>

        <div class="row">
          <div class="col-xl-8">
            <form class="card needs-validation" id="formInstitucion" novalidate>
              <div class="card-header"><h2 class="card-title"><i class="bi bi-building me-2 text-primary"></i>Datos de la institución</h2></div>
              <div class="card-body p-4">
                <div class="row g-3">
                  <div class="col-12">
                    <label class="form-label" for="instNombre">Nombre de la institución</label>
                    <input type="text" class="form-control" id="instNombre" placeholder="Ej. IE Rural La Aldea" required>
                    <div class="invalid-feedback">Escribe el nombre de la institución.</div>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label" for="instComunaSel">Comuna o corregimiento</label>
                    <select class="form-select" id="instComunaSel" required>
                      <option value="" selected disabled>Selecciona una opción</option>
                      <option>San Cristóbal</option>
                      <option>Palmitas</option>
                      <option>Santa Elena</option>
                      <option>Altavista</option>
                      <option>San Antonio de Prado</option>
                    </select>
                    <div class="invalid-feedback">Elige una comuna o corregimiento.</div>
                  </div>
                  <div class="col-md-3">
                    <label class="form-label" for="instSedesNum">Número de sedes</label>
                    <input type="number" class="form-control" id="instSedesNum" min="1" value="1" required>
                  </div>
                  <div class="col-md-3">
                    <label class="form-label" for="instEstadoSel">Estado</label>
                    <select class="form-select" id="instEstadoSel">
                      <option selected>Activa</option>
                      <option>Inactiva</option>
                    </select>
                  </div>
                </div>
              </div>
            </form>
          </div>
          <div class="col-xl-4 mt-4 mt-xl-0">
            <div class="notice">
              <i class="bi bi-info-circle"></i>
              <div>Después de crearla podrás agregar sus grupos y asignar docentes desde <strong>Usuarios</strong>.</div>
            </div>
          </div>
        </div>
      </main>`;
}

export function mountInstitucionNuevaPage({ navigate }) {
  const form = $('#formInstitucion');
  const nombre = $('#instNombre');
  const avisoNombre = nombre.nextElementSibling;
  const textoOriginal = avisoNombre.textContent;
  nombre.addEventListener('input', () => {
    nombre.setCustomValidity('');
    avisoNombre.textContent = textoOriginal;
  });
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!form.checkValidity()) {
      form.classList.add('was-validated');
      return;
    }
    try {
      await crearInstitucion({
        nombre: nombre.value,
        comuna: $('#instComunaSel').value,
        sedes: $('#instSedesNum').value,
        estado: $('#instEstadoSel').value,
      });
      navigate('instituciones?msg=institucion');
    } catch (error) {
      if (error.status === 409) {
        nombre.setCustomValidity(error.message);
        avisoNombre.textContent = error.message;
        form.classList.add('was-validated');
      } else {
        mostrarError(error);
      }
    }
  });
}

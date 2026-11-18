import { Modal } from 'bootstrap';

import { eliminarActividad, getActividad } from '../api/actividades.api.js';
import { setStatus } from '../utils/badges.js';
import { $, $$ } from '../utils/dom.js';
import { mostrarError } from '../utils/toast.js';

export function ActividadDetallePage() {
  return `<header class="topbar">
        <button class="btn btn-light d-lg-none" type="button" data-bs-toggle="offcanvas" data-bs-target="#sidebar" aria-controls="sidebar" aria-label="Abrir menú"><i class="bi bi-list"></i></button>
        <a href="#/actividades" class="btn-back"><i class="bi bi-arrow-left"></i> Volver</a>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="#/inicio">Inicio</a></li>
            <li class="breadcrumb-item"><a href="#/actividades">Actividades</a></li>
            <li class="breadcrumb-item active" aria-current="page" data-act="nombre">Los números</li>
          </ol>
        </nav>
        <div class="topbar-actions">
          <button type="button" class="btn btn-outline-danger btn-sm" data-bs-toggle="modal" data-bs-target="#modalEliminar"><i class="bi bi-trash me-1"></i> Eliminar</button>
          <a href="#/constructor?id=los-numeros" class="btn btn-primary btn-sm" id="btnEditar"><i class="bi bi-pencil me-1"></i> Editar</a>
        </div>
      </header>

<main class="app-content">
        <div class="page-header">
          <div>
            <div class="d-flex align-items-center gap-2 flex-wrap">
              <h1 class="page-title" data-act="nombre">Los números</h1>
              <span class="status status-success" data-act="estadoBadge">Publicada</span>
            </div>
            <p class="page-subtitle">Detalle de la actividad</p>
          </div>
        </div>

        <div class="row g-4">
          <div class="col-lg-7">
            <div class="card">
              <div class="card-header"><h2 class="card-title">Información general</h2></div>
              <div class="card-body p-4">
                <dl class="row detail-list">
                  <dt class="col-sm-5">Materia</dt>
                  <dd class="col-sm-7" data-act="materia">Matemáticas</dd>
                  <dt class="col-sm-5">Grado</dt>
                  <dd class="col-sm-7" data-act="grado">1°</dd>
                  <dt class="col-sm-5">Tipo de actividad</dt>
                  <dd class="col-sm-7" data-act="tipo">Arrastrar y soltar</dd>
                  <dt class="col-sm-5">Veces resuelta</dt>
                  <dd class="col-sm-7" data-act="resuelta">612</dd>
                  <dt class="col-sm-5">Estado</dt>
                  <dd class="col-sm-7 mb-0" data-act="estado">Publicada</dd>
                </dl>
              </div>
            </div>
          </div>
          <div class="col-lg-5">
            <div class="notice mb-3">
              <i class="bi bi-pencil-square"></i>
              <div>Las preguntas y los recursos de la actividad se editan con el botón <strong>Editar</strong>.</div>
            </div>
            <div class="notice">
              <i class="bi bi-phone"></i>
              <div>Los cambios llegan al celular del niño en su próxima sincronización, no de inmediato.</div>
            </div>
          </div>
        </div>
      </main>

<div class="modal fade" id="modalEliminar" tabindex="-1" aria-labelledby="modalEliminarTitulo" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-body text-center p-4">
          <div class="danger-icon"><i class="bi bi-exclamation-lg"></i></div>
          <h2 class="h5 fw-bold" id="modalEliminarTitulo">¿Eliminar «<span data-act="nombre">Los números</span>»?</h2>
          <p class="text-secondary mb-0">La actividad sale de la lista y deja de estar disponible en el celular del niño en su próxima sincronización. Queda registrada en el Historial.</p>
        </div>
        <div class="modal-footer justify-content-center border-0 pt-0 pb-4">
          <button type="button" class="btn btn-light" data-bs-dismiss="modal">Cancelar</button>
          <a href="#/actividades?eliminada=los-numeros" class="btn btn-danger" id="btnConfirmarEliminar">Eliminar</a>
        </div>
      </div>
    </div>
  </div>`;
}

export async function mountActividadDetallePage({ navigate, query }) {
  const id = query.get('id');
  if (!id) return navigate('actividades');
  let act;
  try {
    act = await getActividad(id);
  } catch {
    return navigate('actividades');
  }
  $$('[data-act]').forEach((nodo) => {
    const key = nodo.dataset.act;
    if (key === 'estadoBadge') setStatus(nodo, act.estado);
    else nodo.textContent = act[key];
  });
  $('#btnEditar').href = `#/constructor?id=${encodeURIComponent(act.id)}`;

  const confirmar = $('#btnConfirmarEliminar');
  confirmar.href = '#';
  confirmar.addEventListener('click', async (e) => {
    e.preventDefault();
    confirmar.classList.add('disabled');
    try {
      const eliminada = await eliminarActividad(act.id);
      navigate(`actividades?eliminada=${encodeURIComponent(eliminada.nombre)}`);
    } catch (error) {
      Modal.getInstance('#modalEliminar')?.hide();
      mostrarError(error);
      confirmar.classList.remove('disabled');
    }
  });
}

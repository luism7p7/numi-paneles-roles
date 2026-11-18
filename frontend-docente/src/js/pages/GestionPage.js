import { actualizarPaquete, cambiarIa, getGestion, nuevoCodigo } from '../api/gestion.api.js';
import { pintarGrupo } from '../components/layout/Layout.js';
import { grupo } from '../state/docente.store.js';
import { $ } from '../utils/dom.js';
import { mostrarError, showToast } from '../utils/toast.js';

export function GestionPage() {
  return `<div class="section-bar">
        <a href="#/panel" class="btn-back"><i class="bi bi-arrow-left"></i> Volver</a>
        <h2 class="section-title">Gestión del grupo</h2>
      </div>

<main class="app-content">
        <div class="row g-4">
          <!-- Código del grupo -->
          <div class="col-lg-6">
            <div class="card h-100">
              <div class="card-header"><h3 class="card-title">Código del grupo <span data-group="corto">3° A</span></h3></div>
              <div class="card-body p-4">
                <div class="code-box mb-3">
                  <div class="code-value" id="codigoGrupo" data-group="codigo">7K4M-92</div>
                  <div class="small text-secondary fw-bold mt-1">Vence el 15 de septiembre · <span id="usosCodigo">18 de 30 usos disponibles</span></div>
                </div>
                <div class="d-flex gap-2 flex-wrap">
                  <button type="button" class="btn btn-primary flex-fill" id="btnCopiar"><i class="bi bi-clipboard me-1"></i> Copiar código</button>
                  <button type="button" class="btn btn-outline-primary flex-fill" id="btnNuevoCodigo"><i class="bi bi-arrow-repeat me-1"></i> Generar uno nuevo</button>
                </div>
              </div>
            </div>
          </div>

          <!-- Cómo lo usa el estudiante -->
          <div class="col-lg-6">
            <div class="card h-100">
              <div class="card-header"><h3 class="card-title">Cómo lo usa el estudiante</h3></div>
              <div class="card-body p-4">
                <div class="step"><span class="step-num">1</span><div>Abre Numi en el celular y entra a su perfil.</div></div>
                <div class="step"><span class="step-num">2</span><div>Toca <strong>“Unirme a un grupo”</strong> y escribe el código.</div></div>
                <div class="step"><span class="step-num">3</span><div>Necesita internet solo en este paso. Después vuelve a funcionar <strong>offline</strong>.</div></div>
              </div>
            </div>
          </div>

          <!-- Configuración -->
          <div class="col-12">
            <div class="card">
              <div class="card-header"><h3 class="card-title">Configuración</h3></div>
              <div class="setting-row">
                <span class="stat-top m-0"><i class="bi bi-robot icon-teal"></i></span>
                <div class="flex-grow-1">
                  <div class="fw-bold">Asistente de IA</div>
                  <div class="cell-sub">Disponible para 3°, 4° y 5°</div>
                </div>
                <div class="form-check form-switch mb-0 d-flex align-items-center gap-2">
                  <input class="form-check-input" type="checkbox" role="switch" id="switchIA" checked>
                  <label class="form-check-label small fw-bold" for="switchIA" id="labelIA">Activado</label>
                </div>
              </div>
              <div class="setting-row">
                <span class="stat-top m-0"><i class="bi bi-box-seam icon-sky"></i></span>
                <div class="flex-grow-1">
                  <div class="fw-bold">Paquete de conocimiento</div>
                  <div class="cell-sub" id="paqueteInfo">v2.1 · 340 MB · actualizado el 12 de agosto</div>
                </div>
                <button type="button" class="btn btn-soft btn-sm" id="btnActualizar"><i class="bi bi-arrow-clockwise me-1"></i> Actualizar</button>
              </div>
            </div>
          </div>
        </div>
      </main>`;
}

function pintarGestion(datos) {
  $('#codigoGrupo').textContent = datos.codigo;
  $('#usosCodigo').textContent = datos.usos;
  $('#usosCodigo').parentElement.firstChild.textContent = `${datos.vence} · `;
  $('#switchIA').checked = datos.ia;
  $('#switchIA').disabled = !datos.ia_disponible && !datos.ia;
  $('#labelIA').textContent = datos.ia ? 'Activado' : 'Desactivado';
  $('#paqueteInfo').textContent = datos.paquete;
  grupo().codigo = datos.codigo;
  pintarGrupo(); // el código también se ve en la ventana de perfil
}

export async function mountGestionPage() {
  $('#btnCopiar').addEventListener('click', () => {
    const codigo = $('#codigoGrupo').textContent;
    const listo = () => showToast(`Código ${codigo} copiado.`);
    if (navigator.clipboard) navigator.clipboard.writeText(codigo).then(listo, listo);
    else listo();
  });

  $('#btnNuevoCodigo').addEventListener('click', async () => {
    try {
      pintarGestion(await nuevoCodigo());
    } catch (error) {
      return mostrarError(error);
    }
    showToast('Se generó un código nuevo. El anterior deja de funcionar.');
  });

  $('#switchIA').addEventListener('change', async (e) => {
    const activada = e.target.checked;
    try {
      pintarGestion(await cambiarIa(activada));
    } catch (error) {
      e.target.checked = !activada;
      return mostrarError(error);
    }
    showToast(activada ? 'Asistente de IA activado para el grupo.' : 'Asistente de IA desactivado para el grupo.');
  });

  $('#btnActualizar').addEventListener('click', async (e) => {
    const boton = e.currentTarget;
    boton.disabled = true;
    boton.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Actualizando';
    try {
      pintarGestion(await actualizarPaquete());
      showToast('El paquete de conocimiento ya está al día.');
    } catch (error) {
      mostrarError(error);
    } finally {
      boton.disabled = false;
      boton.innerHTML = '<i class="bi bi-arrow-clockwise me-1"></i> Actualizar';
    }
  });

  try {
    pintarGestion(await getGestion());
  } catch (error) {
    mostrarError(error);
  }
}

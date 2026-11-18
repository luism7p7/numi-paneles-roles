import { getPanel } from '../api/seguimiento.api.js';
import { $, $$, el, iniciales } from '../utils/dom.js';
import { mostrarError } from '../utils/toast.js';

export function PanelPage() {
  return `<div class="section-bar">
        <h2 class="section-title">Panel</h2>
      </div>

<main class="app-content">
        <!-- Indicadores -->
        <div class="row g-3 mb-4">
          <div class="col-6 col-xl-3">
            <div class="card stat-card">
              <div class="stat-top">Activos esta semana <i class="bi bi-lightning-charge icon-teal"></i></div>
              <div class="stat-value" id="statActivos">—</div>
            </div>
          </div>
          <div class="col-6 col-xl-3">
            <div class="card stat-card">
              <div class="stat-top">Sin conexión +7 días <i class="bi bi-wifi-off icon-rose"></i></div>
              <div class="stat-value" id="statSinConexion">—</div>
            </div>
          </div>
          <div class="col-6 col-xl-3">
            <div class="card stat-card">
              <div class="stat-top">Racha promedio <i class="bi bi-fire icon-amber"></i></div>
              <div class="stat-value" id="statRacha">—</div>
            </div>
          </div>
          <div class="col-6 col-xl-3">
            <div class="card stat-card">
              <div class="stat-top">Avance promedio <i class="bi bi-graph-up icon-sky"></i></div>
              <div class="stat-value" id="statAvance">—</div>
            </div>
          </div>
        </div>

        <div class="row g-4 mb-4">
          <!-- Avance por materia -->
          <div class="col-lg-7">
            <div class="card h-100">
              <div class="card-header"><h3 class="card-title">Avance por materia</h3></div>
              <div class="card-body p-4">
                <div class="row align-items-center g-4">
                  <div class="col-sm-4 text-center">
                    <div class="ring" id="ringAvance" style="--value: 0"><span>—</span></div>
                    <div class="small text-secondary fw-bold mt-2">Promedio del grupo</div>
                  </div>
                  <div class="col-sm-8" id="materias">
                    <div class="subject-row">
                      <div class="d-flex justify-content-between small fw-bold mb-1"><span>Matemáticas</span><span data-val>—</span></div>
                      <div class="progress"><div class="progress-bar bar-mat" style="width: 0%"></div></div>
                    </div>
                    <div class="subject-row">
                      <div class="d-flex justify-content-between small fw-bold mb-1"><span>Ciencias</span><span data-val>—</span></div>
                      <div class="progress"><div class="progress-bar bar-cie" style="width: 0%"></div></div>
                    </div>
                    <div class="subject-row">
                      <div class="d-flex justify-content-between small fw-bold mb-1"><span>Español</span><span data-val>—</span></div>
                      <div class="progress"><div class="progress-bar bar-esp" style="width: 0%"></div></div>
                    </div>
                    <div class="subject-row">
                      <div class="d-flex justify-content-between small fw-bold mb-1"><span>Sociales</span><span data-val>—</span></div>
                      <div class="progress"><div class="progress-bar bar-soc" style="width: 0%"></div></div>
                    </div>
                    <div class="subject-row">
                      <div class="d-flex justify-content-between small fw-bold mb-1"><span>Inglés</span><span data-val>—</span></div>
                      <div class="progress"><div class="progress-bar bar-ing" style="width: 0%"></div></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Requieren atención -->
          <div class="col-lg-5">
            <div class="card h-100">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h3 class="card-title">Requieren atención</h3>
                <a href="#/estudiantes" class="small fw-bold text-decoration-none">Ver todos <i class="bi bi-arrow-right"></i></a>
              </div>
              <div id="atencion">
                <div class="attention-item">
                  <span class="avatar">SR</span>
                  <div class="flex-grow-1"><div class="fw-bold">Samuel Ríos</div><div class="cell-sub">12 días sin entrar</div></div>
                  <span class="status status-danger">Inactivo</span>
                </div>
                <div class="attention-item">
                  <span class="avatar">MO</span>
                  <div class="flex-grow-1"><div class="fw-bold">Mariana Ospina</div><div class="cell-sub">Inglés en 18%</div></div>
                  <span class="status status-warning">Bajo avance</span>
                </div>
                <div class="attention-item">
                  <span class="avatar">KZ</span>
                  <div class="flex-grow-1"><div class="fw-bold">Kevin Zapata</div><div class="cell-sub">Sin sincronizar</div></div>
                  <span class="status status-info">Sincronizar</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Acciones rápidas -->
        <div class="card">
          <div class="card-header"><h3 class="card-title">Acciones rápidas</h3></div>
          <div class="card-body">
            <div class="row g-3">
              <div class="col-6 col-xl-3"><a href="#/estudiantes" class="quick-link"><i class="bi bi-people"></i> Ver estudiantes</a></div>
              <div class="col-6 col-xl-3"><a href="#/actividades" class="quick-link"><i class="bi bi-puzzle"></i> Revisar actividades</a></div>
              <div class="col-6 col-xl-3"><a href="#/reportes?generar=1" class="quick-link"><i class="bi bi-file-earmark-arrow-down"></i> Generar reporte</a></div>
              <div class="col-6 col-xl-3"><a href="#/gestion" class="quick-link"><i class="bi bi-qr-code"></i> Código del grupo</a></div>
            </div>
          </div>
        </div>
      </main>`;
}

export async function mountPanelPage() {
  let datos;
  try {
    datos = await getPanel();
  } catch (error) {
    return mostrarError(error);
  }
  $('#statActivos').textContent = datos.activos;
  $('#statSinConexion').textContent = datos.sin_conexion;
  $('#statRacha').textContent = datos.racha;
  $('#statAvance').textContent = `${datos.avance}%`;
  const anillo = $('#ringAvance');
  anillo.style.setProperty('--value', datos.avance);
  $('span', anillo).textContent = `${datos.avance}%`;

  $$('#materias .subject-row').forEach((fila, i) => {
    $('[data-val]', fila).textContent = `${datos.materias[i]}%`;
    $('.progress-bar', fila).style.width = `${datos.materias[i]}%`;
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

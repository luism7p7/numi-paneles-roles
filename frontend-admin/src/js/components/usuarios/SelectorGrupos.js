// "Grupos a cargo" dentro de los modales Crear / Editar usuario (el HTML no lo trae).
// Muestra los grupos de la institución elegida y permite crear uno nuevo.
import { crearGrupo, getInstitucion } from '../../api/instituciones.api.js';
import { $, $$, el } from '../../utils/dom.js';
import { mostrarError, showToast } from '../../utils/toast.js';

export function crearSelectorGrupos(modal, selectRol, selectInst, instituciones) {
  const bloque = el('div', 'mt-3');
  bloque.innerHTML = `
    <label class="form-label">Grupos a cargo</label>
    <p class="small text-secondary mb-2">Marca los grados y grupos que manejará el docente. Puede tener varios.</p>
    <div class="d-grid gap-1 mb-2" data-lista></div>
    <div class="d-flex gap-2 align-items-center flex-wrap">
      <select class="form-select form-select-sm w-auto" aria-label="Grado del grupo nuevo" data-grado>
        ${[1, 2, 3, 4, 5].map((g) => `<option value="${g}">Grado ${g}°</option>`).join('')}
      </select>
      <select class="form-select form-select-sm w-auto" aria-label="Letra del grupo nuevo" data-letra>
        ${'ABCDEFGH'
          .split('')
          .map((l) => `<option>${l}</option>`)
          .join('')}
      </select>
      <button type="button" class="btn btn-sm btn-soft" data-crear><i class="bi bi-plus-lg me-1"></i>Crear grupo</button>
    </div>`;
  $('.modal-body', modal).appendChild(bloque);
  const lista = $('[data-lista]', bloque);
  let usuarioId = null;
  let grupos = [];

  const institucionId = () => instituciones().find((i) => i.nombre === selectInst.value)?.id;
  const marcados = () => $$('input[type="checkbox"]:checked', lista).map((cb) => Number(cb.value));
  const visible = () => selectRol.value === 'Docente' && Boolean(institucionId());

  const pintar = (seleccion) => {
    lista.replaceChildren();
    if (!grupos.length) lista.appendChild(el('span', 'small text-secondary', 'Esta institución todavía no tiene grupos: crea uno abajo.'));
    grupos.forEach((g) => {
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
    try {
      grupos = (await getInstitucion(institucionId())).grupos;
    } catch {
      grupos = [];
    }
    pintar(seleccion);
  };

  $('[data-crear]', bloque).addEventListener('click', async () => {
    try {
      const grupo = await crearGrupo(institucionId(), { grado: $('[data-grado]', bloque).value, letra: $('[data-letra]', bloque).value });
      showToast(`Se creó el grupo ${grupo.corto}.`);
      await cargar([...marcados(), grupo.id]);
    } catch (error) {
      mostrarError(error);
    }
  });
  selectRol.addEventListener('change', () => cargar(marcados()));
  selectInst.addEventListener('change', () => cargar([]));

  return {
    abrir: (id, seleccion) => {
      usuarioId = id;
      return cargar(seleccion);
    },
    ids: () => (visible() ? marcados() : []),
  };
}

// Filtros y paginación de las tablas. Un formulario con `data-table-filter="#tabla"` filtra las filas de esa tabla.
import { POR_PAGINA } from '../../utils/constantes.js';
import { $, $$, el } from '../../utils/dom.js';

export function dibujarPaginacion(ul, actual, total, irA) {
  ul.replaceChildren();
  const item = (texto, pagina, { activo = false, deshabilitado = false } = {}) => {
    const li = el('li', `page-item${activo ? ' active' : ''}${deshabilitado ? ' disabled' : ''}`);
    const a = el('a', 'page-link', texto);
    a.href = '#';
    a.addEventListener('click', (e) => {
      e.preventDefault();
      if (!activo && !deshabilitado) irA(pagina);
    });
    li.appendChild(a);
    return li;
  };
  ul.appendChild(item('Anterior', actual - 1, { deshabilitado: actual === 1 }));
  for (let p = 1; p <= total; p++) ul.appendChild(item(String(p), p, { activo: p === actual }));
  ul.appendChild(item('Siguiente', actual + 1, { deshabilitado: actual === total }));
}

// Muestra solo la página actual de las filas que cumplen los filtros. Devuelve cuántas quedan visibles.
export function paginar(todas, coinciden, ul, estado, redibujar) {
  let visibles = coinciden;
  if (ul) {
    const paginas = Math.max(1, Math.ceil(coinciden.length / POR_PAGINA));
    estado.pagina = Math.min(Math.max(1, estado.pagina), paginas);
    const inicio = (estado.pagina - 1) * POR_PAGINA;
    visibles = coinciden.slice(inicio, inicio + POR_PAGINA);
    dibujarPaginacion(ul, estado.pagina, paginas, (p) => {
      estado.pagina = p;
      redibujar();
    });
  }
  todas.forEach((fila) => fila.classList.toggle('d-none', !visibles.includes(fila)));
  return visibles.length;
}

// Conecta cada formulario de filtro de la pantalla con su tabla. Se llama una vez cuando la pantalla ya está dibujada.
export function activarFiltrosDeTablas() {
  $$('[data-table-filter]').forEach((form) => {
    const table = $(form.dataset.tableFilter);
    if (!table) return;
    const card = table.closest('.card');
    const counter = $('[data-visible]', card);
    const paginacion = $('.pagination', card);
    const estado = { pagina: 1 };

    const cumple = (row, ctrl) => {
      const value = ctrl.value.trim().toLowerCase();
      if (!value) return true;
      const filtro = ctrl.dataset.filter;
      if (filtro === 'text') return row.textContent.toLowerCase().includes(value);
      if (filtro === 'desde') return (row.dataset.dia || '') >= value;
      if (filtro === 'hasta') return (row.dataset.dia || '') <= value;
      return (row.dataset[filtro] || '').toLowerCase() === value;
    };

    const apply = (reiniciar = true) => {
      if (reiniciar) estado.pagina = 1;
      const filas = $$('tbody tr', table).filter((row) => !row.dataset.vacia);
      const controles = $$('[data-filter]', form);
      const coinciden = filas.filter((row) => controles.every((ctrl) => cumple(row, ctrl)));
      const visibles = paginar(filas, coinciden, paginacion, estado, () => apply(false));
      if (counter) counter.textContent = visibles;
    };

    form.addEventListener('input', () => apply());
    form.addEventListener('submit', (e) => e.preventDefault());
    form.applyFilters = apply;
  });
}

export function aplicarFiltros(tabla, reiniciar = true) {
  const form = $(`[data-table-filter="${tabla}"]`);
  if (form) form.applyFilters(reiniciar);
}

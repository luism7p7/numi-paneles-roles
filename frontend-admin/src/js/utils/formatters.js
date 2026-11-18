import { el } from './dom.js';

export function plural(n, singular, varios) {
  return `${n} ${n === 1 ? singular : varios}`;
}

export function fechaISO(fecha) {
  const dos = (n) => String(n).padStart(2, '0');
  return `${fecha.getFullYear()}-${dos(fecha.getMonth() + 1)}-${dos(fecha.getDate())}`;
}

// Cambia el total en textos como "<span data-visible>4</span> de 7 instituciones"
export function fijarTotal(contador, total, nombre) {
  if (contador) contador.parentElement.lastChild.textContent = ` de ${total} ${nombre}`;
}

export function filaVacia(tbody, columnas, texto) {
  const tr = el('tr');
  tr.dataset.vacia = 'true';
  const td = el('td', 'text-center text-secondary py-4', texto);
  td.colSpan = columnas;
  tr.appendChild(td);
  tbody.appendChild(tr);
}

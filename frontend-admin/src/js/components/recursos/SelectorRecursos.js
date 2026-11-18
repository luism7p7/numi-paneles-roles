// Ventana con buscador, filtros por materia y miniaturas grandes para elegir de TODO el catálogo.
// Tiene dos modos: elegirUno (un campo del contenido de la actividad) y elegirVarios (los recursos de la actividad).
import { Modal } from 'bootstrap';

import { el, icono } from '../../utils/dom.js';
import { plural } from '../../utils/formatters.js';
import { showToast } from '../../utils/toast.js';

const ETIQUETAS_CARPETA = {
  'actividades/matematicas': 'Matemáticas',
  'actividades/espanol': 'Español',
  'actividades/ciencias': 'Ciencias naturales',
  'actividades/sociales': 'Sociales',
  'actividades/ingles': 'Inglés',
  'app/general': 'General de la app',
};

export function etiquetaCarpeta(carpeta) {
  const nombre = ETIQUETAS_CARPETA[carpeta] || carpeta.replace(/^actividades\//, '');
  return nombre.charAt(0).toUpperCase() + nombre.slice(1);
}

// "Botón_doméstico (1).png" → "boton domestico 1 png": se busca sin tildes, mayúsculas ni símbolos
function paraBuscar(texto) {
  return texto
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, ' ')
    .trim();
}

export function crearSelectorRecursos(catalogo) {
  const POR_TANDA = 60;
  const indice = catalogo.map((r) => ({ r, clave: paraBuscar(`${r.nombre} ${etiquetaCarpeta(r.carpeta)} ${r.tipo}`) }));
  const carpetas = [...new Set(catalogo.map((r) => r.carpeta))];
  const e = {
    modo: 'uno',
    tipo: '',
    tipoFijo: false,
    carpeta: '',
    limite: POR_TANDA,
    materia: '',
    actual: null,
    seleccion: new Map(),
    alElegir: null,
    alCambiar: null,
  };
  let reproductor = null;

  // --- Estructura de la ventana
  const modal = el('div', 'modal fade');
  modal.tabIndex = -1;
  modal.setAttribute('aria-hidden', 'true');
  const contenido = el('div', 'modal-content');
  modal.appendChild(el('div', 'modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable')).appendChild(contenido);

  const cabecera = el('div', 'modal-header');
  const titulos = el('div');
  const titulo = el('h2', 'modal-title fs-5');
  const subtitulo = el('p', 'small text-secondary mb-0');
  titulos.append(titulo, subtitulo);
  const cerrar = el('button', 'btn-close');
  cerrar.type = 'button';
  cerrar.setAttribute('data-bs-dismiss', 'modal');
  cerrar.setAttribute('aria-label', 'Cerrar');
  cabecera.append(titulos, cerrar);

  const cuerpo = el('div', 'modal-body');
  const barra = el('div', 'picker-barra');
  const fila = el('div', 'picker-fila');
  const caja = el('div', 'picker-busqueda');
  const buscador = el('input', 'form-control');
  buscador.type = 'search';
  buscador.placeholder = 'Buscar por nombre: perro, cocodrilo, pantalla 3…';
  buscador.setAttribute('aria-label', 'Buscar recurso');
  caja.append(icono('bi-search'), buscador);
  const grupoTipos = el('div', 'btn-group');
  grupoTipos.setAttribute('role', 'group');
  const botonesTipo = [
    ['', 'Todo'],
    ['Imagen', 'Imágenes'],
    ['Audio', 'Audios'],
  ].map(([valor, texto]) => {
    const boton = el('button', 'btn btn-sm', texto);
    boton.type = 'button';
    boton.dataset.valor = valor;
    boton.addEventListener('click', () => {
      e.tipo = valor;
      e.limite = POR_TANDA;
      pintar();
    });
    return boton;
  });
  grupoTipos.append(...botonesTipo);
  fila.append(caja, grupoTipos);
  const chips = el('div', 'picker-chips');
  barra.append(fila, chips);
  const rejilla = el('div', 'picker-grid');
  const pie = el('div', 'picker-pie');
  cuerpo.append(barra, rejilla, pie);

  const piePie = el('div', 'modal-footer');
  const contador = el('span', 'me-auto small text-secondary');
  const quitar = el('button', 'btn btn-outline-danger');
  quitar.type = 'button';
  const listo = el('button', 'btn');
  listo.type = 'button';
  listo.setAttribute('data-bs-dismiss', 'modal');
  piePie.append(contador, quitar, listo);

  contenido.append(cabecera, cuerpo, piePie);
  document.body.appendChild(modal);
  const ventana = new Modal(modal);

  // --- Acciones
  const escuchar = (recurso) => {
    reproductor?.pause();
    reproductor = new Audio(recurso.url);
    reproductor.play().catch(() => showToast('No se pudo reproducir el audio.'));
  };

  const elegir = (recurso) => {
    if (e.modo === 'uno') {
      e.alElegir(recurso.id);
      ventana.hide();
      return;
    }
    const clave = String(recurso.id);
    if (e.seleccion.has(clave)) e.seleccion.delete(clave);
    else e.seleccion.set(clave, recurso);
    e.alCambiar();
    pintar();
  };

  const tarjeta = (recurso) => {
    const elegido = e.modo === 'varios' ? e.seleccion.has(String(recurso.id)) : recurso.id === e.actual;
    const nodo = el('div', `picker-card${elegido ? ' is-selected' : ''}${recurso.compatible ? '' : ' is-disabled'}`);
    nodo.setAttribute('role', 'button');
    nodo.tabIndex = recurso.compatible ? 0 : -1;
    nodo.title = recurso.compatible
      ? recurso.nombre
      : `Disponible desde la v${recurso.version_minima}: ${recurso.equipos_incompatibles} equipos no lo mostrarían`;

    const vista = el('div', 'picker-thumb');
    if (recurso.tipo === 'Imagen' && recurso.url) {
      const img = el('img');
      img.src = recurso.url;
      img.alt = '';
      img.loading = 'lazy';
      vista.appendChild(img);
    } else {
      vista.appendChild(icono(recurso.tipo === 'Audio' ? 'bi-music-note-beamed' : recurso.tipo === 'Video' ? 'bi-film' : 'bi-image'));
    }
    if (recurso.tipo === 'Audio' && recurso.url) {
      const play = el('button', 'picker-play');
      play.type = 'button';
      play.title = 'Escuchar';
      play.setAttribute('aria-label', `Escuchar ${recurso.nombre}`);
      play.appendChild(icono('bi-play-fill'));
      play.addEventListener('click', (ev) => {
        ev.stopPropagation();
        escuchar(recurso);
      });
      vista.appendChild(play);
    }
    const marca = el('span', 'picker-check');
    marca.appendChild(icono('bi-check-lg'));

    const partes = recurso.nombre.split('/');
    const ruta = [etiquetaCarpeta(recurso.carpeta), ...partes.slice(0, -1)].join(' › ');
    nodo.append(vista, marca, el('div', 'picker-nombre', partes.at(-1)), el('div', 'picker-ruta', ruta));
    if (recurso.compatible) {
      nodo.addEventListener('click', () => elegir(recurso));
      nodo.addEventListener('keydown', (ev) => {
        if (ev.key === 'Enter' || ev.key === ' ') {
          ev.preventDefault();
          elegir(recurso);
        }
      });
    }
    return nodo;
  };

  const chip = (valor, texto) => {
    const boton = el('button', `btn btn-sm rounded-pill ${e.carpeta === valor ? 'btn-primary' : 'btn-outline-secondary'}`, texto);
    boton.type = 'button';
    boton.addEventListener('click', () => {
      e.carpeta = valor;
      e.limite = POR_TANDA;
      pintar();
    });
    return boton;
  };

  function pintar() {
    const terminos = paraBuscar(buscador.value).split(' ').filter(Boolean);
    const coincide = (x) => (!e.tipo || x.r.tipo === e.tipo) && terminos.every((t) => x.clave.includes(t));
    const base = indice.filter(coincide);
    const lista = base.filter((x) => !e.carpeta || x.r.carpeta === e.carpeta);
    // Primero lo de la materia de la actividad, luego el resto en orden
    const prioridad = (r) => (r.carpeta === e.materia ? 0 : 1);
    const ordenTipo = { Imagen: 0, Audio: 1, Video: 2 };
    lista.sort(
      (a, b) =>
        prioridad(a.r) - prioridad(b.r) ||
        a.r.carpeta.localeCompare(b.r.carpeta) ||
        ordenTipo[a.r.tipo] - ordenTipo[b.r.tipo] ||
        a.r.nombre.localeCompare(b.r.nombre, 'es', { numeric: true }),
    );

    botonesTipo.forEach((b) => {
      b.className = `btn btn-sm ${b.dataset.valor === e.tipo ? 'btn-primary' : 'btn-outline-primary'}`;
    });
    grupoTipos.classList.toggle('d-none', e.tipoFijo);

    const cuenta = (c) => base.filter((x) => x.r.carpeta === c).length;
    const ordenadas = [...carpetas].sort(
      (a, b) => prioridad({ carpeta: a }) - prioridad({ carpeta: b }) || etiquetaCarpeta(a).localeCompare(etiquetaCarpeta(b), 'es'),
    );
    chips.replaceChildren(
      chip('', `Todas (${base.length})`),
      ...ordenadas.filter((c) => cuenta(c) || c === e.carpeta).map((c) => chip(c, `${etiquetaCarpeta(c)} (${cuenta(c)})`)),
    );

    const visibles = lista.slice(0, e.limite);
    rejilla.replaceChildren(...visibles.map((x) => tarjeta(x.r)));
    if (!lista.length) {
      const vacio = el('p', 'text-secondary mb-0', 'No hay recursos con esa búsqueda. Prueba con otra palabra o quita los filtros.');
      vacio.style.gridColumn = '1 / -1';
      rejilla.appendChild(vacio);
    }

    pie.replaceChildren(el('span', '', `Mostrando ${visibles.length} de ${plural(lista.length, 'recurso', 'recursos')}`));
    if (lista.length > visibles.length) {
      const mas = el('button', 'btn btn-sm btn-soft', `Mostrar ${Math.min(POR_TANDA, lista.length - visibles.length)} más`);
      mas.type = 'button';
      mas.addEventListener('click', () => {
        e.limite += POR_TANDA;
        pintar();
      });
      pie.appendChild(mas);
    }
    contador.textContent = e.modo === 'varios' ? `${plural(e.seleccion.size, 'seleccionado', 'seleccionados')}` : '';
  }

  let consulta;
  buscador.addEventListener('input', () => {
    clearTimeout(consulta);
    consulta = setTimeout(() => {
      e.limite = POR_TANDA;
      pintar();
    }, 120);
  });
  quitar.addEventListener('click', () => {
    e.alElegir(null);
    ventana.hide();
  });
  modal.addEventListener('shown.bs.modal', () => buscador.focus());
  modal.addEventListener('hidden.bs.modal', () => reproductor?.pause());

  const abrir = (datos) => {
    Object.assign(e, { carpeta: '', limite: POR_TANDA }, datos);
    buscador.value = '';
    pintar();
    ventana.show();
  };

  return {
    // Un campo del contenido: toca un recurso y la ventana se cierra
    elegirUno({ tipo, actual, materia, alElegir }) {
      const que = tipo === 'Audio' ? 'audio' : 'imagen';
      titulo.textContent = `Elegir ${que}`;
      subtitulo.textContent = 'Busca por nombre y toca el recurso que quieres usar.';
      quitar.textContent = `Quitar ${que}`;
      quitar.classList.toggle('d-none', actual == null);
      listo.className = 'btn btn-light';
      listo.textContent = 'Cancelar';
      abrir({ modo: 'uno', tipo, tipoFijo: true, actual, materia, alElegir });
    },
    // Los recursos de la actividad: se marcan varios y cada cambio se avisa al momento
    elegirVarios({ seleccion, materia, alCambiar }) {
      titulo.textContent = 'Agregar recursos';
      subtitulo.textContent = 'Marca los que quieras. Los que uses en el contenido se agregan solos.';
      quitar.classList.add('d-none');
      listo.className = 'btn btn-primary';
      listo.textContent = 'Listo';
      abrir({ modo: 'varios', tipo: '', tipoFijo: false, seleccion, materia, alCambiar });
    },
    // Al salir de la pantalla: la ventana vive en <body>, así que hay que quitarla
    destruir() {
      reproductor?.pause();
      ventana.dispose();
      modal.remove();
    },
  };
}

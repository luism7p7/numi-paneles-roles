// Editor del contenido de una actividad: una plantilla por tipo (preguntas, grupos, parejas, sílabas, pares).
// El formato de cada contenido está documentado en api/app/dominios/actividades/plantillas.py.
import { CARPETA_MATERIA } from '../../utils/constantes.js';
import { $, el, icono } from '../../utils/dom.js';
import { plural } from '../../utils/formatters.js';
import { miniatura } from '../recursos/Miniatura.js';

const MAX_OPCIONES = 4;
const MAX_GRUPOS = 4;
const MAX_ELEMENTOS = 12;
const MAX_PAREJAS = 6;
const MAX_PALABRAS = 10;
const MAX_PARES = 8;

// Controles compartidos por los editores. `ctx` trae el catálogo de recursos y el selector.
function crearControles(ctx) {
  const carpetaActual = () => `actividades/${CARPETA_MATERIA[$('#actMateria').value]}`;
  // Botón que muestra el recurso elegido y abre el selector con buscador (todas las carpetas)
  const campoRecurso = (objeto, clave, tipo, vacio, ancho) => {
    const boton = el('button', 'btn btn-sm btn-outline-secondary picker-campo');
    boton.type = 'button';
    boton.style.width = ancho;
    const vista = el('span', 'thumb-sm flex-shrink-0');
    const nombre = el('span', 'text-truncate flex-grow-1');
    boton.append(vista, nombre, icono('bi-search small'));
    const pintar = () => {
      const recurso = ctx.catalogo.find((r) => r.id === objeto[clave]);
      vista.replaceChildren(...(recurso ? miniatura(recurso, 'thumb-sm').childNodes : []));
      nombre.textContent = recurso ? recurso.nombre.split('/').pop() : vacio;
      nombre.classList.toggle('text-secondary', !recurso);
    };
    boton.addEventListener('click', () =>
      ctx.selector.elegirUno({
        tipo,
        actual: objeto[clave] ?? null,
        materia: carpetaActual(),
        alElegir: (id) => {
          objeto[clave] = id;
          pintar();
        },
      }),
    );
    pintar();
    return boton;
  };
  const texto = (objeto, clave, marcador, maximo, clases = 'form-control form-control-sm') => {
    const input = el('input', clases);
    input.maxLength = maximo;
    input.placeholder = marcador;
    input.value = objeto[clave] || '';
    // Los campos pequeños van en filas flexibles: se estiran y los selectores conservan su ancho
    if (clases.includes('form-control-sm')) Object.assign(input.style, { flex: '1 1 130px', width: 'auto', minWidth: '110px' });
    input.addEventListener('input', () => {
      objeto[clave] = input.value;
    });
    return input;
  };
  const imagen = (objeto, clave = 'imagen', vacio = 'Sin imagen') => campoRecurso(objeto, clave, 'Imagen', vacio, '200px');
  const audio = (objeto, vacio) => campoRecurso(objeto, 'audio', 'Audio', vacio, '100%');
  const quitar = (etiqueta, accion, deshabilitado = false) => {
    const boton = el('button', 'btn btn-sm btn-light');
    boton.type = 'button';
    boton.setAttribute('aria-label', etiqueta);
    boton.title = etiqueta;
    boton.appendChild(icono('bi-x-lg'));
    boton.disabled = deshabilitado;
    boton.addEventListener('click', accion);
    return boton;
  };
  const boton = (etiqueta, accion, clases = 'btn btn-sm btn-soft') => {
    const b = el('button', clases);
    b.type = 'button';
    b.append(icono('bi-plus-lg me-1'), etiqueta);
    b.addEventListener('click', accion);
    return b;
  };
  const campo = (etiqueta, control, columnas) => {
    const col = el('div', columnas);
    col.append(el('label', 'form-label small mb-1', etiqueta), control);
    return col;
  };
  const seccion = (titulo) => el('div', 'small fw-semibold mb-2 mt-3', titulo);
  return { texto, imagen, audio, quitar, boton, campo, seccion };
}

// Una plantilla por tipo: `vacio` (contenido inicial), `agregar` (botón del encabezado),
// `resumen` (texto del resumen antes de publicar) y `pintar` (dibuja el contenido en la tarjeta).
function crearPlantillas(c, repintar) {
  const bloque = (titulo, alQuitar, etiqueta) => {
    const caja = el('div', 'border rounded-4 p-3 mb-3');
    const encabezado = el('div', 'd-flex justify-content-between align-items-center mb-2');
    const quitar = el('button', 'btn btn-sm btn-outline-danger', etiqueta);
    quitar.type = 'button';
    quitar.addEventListener('click', alQuitar);
    encabezado.append(el('span', 'fw-bold', titulo), quitar);
    caja.appendChild(encabezado);
    return caja;
  };
  const vacioMensaje = (texto) => el('p', 'text-secondary mb-0', texto);

  const preguntas = (audioObligatorio) => ({
    vacio: () => ({ preguntas: [] }),
    ayuda: audioObligatorio
      ? 'El niño escucha el audio y elige la respuesta. Cada pregunta necesita un audio; marca la respuesta correcta.'
      : 'Preguntas que verá el niño. Marca la respuesta correcta de cada una.',
    agregar: 'Agregar pregunta',
    nuevo: (d) =>
      d.preguntas.push({
        enunciado: '',
        audio: null,
        opciones: [
          { texto: '', imagen: null, correcta: true },
          { texto: '', imagen: null, correcta: false },
        ],
      }),
    resumen: (d) => plural(d.preguntas.length, 'pregunta', 'preguntas'),
    pintar(d, lista) {
      if (!d.preguntas.length) lista.appendChild(vacioMensaje('Todavía no hay preguntas. Usa «Agregar pregunta».'));
      d.preguntas.forEach((p, i) => {
        const caja = bloque(
          `Pregunta ${i + 1}`,
          () => {
            d.preguntas.splice(i, 1);
            repintar();
          },
          'Quitar pregunta',
        );
        const fila = el('div', 'row g-3 mb-3');
        fila.append(
          c.campo(
            'Enunciado',
            c.texto(p, 'enunciado', audioObligatorio ? 'Ej. ¿Qué animal escuchaste?' : 'Ej. ¿Cuál de estos es una fruta?', 200, 'form-control'),
            'col-md-8',
          ),
          c.campo(
            audioObligatorio ? 'Audio (obligatorio)' : 'Audio de la pregunta (opcional)',
            c.audio(p, audioObligatorio ? 'Elige un audio' : 'Sin audio'),
            'col-md-4',
          ),
        );
        const opciones = el('div');
        p.opciones.forEach((o, j) => {
          const filaOpcion = el('div', 'd-flex align-items-center gap-2 mb-2');
          const correcta = el('input', 'form-check-input mt-0');
          correcta.type = 'radio';
          correcta.name = `correcta-${i}`;
          correcta.checked = o.correcta;
          correcta.title = 'Respuesta correcta';
          correcta.setAttribute('aria-label', 'Respuesta correcta');
          correcta.addEventListener('change', () =>
            p.opciones.forEach((otra, k) => {
              otra.correcta = k === j;
            }),
          );
          const quitarOpcion = c.quitar(
            'Quitar opción',
            () => {
              p.opciones.splice(j, 1);
              if (!p.opciones.some((x) => x.correcta)) p.opciones[0].correcta = true;
              repintar();
            },
            p.opciones.length <= 2,
          );
          filaOpcion.append(correcta, c.texto(o, 'texto', `Opción ${j + 1}`, 60), c.imagen(o), quitarOpcion);
          opciones.appendChild(filaOpcion);
        });
        if (p.opciones.length < MAX_OPCIONES) {
          const agregar = c.boton('Agregar opción', () => {
            p.opciones.push({ texto: '', imagen: null, correcta: false });
            repintar();
          });
          agregar.classList.add('mt-1');
          opciones.appendChild(agregar);
        }
        caja.append(fila, el('div', 'small fw-semibold mb-2', 'Opciones (marca la correcta)'), opciones);
        lista.appendChild(caja);
      });
    },
  });

  const clasificar = {
    vacio: () => ({
      grupos: [
        { nombre: '', imagen: null },
        { nombre: '', imagen: null },
      ],
      elementos: [],
    }),
    ayuda: 'El niño arrastra cada elemento al grupo al que pertenece (por ejemplo, vivo o no vivo).',
    agregar: 'Agregar elemento',
    nuevo: (d) => {
      if (d.elementos.length < MAX_ELEMENTOS) d.elementos.push({ texto: '', imagen: null, grupo: null });
    },
    resumen: (d) => `${plural(d.grupos.length, 'grupo', 'grupos')} · ${plural(d.elementos.length, 'elemento', 'elementos')}`,
    pintar(d, lista) {
      lista.appendChild(c.seccion(`Grupos (2 a ${MAX_GRUPOS})`));
      d.grupos.forEach((g, i) => {
        const fila = el('div', 'd-flex align-items-center gap-2 mb-2');
        const quitar = c.quitar(
          'Quitar grupo',
          () => {
            d.grupos.splice(i, 1);
            // Los elementos de ese grupo quedan sin grupo y los demás conservan el suyo
            d.elementos.forEach((e) => {
              if (e.grupo === i) e.grupo = null;
              else if (e.grupo > i) e.grupo -= 1;
            });
            repintar();
          },
          d.grupos.length <= 2,
        );
        const nombre = c.texto(g, 'nombre', 'Ej. Vivo', 40);
        nombre.addEventListener('change', repintar); // al terminar de escribir, la lista de grupos de los elementos se actualiza
        fila.append(el('span', 'small text-secondary', `${i + 1}.`), nombre, c.imagen(g), quitar);
        lista.appendChild(fila);
      });
      if (d.grupos.length < MAX_GRUPOS) {
        lista.appendChild(
          c.boton('Agregar grupo', () => {
            d.grupos.push({ nombre: '', imagen: null });
            repintar();
          }),
        );
      }

      lista.appendChild(c.seccion(`Elementos (hasta ${MAX_ELEMENTOS}) y el grupo al que pertenece cada uno`));
      if (!d.elementos.length) lista.appendChild(vacioMensaje('Todavía no hay elementos. Usa «Agregar elemento».'));
      d.elementos.forEach((e, i) => {
        const fila = el('div', 'd-flex align-items-center gap-2 mb-2 flex-wrap');
        const grupo = el('select', 'form-select form-select-sm');
        grupo.style.width = '160px';
        grupo.append(
          el('option', '', 'Elige el grupo'),
          ...d.grupos.map((g, k) => {
            const op = el('option', '', g.nombre.trim() || `Grupo ${k + 1}`);
            op.value = k;
            return op;
          }),
        );
        grupo.value = e.grupo ?? '';
        grupo.addEventListener('change', () => {
          e.grupo = grupo.value === '' ? null : Number(grupo.value);
        });
        fila.append(
          c.texto(e, 'texto', 'Ej. Perro', 40),
          c.imagen(e),
          grupo,
          c.quitar('Quitar elemento', () => {
            d.elementos.splice(i, 1);
            repintar();
          }),
        );
        lista.appendChild(fila);
      });
    },
  };

  const emparejar = {
    vacio: () => ({ parejas: [] }),
    ayuda: 'El niño arrastra cada elemento hasta su pareja (por ejemplo, un número hasta esa cantidad de objetos).',
    agregar: 'Agregar pareja',
    nuevo: (d) => {
      if (d.parejas.length < MAX_PAREJAS) d.parejas.push({ elemento: { texto: '', imagen: null }, destino: { texto: '', imagen: null } });
    },
    resumen: (d) => plural(d.parejas.length, 'pareja', 'parejas'),
    pintar(d, lista) {
      if (!d.parejas.length) lista.appendChild(vacioMensaje('Todavía no hay parejas. Usa «Agregar pareja».'));
      d.parejas.forEach((p, i) => {
        const caja = bloque(
          `Pareja ${i + 1}`,
          () => {
            d.parejas.splice(i, 1);
            repintar();
          },
          'Quitar pareja',
        );
        const fila = el('div', 'row g-3');
        for (const [lado, titulo] of [
          ['elemento', 'Elemento que se arrastra'],
          ['destino', 'Destino (su pareja)'],
        ]) {
          const columna = el('div', 'col-md-6');
          const controles = el('div', 'd-flex align-items-center gap-2');
          controles.append(c.texto(p[lado], 'texto', 'Texto', 40), c.imagen(p[lado]));
          columna.append(el('label', 'form-label small mb-1', titulo), controles);
          fila.appendChild(columna);
        }
        caja.appendChild(fila);
        lista.appendChild(caja);
      });
    },
  };

  const silabas = {
    vacio: () => ({ palabras: [] }),
    ayuda: 'El niño ordena las sílabas para armar la palabra. Escríbelas en orden, separadas por guion.',
    agregar: 'Agregar palabra',
    nuevo: (d) => {
      if (d.palabras.length < MAX_PALABRAS) d.palabras.push({ silabas: [], imagen: null, audio: null });
    },
    resumen: (d) => plural(d.palabras.length, 'palabra', 'palabras'),
    pintar(d, lista) {
      if (!d.palabras.length) lista.appendChild(vacioMensaje('Todavía no hay palabras. Usa «Agregar palabra».'));
      d.palabras.forEach((p, i) => {
        const caja = bloque(
          `Palabra ${i + 1}`,
          () => {
            d.palabras.splice(i, 1);
            repintar();
          },
          'Quitar palabra',
        );
        const escritas = el('input', 'form-control');
        escritas.maxLength = 60;
        escritas.placeholder = 'Ej. ma-ri-po-sa';
        escritas.value = p.silabas.join('-');
        escritas.addEventListener('input', () => {
          p.silabas = escritas.value.split(/[-\s]+/).filter(Boolean);
        });
        const fila = el('div', 'row g-3');
        fila.append(
          c.campo('Sílabas en orden (2 a 6)', escritas, 'col-md-4'),
          c.campo('Imagen de la palabra (opcional)', c.imagen(p), 'col-md-4'),
          c.campo('Audio (opcional)', c.audio(p, 'Sin audio'), 'col-md-4'),
        );
        caja.appendChild(fila);
        lista.appendChild(caja);
      });
    },
  };

  const memory = {
    vacio: () => ({ pares: [] }),
    ayuda: 'Cada par genera dos cartas. Con imagen y texto, una carta muestra la imagen y la otra el texto; con uno solo, las dos cartas son iguales.',
    agregar: 'Agregar par',
    nuevo: (d) => {
      if (d.pares.length < MAX_PARES) d.pares.push({ texto: '', imagen: null });
    },
    resumen: (d) => `${plural(d.pares.length, 'par', 'pares')} (${d.pares.length * 2} cartas)`,
    pintar(d, lista) {
      if (!d.pares.length) lista.appendChild(vacioMensaje('Todavía no hay pares. Usa «Agregar par».'));
      d.pares.forEach((p, i) => {
        const fila = el('div', 'd-flex align-items-center gap-2 mb-2 flex-wrap');
        fila.append(
          el('span', 'fw-bold small', `Par ${i + 1}`),
          c.texto(p, 'texto', 'Ej. Dog', 30),
          c.imagen(p),
          c.quitar('Quitar par', () => {
            d.pares.splice(i, 1);
            repintar();
          }),
        );
        lista.appendChild(fila);
      });
    },
  };

  return {
    'Selección múltiple': preguntas(false),
    'Comprensión auditiva': preguntas(true),
    Arrastrar: clasificar,
    'Arrastrar y soltar': emparejar,
    'Ordenar sílabas': silabas,
    'Memory match': memory,
  };
}

export function crearEditorContenido(actividad, catalogo, selector) {
  const enApp = Boolean(actividad?.en_app);
  const filaPrincipal = $('#resourceGrid').closest('.row');
  const tarjeta = el('div', 'card mt-4');
  const cabecera = el('div', 'card-header d-flex justify-content-between align-items-center flex-wrap gap-2');
  const titulos = el('div');
  const titulo = el('h2', 'card-title');
  titulo.append(icono('bi-ui-checks-grid me-2 text-primary'), 'Contenido');
  const ayuda = el('span', 'small text-secondary');
  titulos.append(titulo, ayuda);
  const botonAgregar = el('button', 'btn btn-sm btn-soft');
  botonAgregar.type = 'button';
  cabecera.append(titulos, botonAgregar);
  const lista = el('div', 'card-body p-4');
  tarjeta.append(cabecera, lista);
  filaPrincipal.after(tarjeta);

  const tipo = () => $('#actTipo').value;
  const usaPlantilla = () => !enApp && tipo() in plantillas;
  // El contenido de cada tipo se conserva aparte: cambiar de tipo y volver no borra lo escrito
  const datos = {};
  const contenidoDe = (nombre) => {
    if (!datos[nombre]) {
      datos[nombre] = nombre === actividad?.tipo && actividad.contenido ? structuredClone(actividad.contenido) : plantillas[nombre].vacio();
    }
    return datos[nombre];
  };

  const repintar = () => {
    tarjeta.classList.toggle('d-none', !usaPlantilla());
    if (!usaPlantilla()) return;
    const plantilla = plantillas[tipo()];
    ayuda.textContent = plantilla.ayuda;
    botonAgregar.replaceChildren(icono('bi-plus-lg me-1'), plantilla.agregar);
    lista.replaceChildren();
    plantilla.pintar(contenidoDe(tipo()), lista);
  };
  const plantillas = crearPlantillas(crearControles({ catalogo, selector }), repintar);

  botonAgregar.addEventListener('click', () => {
    plantillas[tipo()].nuevo(contenidoDe(tipo()));
    repintar();
  });
  $('#actTipo').addEventListener('change', repintar);
  $('#actMateria').addEventListener('change', repintar);
  repintar();

  return {
    contenido: () => (usaPlantilla() ? contenidoDe(tipo()) : null),
    resumen: () => (usaPlantilla() ? plantillas[tipo()].resumen(contenidoDe(tipo())) : null),
  };
}

import { el } from './dom.js';
import { mostrarError } from './toast.js';

// Entrega al navegador un archivo ya descargado de la API ({ blob, nombre }).
export async function guardarArchivo(pedirArchivo) {
  try {
    const { blob, nombre } = await pedirArchivo();
    const enlace = el('a');
    enlace.href = URL.createObjectURL(blob);
    enlace.download = nombre;
    document.body.appendChild(enlace);
    enlace.click();
    enlace.remove();
    setTimeout(() => URL.revokeObjectURL(enlace.href), 1000);
  } catch (error) {
    mostrarError(error);
  }
}

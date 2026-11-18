import { ActividadDetallePage, mountActividadDetallePage } from '../pages/ActividadDetallePage.js';
import { ActividadesPage, mountActividadesPage } from '../pages/ActividadesPage.js';
import { BorradoresPage, mountBorradoresPage } from '../pages/BorradoresPage.js';
import { ConstructorPage, mountConstructorPage } from '../pages/ConstructorPage.js';
import { HistorialPage, mountHistorialPage } from '../pages/HistorialPage.js';
import { InicioPage, mountInicioPage } from '../pages/InicioPage.js';
import { InstitucionNuevaPage, mountInstitucionNuevaPage } from '../pages/InstitucionNuevaPage.js';
import { InstitucionesPage, mountInstitucionesPage } from '../pages/InstitucionesPage.js';
import { LoginPage, mountLoginPage } from '../pages/LoginPage.js';
import { MonitoreoPage, mountMonitoreoPage } from '../pages/MonitoreoPage.js';
import { RecursosPage, mountRecursosPage } from '../pages/RecursosPage.js';
import { RegistroPage, mountRegistroPage } from '../pages/RegistroPage.js';
import { UsuariosPage, mountUsuariosPage } from '../pages/UsuariosPage.js';

// Cada ruta dice qué página dibuja, qué hace al montarla, si pide sesión y qué opción del menú se marca.
// `conLayout: false` = pantalla completa (sin barra lateral).
const routeList = [
  { path: 'login', conLayout: false, page: LoginPage, mount: mountLoginPage },
  { path: 'crear-usuario', conLayout: false, page: RegistroPage, mount: mountRegistroPage },
  { path: 'inicio', requiresAuth: true, menu: 'inicio', page: InicioPage, mount: mountInicioPage },
  { path: 'actividades', requiresAuth: true, menu: 'actividades', page: ActividadesPage, mount: mountActividadesPage },
  { path: 'borradores', requiresAuth: true, menu: 'actividades', page: BorradoresPage, mount: mountBorradoresPage },
  { path: 'actividad-detalle', requiresAuth: true, menu: 'actividades', page: ActividadDetallePage, mount: mountActividadDetallePage },
  { path: 'constructor', requiresAuth: true, menu: 'actividades', page: ConstructorPage, mount: mountConstructorPage },
  { path: 'historial', requiresAuth: true, menu: 'actividades', page: HistorialPage, mount: mountHistorialPage },
  { path: 'recursos', requiresAuth: true, menu: 'recursos', page: RecursosPage, mount: mountRecursosPage },
  { path: 'instituciones', requiresAuth: true, menu: 'instituciones', page: InstitucionesPage, mount: mountInstitucionesPage },
  { path: 'institucion-nueva', requiresAuth: true, menu: 'instituciones', page: InstitucionNuevaPage, mount: mountInstitucionNuevaPage },
  { path: 'usuarios', requiresAuth: true, menu: 'usuarios', page: UsuariosPage, mount: mountUsuariosPage },
  { path: 'monitoreo', requiresAuth: true, menu: 'monitoreo', page: MonitoreoPage, mount: mountMonitoreoPage },
];

// "#/actividad-detalle?id=vivo-o-no-vivo" → { view: 'actividad-detalle', query: URLSearchParams }
export function leerRuta(hash = window.location.hash) {
  const [camino, consulta = ''] = hash.replace(/^#\/?/, '').split('?');
  return { view: camino.replace(/\/+$/, '') || 'inicio', query: new URLSearchParams(consulta) };
}

export function getRoute(view) {
  return routeList.find((route) => route.path === view) ?? null;
}

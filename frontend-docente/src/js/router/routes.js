import { ActividadesPage, mountActividadesPage } from '../pages/ActividadesPage.js';
import { EstudiantesPage, mountEstudiantesPage } from '../pages/EstudiantesPage.js';
import { GestionPage, mountGestionPage } from '../pages/GestionPage.js';
import { LoginPage, mountLoginPage } from '../pages/LoginPage.js';
import { MisDatosPage, mountMisDatosPage } from '../pages/MisDatosPage.js';
import { PanelPage, mountPanelPage } from '../pages/PanelPage.js';
import { ReportesPage, mountReportesPage } from '../pages/ReportesPage.js';

// Cada ruta dice qué página dibuja, qué hace al montarla y si pide sesión.
// `conLayout: false` = pantalla completa (sin barra lateral).
const routeList = [
  { path: 'login', conLayout: false, page: LoginPage, mount: mountLoginPage },
  { path: 'panel', requiresAuth: true, page: PanelPage, mount: mountPanelPage },
  { path: 'estudiantes', requiresAuth: true, page: EstudiantesPage, mount: mountEstudiantesPage },
  { path: 'actividades', requiresAuth: true, page: ActividadesPage, mount: mountActividadesPage },
  { path: 'reportes', requiresAuth: true, page: ReportesPage, mount: mountReportesPage },
  { path: 'gestion', requiresAuth: true, page: GestionPage, mount: mountGestionPage },
  { path: 'mis-datos', requiresAuth: true, page: MisDatosPage, mount: mountMisDatosPage },
];

// "#/reportes?generar=1" → { view: 'reportes', query: URLSearchParams }
export function leerRuta(hash = window.location.hash) {
  const [camino, consulta = ''] = hash.replace(/^#\/?/, '').split('?');
  return { view: camino.replace(/\/+$/, '') || 'panel', query: new URLSearchParams(consulta) };
}

export function getRoute(view) {
  return routeList.find((route) => route.path === view) ?? null;
}

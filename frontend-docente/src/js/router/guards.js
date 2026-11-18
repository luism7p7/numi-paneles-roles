import { isAuthenticated } from '../auth/permissions.js';

// Las pantallas del panel exigen sesión. `alDenegar` recibe el motivo ('login').
export function requireAuth(alDenegar) {
  if (!isAuthenticated()) {
    alDenegar?.('login');
    return false;
  }
  return true;
}

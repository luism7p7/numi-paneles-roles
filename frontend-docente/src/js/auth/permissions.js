import { hasSession } from './session.service.js';

export function isAuthenticated() {
  return hasSession();
}

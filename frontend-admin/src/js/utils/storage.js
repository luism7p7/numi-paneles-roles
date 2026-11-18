// Lectura y escritura segura en localStorage (guarda y devuelve JSON).
export function saveItem(key, value) {
  if (value === undefined || value === null) {
    removeItem(key);
    return;
  }
  localStorage.setItem(key, JSON.stringify(value));
}

export function getItem(key) {
  const stored = localStorage.getItem(key);
  if (stored === null) return null;
  try {
    return JSON.parse(stored);
  } catch {
    return stored;
  }
}

export function removeItem(key) {
  localStorage.removeItem(key);
}

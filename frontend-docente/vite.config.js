import { defineConfig } from 'vite';

// El panel docente corre en el 5174 (el administrativo en el 5173); la API en el 5001.
export default defineConfig({
  server: { port: 5174, strictPort: true },
  preview: { port: 5174, strictPort: true }
});

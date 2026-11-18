import { defineConfig } from 'vite';

// El panel administrativo corre en el 5173 (el docente en el 5174); la API en el 5001.
export default defineConfig({
  server: { port: 5173, strictPort: true },
  preview: { port: 5173, strictPort: true }
});

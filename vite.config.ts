import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  // Le worker charge Pyodide par import dynamique, ce qui exige le format ES.
  worker: { format: 'es' },
})

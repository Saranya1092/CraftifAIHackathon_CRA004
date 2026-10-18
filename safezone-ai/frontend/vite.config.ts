import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Build-only config (no test config here to avoid vitest/vite type conflicts)
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})

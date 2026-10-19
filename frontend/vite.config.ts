import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Żądania /api trafiają do FastAPI (lokalnie :8000, w Dockerze serwis "api").
const apiUrl = process.env.VITE_API_URL ?? 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': apiUrl,
    },
  },
})

import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

const apiUrl = process.env.VITE_API_URL ?? 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': apiUrl,
    },
  },
})

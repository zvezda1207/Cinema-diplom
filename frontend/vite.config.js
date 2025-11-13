import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
const proxyTarget = process.env.VITE_PROXY_TARGET || 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Слушаем на всех интерфейсах для Docker
    port: 3000, // Используем порт 3000 по умолчанию
    proxy: {
      '/api': {
        target: proxyTarget,
        changeOrigin: true,
        secure: false,
      },
      '/qr-codes': {
        target: proxyTarget,
        changeOrigin: true,
        secure: false,
      },
    }
  }
})

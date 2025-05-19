import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    watch: {
      usePolling: true,
      interval: 100,
    },
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/auth': {
        target: 'http://backend:8000',  
        changeOrigin: true,
      },
      '/oauth': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
      '/connected_services': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
      '/favorites': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
      '/playlists': { 
        target: 'http://backend:8000', 
        changeOrigin: true 
      },
      '/yandex_music': {
        target: 'http://backend:8000',
        changeOrigin: true
      },
    }
  }
})

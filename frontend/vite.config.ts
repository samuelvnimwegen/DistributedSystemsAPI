import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api/movies': 'http://movie_api:5000',
        '/api/activity': 'http://activity_api:5000',
        '/api/users': 'http://user_api:5000',
        '/api/preference': 'http://preference_api:5000',
    },
    watch: {
      usePolling: true,
    },
    host: true,
    strictPort: true,
  },
})

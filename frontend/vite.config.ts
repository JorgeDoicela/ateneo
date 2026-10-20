/// <reference types="vitest" />
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      injectRegister: 'auto',
      includeAssets: ['favicon-32x32.png', 'apple-touch-icon.png', 'ateneo.png', 'nombre.png'],
      manifest: {
        name: 'Ateneo+ — Simulador Clínico',
        short_name: 'Ateneo+',
        description: 'Simulador clínico multimodal y evaluación formativa médica con IA y RAG (GPC Ecuador)',
        theme_color: '#ffffff',
        background_color: '#f0f4f9',
        display: 'standalone',
        orientation: 'any',
        start_url: '/',
        scope: '/',
        id: '/',
        categories: ['education', 'medical'],
        icons: [
          {
            src: '/pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png',
            purpose: 'any'
          },
          {
            src: '/pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any'
          },
          {
            src: '/pwa-maskable-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable'
          }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'google-fonts-cache',
              expiration: {
                maxEntries: 10,
                maxAgeSeconds: 60 * 60 * 24 * 365
              },
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          },
          {
            urlPattern: /^https:\/\/fonts\.gstatic\.com\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'gstatic-fonts-cache',
              expiration: {
                maxEntries: 20,
                maxAgeSeconds: 60 * 60 * 24 * 365
              },
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          }
        ]
      },
      devOptions: {
        enabled: true
      }
    })
  ],
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: true,
    watch: {
      usePolling: true,
    },
    proxy: {
      '/api': {
        target: process.env.BACKEND_PROXY_URL || process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
        ws: true,
        timeout: 180000,
        proxyTimeout: 180000,
      },
      '/static': {
        target: process.env.BACKEND_PROXY_URL || process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
        timeout: 60000,
        proxyTimeout: 60000,
      }
    }
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/setupTests.ts',
    include: ['src/__tests__/**/*.{test,spec}.{js,jsx,ts,tsx}'],
    exclude: ['e2e/**', 'node_modules/**'],
    pool: 'forks',
    maxWorkers: 1,
  }
})

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// PWA / service-worker config (spec §3.2, §10.3).
// - App shell: precache all JS/CSS/HTML (cache-first).
// - API calls: network-first with offline fallback (handled in src/api/client.js
//   queue + the runtime caching rule below).
// - Parcel GeoJSON is stored in IndexedDB (src/db/parcelCache.js), NOT the SW
//   cache, because per-county bundles can be ~50MB (spec §10.3).
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.png', 'gas-shield.png', 'logo-lockup.png', 'icons/*.png'],
      manifest: {
        name: 'TNC GAS Mapping',
        short_name: 'TNC GAS',
        description: 'Ground & Aerial Services — address → DJI mission → scaled planning maps.',
        theme_color: '#1B3A5C',
        background_color: '#1B3A5C',
        display: 'standalone',
        orientation: 'portrait',
        start_url: '/',
        icons: [
          { src: 'icons/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icons/icon-512.png', sizes: '512x512', type: 'image/png' },
          { src: 'icons/icon-maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg,png,woff2}'],
        maximumFileSizeToCacheInBytes: 5 * 1024 * 1024,
        runtimeCaching: [
          {
            // Recently-searched geocoding results cached for offline reuse
            // (spec §3.2 / §10.1).
            urlPattern: ({ url }) => url.pathname.startsWith('/geocode'),
            handler: 'NetworkFirst',
            options: {
              cacheName: 'geocode-cache',
              expiration: { maxEntries: 100, maxAgeSeconds: 60 * 60 * 24 * 30 }
            }
          },
          {
            // MapLibre vector basemap tiles — offline tile cache (spec §10.3).
            urlPattern: ({ url }) => /tiles|basemap/.test(url.pathname),
            handler: 'CacheFirst',
            options: {
              cacheName: 'basemap-tiles',
              expiration: { maxEntries: 2000, maxAgeSeconds: 60 * 60 * 24 * 90 }
            }
          }
        ]
      },
      devOptions: { enabled: false }
    })
  ],
  server: { port: 5173, host: true }
})

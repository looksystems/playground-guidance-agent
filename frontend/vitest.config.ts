import { defineConfig } from 'vitest/config'
import { fileURLToPath } from 'node:url'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'happy-dom',
    setupFiles: ['./tests/setup.ts'],
    server: {
      deps: {
        inline: ['@nuxt/ui']
      }
    }
  },
  resolve: {
    alias: {
      '~/composables': fileURLToPath(new URL('./app/composables', import.meta.url)),
      '~/components': fileURLToPath(new URL('./app/components', import.meta.url)),
      '~/plugins': fileURLToPath(new URL('./app/plugins', import.meta.url)),
      '~/app': fileURLToPath(new URL('./app', import.meta.url)),
      '~': fileURLToPath(new URL('./app', import.meta.url)),
      '@': fileURLToPath(new URL('./app', import.meta.url))
    }
  }
})

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',

  // Nuxt 3 directory configuration for app/ folder structure
  dir: {
    pages: 'app/pages',
    layouts: 'app/layouts',
    middleware: 'app/middleware',
    plugins: 'app/plugins'
  },

  // Add components directory for auto-import
  components: [
    { path: '~/app/components' }
  ],

  modules: [
    '@nuxt/ui',
    '@pinia/nuxt'
  ],

  icon: {
    clientBundle: {
      scan: true
    },
    provider: 'iconify'
  },

  css: ['~/app/assets/css/main.css'],

  devtools: { enabled: true },

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000'
    }
  },

  typescript: {
    strict: true,
    typeCheck: false  // Disabled in development, enable in CI/CD
  },

  // Proxy API requests to FastAPI
  nitro: {
    devProxy: {
      '/api': {
        target: 'http://localhost:8000/api',
        changeOrigin: true,
        prependPath: true
      }
    }
  },

  routeRules: {
    '/api/**': { proxy: 'http://localhost:8000/api/**' }
  },

  app: {
    head: {
      title: 'Pension Guidance Service',
      link: [
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fira+Code&display=swap'
        }
      ]
    }
  },

  // Test configuration
  vite: {
    test: {
      environment: 'happy-dom',
      setupFiles: ['./tests/setup.ts']
    }
  }
})

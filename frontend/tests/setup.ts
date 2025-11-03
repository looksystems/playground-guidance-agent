import { vi } from 'vitest'
import { config } from '@vue/test-utils'
import { ref, computed, reactive, nextTick, watch } from 'vue'
import { defineStore } from 'pinia'
import Module from 'module'
import path from 'path'
import { fileURLToPath } from 'url'
import { dirname } from 'path'

// Get the directory of this setup file
const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

// Import all composables and components and make them available
import * as useHealthCheckModule from '../app/composables/useHealthCheck'
import BackendHealthBannerComponent from '../app/components/common/BackendHealthBanner.vue'
// Note: Cannot import plugin here due to #app dependency, will be loaded dynamically

// Setup module aliasing for require() calls in tests
const originalRequire = Module.prototype.require as any
const appDir = path.resolve(__dirname, '../app')

// Cache for loaded modules
const moduleCache: Record<string, any> = {
  '~/composables/useHealthCheck': useHealthCheckModule,
  '~/components/common/BackendHealthBanner.vue': { default: BackendHealthBannerComponent }
  // Plugin will be resolved via file system
}

Module.prototype.require = function(id: string) {
  // Check cache first
  if (moduleCache[id]) {
    return moduleCache[id]
  }

  if (id.startsWith('~/composables/')) {
    const modulePath = path.join(appDir, 'composables', id.replace('~/composables/', '')) + '.ts'
    return originalRequire.call(this, modulePath)
  }
  if (id.startsWith('~/components/')) {
    const modulePath = path.join(appDir, 'components', id.replace('~/components/', '')) + '.vue'
    return originalRequire.call(this, modulePath)
  }
  if (id.startsWith('~/plugins/')) {
    const modulePath = path.join(appDir, 'plugins', id.replace('~/plugins/', '')) + '.ts'
    return originalRequire.call(this, modulePath)
  }
  if (id.startsWith('~/')) {
    const modulePath = path.join(appDir, id.replace('~/', ''))
    return originalRequire.call(this, modulePath)
  }

  return originalRequire.call(this, id)
} as any

// Mock Nuxt auto-imports
global.defineNuxtConfig = vi.fn()
global.useRuntimeConfig = vi.fn(() => ({
  public: {
    apiBase: 'http://localhost:8000'
  }
}))
global.navigateTo = vi.fn()
global.useFetch = vi.fn(() => ({
  data: ref(null),
  pending: ref(false),
  error: ref(null),
  refresh: vi.fn()
}))
global.ref = ref
global.computed = computed
global.reactive = reactive
global.nextTick = nextTick
global.watch = watch
global.defineStore = defineStore
global.$fetch = vi.fn() as any
global.definePageMeta = vi.fn()
global.useRoute = vi.fn(() => ({
  path: '/admin',
  params: {},
  query: {}
}))
global.useRouter = vi.fn(() => ({
  push: vi.fn(),
  replace: vi.fn(),
  back: vi.fn(),
  forward: vi.fn()
}))

// Stub Nuxt UI components globally
config.global.stubs = {
  UButton: {
    template: '<button><slot /></button>',
    props: ['to', 'variant', 'icon', 'block', 'justify', 'active', 'size']
  },
  UIcon: {
    name: 'UIcon',
    template: '<i :class="name"></i>',
    props: ['name', 'class']
  },
  UCard: {
    template: '<div class="card"><header v-if="$slots.header"><slot name="header" /></header><slot /></div>',
    props: []
  },
  UTable: {
    template: '<table><slot /></table>',
    props: ['columns', 'rows', 'loading']
  },
  UBadge: {
    template: '<span><slot /></span>',
    props: ['color', 'variant']
  },
  UMeter: {
    template: '<div class="meter"></div>',
    props: ['value', 'max', 'color']
  },
  USkeleton: {
    template: '<div class="skeleton"></div>',
    props: ['class']
  },
  NuxtLink: {
    template: '<a><slot /></a>',
    props: ['to']
  },
  ClientOnly: {
    template: '<div><slot /></div>'
  },
  AdminLineChart: {
    template: '<div class="chart"></div>',
    props: ['data', 'height']
  }
}

// Mock $route globally
config.global.mocks = {
  $route: {
    path: '/admin',
    params: {},
    query: {}
  }
}

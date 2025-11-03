import type { Ref, ComputedRef } from 'vue'
import type { Mock } from 'vitest'
import type { DefineStoreOptions } from 'pinia'
import type { $Fetch } from 'nitropack'

declare global {
  var defineNuxtConfig: Mock
  var useRuntimeConfig: Mock
  var navigateTo: Mock
  var useFetch: Mock
  var ref: typeof import('vue').ref
  var computed: typeof import('vue').computed
  var reactive: typeof import('vue').reactive
  var nextTick: typeof import('vue').nextTick
  var defineStore: typeof import('pinia').defineStore
  var $fetch: $Fetch
  var definePageMeta: Mock
  var useRoute: Mock
  var useRouter: Mock
}

export {}

<template>
  <ClientOnly>
    <div class="space-y-6">
      <!-- Header with Breadcrumb -->
      <div class="mb-6">
        <UButton to="/admin" variant="ghost" icon="i-heroicons-arrow-left">
          Back to Dashboard
        </UButton>
        <h1 class="text-3xl font-bold mt-4">Rule Repository</h1>
        <p class="text-gray-600 dark:text-gray-400 mt-2">Learned principles and domain knowledge</p>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <UCard>
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Total Rules</p>
              <p class="mt-2 text-4xl font-bold">{{ stats.total }}</p>
            </div>
            <div class="p-3 bg-teal-50 dark:bg-teal-900/20 rounded-lg">
              <UIcon name="i-heroicons-shield-check-solid" class="w-6 h-6 text-teal-600 dark:text-teal-400" />
            </div>
          </div>
        </UCard>

        <UCard>
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Domains</p>
              <p class="mt-2 text-4xl font-bold">{{ stats.domains }}</p>
            </div>
            <div class="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <UIcon name="i-heroicons-squares-2x2-solid" class="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
        </UCard>

        <UCard>
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">High Confidence</p>
              <p class="mt-2 text-4xl font-bold">{{ stats.highConfidence }}</p>
            </div>
            <div class="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <UIcon name="i-heroicons-star-solid" class="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
          </div>
        </UCard>
      </div>

      <!-- Filters Bar -->
      <UCard>
        <div class="flex flex-wrap gap-4">
          <!-- Domain Filter -->
          <div class="flex-1 min-w-[200px]">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Domain</label>
            <USelectMenu
              v-model="filters.domain"
              :options="domainOptions"
              placeholder="All Domains"
              @update:model-value="applyFilters"
            />
          </div>

          <!-- Confidence Range -->
          <div class="flex-1 min-w-[200px]">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Min Confidence: {{ filters.minConfidence.toFixed(1) }}
            </label>
            <input
              v-model.number="filters.minConfidence"
              type="range"
              min="0"
              max="1"
              step="0.1"
              class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
              @change="applyFilters"
            />
          </div>

          <div class="flex-1 min-w-[200px]">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Max Confidence: {{ filters.maxConfidence.toFixed(1) }}
            </label>
            <input
              v-model.number="filters.maxConfidence"
              type="range"
              min="0"
              max="1"
              step="0.1"
              class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
              @change="applyFilters"
            />
          </div>

          <!-- Date Range -->
          <div class="flex-1 min-w-[200px]">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">From Date</label>
            <UInput
              v-model="filters.fromDate"
              type="date"
              @update:model-value="applyFilters"
            />
          </div>

          <div class="flex-1 min-w-[200px]">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">To Date</label>
            <UInput
              v-model="filters.toDate"
              type="date"
              @update:model-value="applyFilters"
            />
          </div>

          <!-- Clear Filters -->
          <div class="flex items-end">
            <UButton
              variant="outline"
              icon="i-heroicons-x-mark"
              @click="clearFilters"
            >
              Clear
            </UButton>
          </div>
        </div>
      </UCard>

      <!-- Sort Controls -->
      <UCard>
        <div class="flex flex-wrap gap-4 items-center">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Sort By</label>
            <USelectMenu
              v-model="sortBy"
              :options="sortOptions"
              @update:model-value="applyFilters"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Order</label>
            <USelectMenu
              v-model="sortOrder"
              :options="['asc', 'desc']"
              @update:model-value="applyFilters"
            />
          </div>
        </div>
      </UCard>

      <!-- Error State -->
      <UAlert
        v-if="error"
        color="red"
        variant="solid"
        title="Failed to load rules"
        :description="error.message || 'An error occurred while loading the data.'"
        icon="i-heroicons-exclamation-triangle"
      />

      <!-- Loading State -->
      <div v-if="pending" class="flex items-center justify-center py-12">
        <div class="text-center">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
          <p class="mt-4 text-gray-600 dark:text-gray-400">Loading rules...</p>
        </div>
      </div>

      <!-- Empty State -->
      <UCard v-else-if="!items || items.length === 0">
        <div class="text-center py-12">
          <UIcon name="i-heroicons-shield-check" class="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">No Rules Found</h3>
          <p class="text-gray-600 dark:text-gray-400">
            {{ filters.domain || filters.minConfidence > 0 ? 'Try adjusting your filters' : 'No rules have been learned yet.' }}
          </p>
        </div>
      </UCard>

      <!-- Data Table -->
      <UCard v-else>
        <template #header>
          <div class="flex items-center justify-between">
            <h2 class="text-xl font-semibold">Rules</h2>
            <span class="text-sm text-gray-600 dark:text-gray-400">
              Showing {{ items.length }} of {{ pagination.total }} items
            </span>
          </div>
        </template>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ID
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Principle
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Domain
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Confidence
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Evidence
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Updated
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="item in items" :key="item.id" class="hover:bg-gray-50 dark:hover:bg-gray-800 dark:bg-gray-800">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900 dark:text-gray-100">
                  {{ item.id.substring(0, 8) }}...
                </td>
                <td class="px-6 py-4 text-sm text-gray-900 dark:text-gray-100 max-w-md">
                  <div class="line-clamp-2">{{ item.principle }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <UBadge color="teal" variant="subtle">
                    {{ item.domain || 'General' }}
                  </UBadge>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <div class="flex items-center gap-2">
                    <div class="flex-1 w-20 bg-gray-200 rounded-full h-2">
                      <div
                        class="h-2 rounded-full transition-all"
                        :class="getConfidenceBarColor(item.confidence)"
                        :style="{ width: `${item.confidence * 100}%` }"
                      ></div>
                    </div>
                    <UBadge
                      :color="getConfidenceColor(item.confidence)"
                      variant="subtle"
                      size="xs"
                    >
                      {{ item.confidence.toFixed(2) }}
                    </UBadge>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <UBadge color="blue" variant="subtle">
                    {{ getEvidenceCount(item.supporting_evidence) }}
                  </UBadge>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                  {{ formatDate(item.updated_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <UButton
                    size="xs"
                    @click="navigateTo(`/admin/learning/rules/${item.id}`)"
                  >
                    View
                  </UButton>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </UCard>

      <!-- Pagination -->
      <div v-if="items && items.length > 0" class="flex items-center justify-between">
        <div class="text-sm text-gray-600 dark:text-gray-400">
          Page {{ pagination.page }} of {{ pagination.pages }}
        </div>
        <div class="flex gap-2">
          <UButton
            icon="i-heroicons-chevron-left"
            :disabled="pagination.page === 1"
            @click="goToPage(pagination.page - 1)"
          >
            Previous
          </UButton>
          <UButton
            icon="i-heroicons-chevron-right"
            trailing
            :disabled="pagination.page === pagination.pages"
            @click="goToPage(pagination.page + 1)"
          >
            Next
          </UButton>
        </div>
      </div>
    </div>

    <template #fallback>
      <div class="flex items-center justify-center min-h-screen">
        <div class="text-center">
          <UIcon name="i-heroicons-arrow-path" class="w-12 h-12 animate-spin text-gray-400 mx-auto mb-4" />
          <p class="text-gray-500">Loading rules...</p>
        </div>
      </div>
    </template>
  </ClientOnly>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  ssr: false
})

// State
const filters = ref({
  domain: null as string | null,
  minConfidence: 0.0,
  maxConfidence: 1.0,
  fromDate: '',
  toDate: ''
})

const sortBy = ref('confidence')
const sortOrder = ref('desc')
const currentPage = ref(1)
const pageSize = 20

const sortOptions = ['confidence', 'created_at', 'updated_at']

// Computed query params
const queryParams = computed(() => {
  const params: any = {
    page: currentPage.value,
    page_size: pageSize,
    sort_by: sortBy.value,
    sort_order: sortOrder.value
  }
  if (filters.value.domain && filters.value.domain !== 'All Domains') {
    params.domain = filters.value.domain
  }
  if (filters.value.minConfidence > 0) params.min_confidence = filters.value.minConfidence
  if (filters.value.maxConfidence < 1) params.max_confidence = filters.value.maxConfidence
  if (filters.value.fromDate) params.from_date = filters.value.fromDate
  if (filters.value.toDate) params.to_date = filters.value.toDate
  return params
})

// Fetch data
const { data: apiData, pending, error, refresh } = await useFetch('/api/admin/rules', {
  query: queryParams,
  headers: {
    'Authorization': 'Bearer admin-token'
  },
  watch: false
})

// Computed data
const items = computed(() => apiData.value?.items || [])
const pagination = computed(() => ({
  total: apiData.value?.total || 0,
  page: apiData.value?.page || 1,
  pages: apiData.value?.pages || 1,
  page_size: apiData.value?.page_size || pageSize
}))

const stats = computed(() => ({
  total: apiData.value?.total || 0,
  domains: apiData.value?.domains_count || 0,
  highConfidence: apiData.value?.high_confidence_count || 0
}))

// Get unique domains for filter
const domainOptions = computed(() => {
  if (!apiData.value?.items) return ['All Domains']
  const domains = new Set(apiData.value.items.map((item: any) => item.domain).filter(Boolean))
  return ['All Domains', ...Array.from(domains)]
})

// Methods
const getConfidenceColor = (confidence: number) => {
  if (confidence > 0.8) return 'green'
  if (confidence >= 0.5) return 'yellow'
  return 'red'
}

const getConfidenceBarColor = (confidence: number) => {
  if (confidence > 0.8) return 'bg-green-500'
  if (confidence >= 0.5) return 'bg-yellow-500'
  return 'bg-red-500'
}

const getEvidenceCount = (evidence: any) => {
  if (!evidence) return 0
  if (Array.isArray(evidence)) return evidence.length
  if (typeof evidence === 'object') return Object.keys(evidence).length
  return 0
}

const applyFilters = () => {
  currentPage.value = 1
  refresh()
}

const clearFilters = () => {
  filters.value = {
    domain: null,
    minConfidence: 0.0,
    maxConfidence: 1.0,
    fromDate: '',
    toDate: ''
  }
  sortBy.value = 'confidence'
  sortOrder.value = 'desc'
  currentPage.value = 1
  refresh()
}

const goToPage = (page: number) => {
  currentPage.value = page
  refresh()
}

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('en-GB', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Initial load
onMounted(() => {
  refresh()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.slider::-webkit-slider-thumb {
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #14b8a6;
  cursor: pointer;
}

.slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #14b8a6;
  cursor: pointer;
  border: none;
}
</style>

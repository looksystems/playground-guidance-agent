<template>
  <ClientOnly>
    <div class="space-y-6">
      <!-- Header with Breadcrumb -->
      <div class="mb-6">
        <UButton to="/admin" variant="ghost" icon="i-heroicons-arrow-left" color="indigo">
          Back to Dashboard
        </UButton>
        <h1 class="text-3xl font-bold mt-4">Memory Bank</h1>
        <p class="text-gray-600 dark:text-gray-400 mt-2">Agent observations, reflections, and plans</p>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
        <UCard>
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Total Memories</p>
              <p class="mt-2 text-4xl font-bold">{{ stats.total }}</p>
            </div>
            <div class="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
              <UIcon name="i-heroicons-light-bulb-solid" class="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
          </div>
        </UCard>

        <UCard>
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Observations</p>
              <p class="mt-2 text-4xl font-bold">{{ stats.observations }}</p>
            </div>
            <div class="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <UIcon name="i-heroicons-eye-solid" class="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
        </UCard>

        <UCard>
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Reflections</p>
              <p class="mt-2 text-4xl font-bold">{{ stats.reflections }}</p>
            </div>
            <div class="p-3 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg">
              <UIcon name="i-heroicons-sparkles-solid" class="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
            </div>
          </div>
        </UCard>

        <UCard>
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Plans</p>
              <p class="mt-2 text-4xl font-bold">{{ stats.plans }}</p>
            </div>
            <div class="p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
              <UIcon name="i-heroicons-map-solid" class="w-6 h-6 text-orange-600 dark:text-orange-400" />
            </div>
          </div>
        </UCard>
      </div>

      <!-- Filters Bar -->
      <UCard>
        <div class="flex flex-wrap gap-4">
          <!-- Memory Type Filter -->
          <div class="flex-1 min-w-[200px]">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Memory Type</label>
            <USelectMenu
              v-model="filters.memoryType"
              :options="memoryTypeOptions"
              placeholder="All Types"
              @update:model-value="applyFilters"
            />
          </div>

          <!-- Importance Range -->
          <div class="flex-1 min-w-[200px]">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Min Importance: {{ filters.minImportance.toFixed(1) }}
            </label>
            <input
              v-model.number="filters.minImportance"
              type="range"
              min="0"
              max="1"
              step="0.1"
              class="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
              @change="applyFilters"
            />
          </div>

          <div class="flex-1 min-w-[200px]">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Max Importance: {{ filters.maxImportance.toFixed(1) }}
            </label>
            <input
              v-model.number="filters.maxImportance"
              type="range"
              min="0"
              max="1"
              step="0.1"
              class="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
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
        title="Failed to load memories"
        :description="error.message || 'An error occurred while loading the data.'"
        icon="i-heroicons-exclamation-triangle"
      />

      <!-- Loading State -->
      <div v-if="pending" class="flex items-center justify-center py-12">
        <div class="text-center">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
          <p class="mt-4 text-gray-600 dark:text-gray-400">Loading memories...</p>
        </div>
      </div>

      <!-- Empty State -->
      <UCard v-else-if="!items || items.length === 0">
        <div class="text-center py-12">
          <UIcon name="i-heroicons-light-bulb" class="w-16 h-16 text-gray-400 dark:text-gray-600 mx-auto mb-4" />
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">No Memories Found</h3>
          <p class="text-gray-600 dark:text-gray-400">
            {{ filters.memoryType || filters.minImportance > 0 ? 'Try adjusting your filters' : 'No memories have been recorded yet.' }}
          </p>
        </div>
      </UCard>

      <!-- Data Table -->
      <UCard v-else>
        <template #header>
          <div class="flex items-center justify-between">
            <h2 class="text-xl font-semibold">Memories</h2>
            <span class="text-sm text-gray-600 dark:text-gray-400">
              Showing {{ items.length }} of {{ pagination.total }} items
            </span>
          </div>
        </template>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  ID
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Description
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Type
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Importance
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Last Accessed
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Vector
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="item in items" :key="item.id" class="hover:bg-gray-50 dark:hover:bg-gray-800">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900 dark:text-gray-100">
                  {{ item.id.substring(0, 8) }}...
                </td>
                <td class="px-6 py-4 text-sm text-gray-900 dark:text-gray-100 max-w-md">
                  <div class="line-clamp-2">{{ item.description }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <UBadge
                    :color="getMemoryTypeColor(item.memory_type)"
                    variant="subtle"
                  >
                    {{ item.memory_type }}
                  </UBadge>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <div class="flex items-center gap-2">
                    <div class="flex-1 w-20 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div
                        class="h-2 rounded-full transition-all"
                        :class="getImportanceBarColor(item.importance)"
                        :style="{ width: `${item.importance * 100}%` }"
                      ></div>
                    </div>
                    <UBadge
                      :color="getImportanceColor(item.importance)"
                      variant="subtle"
                      size="xs"
                    >
                      {{ item.importance.toFixed(2) }}
                    </UBadge>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                  {{ formatDate(item.last_accessed) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <UBadge
                    :color="item.has_embedding ? 'green' : 'gray'"
                    variant="subtle"
                  >
                    {{ item.has_embedding ? 'Yes' : 'No' }}
                  </UBadge>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <UButton
                    size="xs"
                    @click="navigateTo(`/admin/learning/memories/${item.id}`)"
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
            color="indigo"
            :disabled="pagination.page === 1"
            @click="goToPage(pagination.page - 1)"
          >
            Previous
          </UButton>
          <UButton
            icon="i-heroicons-chevron-right"
            color="indigo"
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
          <UIcon name="i-heroicons-arrow-path" class="w-12 h-12 animate-spin text-gray-400 dark:text-gray-600 mx-auto mb-4" />
          <p class="text-gray-500 dark:text-gray-400">Loading memories...</p>
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
  memoryType: null as string | null,
  minImportance: 0.0,
  maxImportance: 1.0,
  fromDate: '',
  toDate: ''
})

const sortBy = ref('importance')
const sortOrder = ref('desc')
const currentPage = ref(1)
const pageSize = 20

const memoryTypeOptions = ['All Types', 'observation', 'reflection', 'plan']
const sortOptions = ['importance', 'timestamp', 'last_accessed']

// Computed query params
const queryParams = computed(() => {
  const params: any = {
    page: currentPage.value,
    page_size: pageSize,
    sort_by: sortBy.value,
    sort_order: sortOrder.value
  }
  if (filters.value.memoryType && filters.value.memoryType !== 'All Types') {
    params.memory_type = filters.value.memoryType
  }
  if (filters.value.minImportance > 0) params.min_importance = filters.value.minImportance
  if (filters.value.maxImportance < 1) params.max_importance = filters.value.maxImportance
  if (filters.value.fromDate) params.from_date = filters.value.fromDate
  if (filters.value.toDate) params.to_date = filters.value.toDate
  return params
})

// Fetch data
const { data: apiData, pending, error, refresh } = await useFetch('/api/admin/memories', {
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
  observations: apiData.value?.type_counts?.observation || 0,
  reflections: apiData.value?.type_counts?.reflection || 0,
  plans: apiData.value?.type_counts?.plan || 0
}))

// Methods
const getMemoryTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    observation: 'blue',
    reflection: 'indigo',
    plan: 'orange'
  }
  return colors[type] || 'gray'
}

const getImportanceColor = (importance: number) => {
  if (importance > 0.7) return 'indigo'
  if (importance >= 0.4) return 'yellow'
  return 'gray'
}

const getImportanceBarColor = (importance: number) => {
  if (importance > 0.7) return 'bg-indigo-500'
  if (importance >= 0.4) return 'bg-yellow-500'
  return 'bg-gray-400'
}

const applyFilters = () => {
  currentPage.value = 1
  refresh()
}

const clearFilters = () => {
  filters.value = {
    memoryType: null,
    minImportance: 0.0,
    maxImportance: 1.0,
    fromDate: '',
    toDate: ''
  }
  sortBy.value = 'importance'
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
  background: #4f46e5;
  cursor: pointer;
}

.slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #4f46e5;
  cursor: pointer;
  border: none;
}
</style>

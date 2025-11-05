<template>
  <ClientOnly>
    <div class="space-y-6">
      <!-- Header with Breadcrumb -->
      <div class="mb-6">
        <UButton to="/admin" variant="ghost" icon="i-heroicons-arrow-left" color="indigo">
          Back to Dashboard
        </UButton>
        <h1 class="text-3xl font-bold mt-4">Case Library</h1>
        <p class="text-gray-600 mt-2">Customer situations and guidance provided</p>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <UCard>
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Total Cases</p>
              <p class="mt-2 text-4xl font-bold">{{ stats.total }}</p>
            </div>
            <div class="p-3 bg-indigo-50 rounded-lg">
              <UIcon name="i-heroicons-briefcase-solid" class="w-6 h-6 text-indigo-600" />
            </div>
          </div>
        </UCard>

        <UCard>
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Task Types</p>
              <p class="mt-2 text-4xl font-bold">{{ stats.taskTypes }}</p>
            </div>
            <div class="p-3 bg-blue-50 rounded-lg">
              <UIcon name="i-heroicons-tag-solid" class="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </UCard>

        <UCard>
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">With Outcomes</p>
              <p class="mt-2 text-4xl font-bold">{{ stats.withOutcomes }}</p>
            </div>
            <div class="p-3 bg-green-50 rounded-lg">
              <UIcon name="i-heroicons-check-circle-solid" class="w-6 h-6 text-green-600" />
            </div>
          </div>
        </UCard>
      </div>

      <!-- Filters Bar -->
      <UCard>
        <div class="flex flex-wrap gap-4">
          <!-- Task Type Filter -->
          <div class="flex-1 min-w-[200px]">
            <label class="block text-sm font-medium text-gray-700 mb-2">Task Type</label>
            <USelectMenu
              v-model="filters.taskType"
              :options="taskTypeOptions"
              placeholder="All Task Types"
              @update:model-value="applyFilters"
            />
          </div>

          <!-- Date Range -->
          <div class="flex-1 min-w-[200px]">
            <label class="block text-sm font-medium text-gray-700 mb-2">From Date</label>
            <UInput
              v-model="filters.fromDate"
              type="date"
              @update:model-value="applyFilters"
            />
          </div>

          <div class="flex-1 min-w-[200px]">
            <label class="block text-sm font-medium text-gray-700 mb-2">To Date</label>
            <UInput
              v-model="filters.toDate"
              type="date"
              @update:model-value="applyFilters"
            />
          </div>

          <!-- Search -->
          <div class="flex-1 min-w-[300px]">
            <label class="block text-sm font-medium text-gray-700 mb-2">Search</label>
            <UInput
              v-model="filters.search"
              placeholder="Search situations or guidance..."
              icon="i-heroicons-magnifying-glass"
              @update:model-value="debouncedSearch"
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

      <!-- Error State -->
      <UAlert
        v-if="error"
        color="red"
        variant="solid"
        title="Failed to load cases"
        :description="error.message || 'An error occurred while loading the data.'"
        icon="i-heroicons-exclamation-triangle"
      />

      <!-- Loading State -->
      <div v-if="pending" class="flex items-center justify-center py-12">
        <div class="text-center">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
          <p class="mt-4 text-gray-600">Loading cases...</p>
        </div>
      </div>

      <!-- Empty State -->
      <UCard v-else-if="!items || items.length === 0">
        <div class="text-center py-12">
          <UIcon name="i-heroicons-briefcase" class="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 class="text-lg font-semibold text-gray-900 mb-2">No Cases Found</h3>
          <p class="text-gray-600">
            {{ filters.taskType || filters.search ? 'Try adjusting your filters' : 'No cases have been recorded yet.' }}
          </p>
        </div>
      </UCard>

      <!-- Data Table -->
      <UCard v-else>
        <template #header>
          <div class="flex items-center justify-between">
            <h2 class="text-xl font-semibold">Cases</h2>
            <span class="text-sm text-gray-600">
              Showing {{ items.length }} of {{ pagination.total }} items
            </span>
          </div>
        </template>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ID
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Situation
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Task Type
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Guidance
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Vector
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="item in items" :key="item.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">
                  {{ item.id.substring(0, 8) }}...
                </td>
                <td class="px-6 py-4 text-sm text-gray-900 max-w-md">
                  <div class="line-clamp-2">{{ item.customer_situation }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <UBadge color="indigo" variant="subtle">
                    {{ item.task_type || 'General' }}
                  </UBadge>
                </td>
                <td class="px-6 py-4 text-sm text-gray-600 max-w-md">
                  <div class="line-clamp-2">{{ item.guidance_provided }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {{ formatDate(item.created_at) }}
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
                    @click="navigateTo(`/admin/learning/cases/${item.id}`)"
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
        <div class="text-sm text-gray-600">
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
          <UIcon name="i-heroicons-arrow-path" class="w-12 h-12 animate-spin text-gray-400 mx-auto mb-4" />
          <p class="text-gray-500">Loading cases...</p>
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
  taskType: null as string | null,
  fromDate: '',
  toDate: '',
  search: ''
})

const currentPage = ref(1)
const pageSize = 20

// Computed query params
const queryParams = computed(() => {
  const params: any = {
    page: currentPage.value,
    page_size: pageSize
  }
  if (filters.value.taskType && filters.value.taskType !== 'All Task Types') {
    params.task_type = filters.value.taskType
  }
  if (filters.value.search) params.search = filters.value.search
  if (filters.value.fromDate) params.from_date = filters.value.fromDate
  if (filters.value.toDate) params.to_date = filters.value.toDate
  return params
})

// Fetch data
const { data: apiData, pending, error, refresh } = await useFetch('/api/admin/cases', {
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
  taskTypes: apiData.value?.task_types_count || 0,
  withOutcomes: apiData.value?.with_outcomes_count || 0
}))

// Get unique task types for filter
const taskTypeOptions = computed(() => {
  if (!apiData.value?.items) return ['All Task Types']
  const types = new Set(apiData.value.items.map((item: any) => item.task_type).filter(Boolean))
  return ['All Task Types', ...Array.from(types)]
})

// Methods
const applyFilters = () => {
  currentPage.value = 1
  refresh()
}

// Debounced search
let searchTimeout: NodeJS.Timeout
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    applyFilters()
  }, 500)
}

const clearFilters = () => {
  filters.value = {
    taskType: null,
    fromDate: '',
    toDate: '',
    search: ''
  }
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
</style>

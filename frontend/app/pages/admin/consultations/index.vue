<template>
  <ClientOnly>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Consultations</h1>
          <p class="mt-2 text-gray-600 dark:text-gray-400">View and manage all customer consultations</p>
        </div>
        <UButton
          to="/admin"
          variant="outline"
          icon="i-heroicons-arrow-left"
          color="indigo"
        >
          Back to Dashboard
        </UButton>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <UCard>
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-blue-100 rounded-lg p-3">
              <UIcon name="i-heroicons-chat-bubble-left-right" class="w-8 h-8 text-blue-600 dark:text-blue-400" />
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Total Consultations</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ stats.total }}</p>
            </div>
          </div>
        </UCard>

        <UCard>
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-green-100 rounded-lg p-3">
              <UIcon name="i-heroicons-check-circle" class="w-8 h-8 text-green-600 dark:text-green-400" />
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Completed</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ stats.total }}</p>
            </div>
          </div>
        </UCard>

        <UCard>
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-purple-100 rounded-lg p-3">
              <UIcon name="i-heroicons-clock" class="w-8 h-8 text-purple-600 dark:text-purple-400" />
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Avg Duration</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ avgDuration }}m</p>
            </div>
          </div>
        </UCard>
      </div>

      <!-- Filters Bar -->
      <UCard>
        <div class="flex flex-wrap gap-4">
          <!-- Date Range -->
          <div class="flex-1 min-w-[180px]">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">From Date</label>
            <UInput
              v-model="filters.fromDate"
              type="date"
              @update:model-value="applyFilters"
            />
          </div>

          <div class="flex-1 min-w-[180px]">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">To Date</label>
            <UInput
              v-model="filters.toDate"
              type="date"
              @update:model-value="applyFilters"
            />
          </div>

          <!-- Search -->
          <div class="flex-1 min-w-[300px]">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Search</label>
            <UInput
              v-model="filters.search"
              placeholder="Search by customer or topic..."
              icon="i-heroicons-magnifying-glass"
              @update:model-value="debouncedSearch"
            />
          </div>

          <!-- Clear Button -->
          <div class="flex items-end">
            <UButton
              variant="outline"
              color="gray"
              @click="clearFilters"
            >
              Clear Filters
            </UButton>
          </div>
        </div>
      </UCard>

      <!-- Error State -->
      <UAlert
        v-if="error"
        color="red"
        variant="solid"
        title="Failed to load consultations"
        :description="error.message || 'An error occurred while loading the data.'"
        icon="i-heroicons-exclamation-triangle"
      />

      <!-- Loading State -->
      <div v-if="pending" class="flex items-center justify-center py-12">
        <div class="text-center">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          <p class="mt-4 text-gray-600 dark:text-gray-400">Loading consultations...</p>
        </div>
      </div>

      <!-- Empty State -->
      <UCard v-else-if="!transformedItems || transformedItems.length === 0">
        <div class="text-center py-12">
          <UIcon name="i-heroicons-chat-bubble-left-right" class="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">No Consultations Found</h3>
          <p class="text-gray-600 dark:text-gray-400">
            {{ filters.search || filters.fromDate ? 'Try adjusting your filters' : 'No consultations available yet.' }}
          </p>
        </div>
      </UCard>

      <!-- Data Table -->
      <UCard v-else>
        <template #header>
          <div class="flex items-center justify-between">
            <h2 class="text-xl font-semibold">Consultations</h2>
            <span class="text-sm text-gray-600 dark:text-gray-400">{{ pagination.total }} total</span>
          </div>
        </template>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Customer
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Topic
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Duration
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Compliance
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="consultation in transformedItems" :key="consultation.id" class="hover:bg-gray-50 dark:hover:bg-gray-800 dark:bg-gray-800">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ consultation.customer }}</div>
                  <div class="text-sm text-gray-500">Age: {{ consultation.age }}</div>
                </td>
                <td class="px-6 py-4">
                  <div class="text-sm text-gray-900 dark:text-gray-100 max-w-xs truncate">{{ consultation.initial_topic }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900 dark:text-gray-100">
                    {{ formatDate(consultation.start_time) }}
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900 dark:text-gray-100">
                    {{ calculateDuration(consultation.start_time, consultation.end_time) }}m
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="flex-shrink-0 w-24 bg-gray-200 rounded-full h-2 mr-2">
                      <div
                        class="h-2 rounded-full"
                        :class="getComplianceColor(consultation.compliance_score)"
                        :style="{ width: consultation.compliance_score + '%' }"
                      ></div>
                    </div>
                    <span class="text-sm text-gray-900 dark:text-gray-100">{{ Math.round(consultation.compliance_score) }}%</span>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <UButton
                    :to="`/admin/consultations/${consultation.id}`"
                    size="sm"
                    variant="outline"
                    color="indigo"
                  >
                    View
                  </UButton>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <template #footer>
          <div class="flex items-center justify-between">
            <div class="text-sm text-gray-600 dark:text-gray-400">
              Page {{ pagination.page }} of {{ pagination.pages }}
            </div>
            <div class="flex gap-2">
              <UButton
                icon="i-heroicons-chevron-left"
                color="indigo"
                :disabled="pagination.page === 1"
                @click="previousPage"
              >
                Previous
              </UButton>
              <UButton
                icon="i-heroicons-chevron-right"
                color="indigo"
                trailing
                :disabled="pagination.page >= pagination.pages"
                @click="nextPage"
              >
                Next
              </UButton>
            </div>
          </div>
        </template>
      </UCard>
    </div>
  </ClientOnly>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'admin',
})

// Reactive state
const currentPage = ref(1)
const pageSize = 20
const filters = ref({
  fromDate: null as string | null,
  toDate: null as string | null,
  search: '' as string,
})

// Debounced search value
const debouncedSearchValue = ref('')
let searchTimeout: NodeJS.Timeout

// Fetch data using useAsyncData for full control over reactivity
const { data: apiData, pending, error, refresh } = useAsyncData(
  'consultations',
  () => {
    const params: Record<string, any> = {
      page: currentPage.value,
      page_size: pageSize,
    }
    if (filters.value.fromDate) params.from_date = filters.value.fromDate
    if (filters.value.toDate) params.to_date = filters.value.toDate
    if (debouncedSearchValue.value) params.search = debouncedSearchValue.value

    return $fetch('/api/admin/consultations', {
      query: params,
      headers: {
        'Authorization': 'Bearer admin-token'
      },
    })
  },
  {
    watch: [currentPage, () => filters.value.fromDate, () => filters.value.toDate, debouncedSearchValue],
  }
)

// Helper function to extract initial topic
const extractInitialTopic = (item: any): string => {
  // Try to find the first customer message in conversation
  const customerTurn = item.conversation?.find((turn: any) => turn.role === 'customer')
  if (customerTurn?.content) {
    return customerTurn.content.substring(0, 100) + (customerTurn.content.length > 100 ? '...' : '')
  }
  // Fallback to meta.initial_topic if available
  return item.meta?.initial_topic || 'N/A'
}

// Computed properties
const items = computed(() => apiData.value?.items || [])

// Transform API data to match template expectations
const transformedItems = computed(() => {
  return items.value.map((item: any) => ({
    id: item.id,
    customer: item.customer_name,
    age: item.customer_age,
    initial_topic: extractInitialTopic(item),
    start_time: item.created_at,
    end_time: item.ended_at,
    compliance_score: Math.round((item.metrics?.avg_compliance_score || 0) * 100)
  }))
})

const pagination = computed(() => {
  const total = apiData.value?.total || 0
  const limit = apiData.value?.limit || pageSize
  return {
    total,
    page: currentPage.value,
    pages: Math.ceil(total / limit) || 1,
    page_size: limit
  }
})

const stats = computed(() => ({
  total: apiData.value?.total || 0,
}))

const avgDuration = computed(() => {
  if (!transformedItems.value.length) return 0
  const total = transformedItems.value.reduce((sum: number, c: any) => {
    const duration = calculateDuration(c.start_time, c.end_time)
    return sum + (isNaN(duration) ? 0 : duration)
  }, 0)
  return Math.round(total / transformedItems.value.length)
})

// Methods
const applyFilters = () => {
  currentPage.value = 1
  // No need to call refresh() - the watch will handle it automatically
}

// Debounced search - update debounced value after delay
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    debouncedSearchValue.value = filters.value.search
    currentPage.value = 1
  }, 500)
}

const clearFilters = () => {
  filters.value = {
    fromDate: null,
    toDate: null,
    search: '',
  }
  debouncedSearchValue.value = ''
  applyFilters()
}

const nextPage = () => {
  if (currentPage.value < pagination.value.pages) {
    currentPage.value++
    refresh()
  }
}

const previousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    refresh()
  }
}

const formatDate = (dateString: string) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-GB', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const calculateDuration = (start: string, end: string) => {
  if (!start || !end) return 0
  const startTime = new Date(start).getTime()
  const endTime = new Date(end).getTime()
  return Math.round((endTime - startTime) / 1000 / 60)
}

const getComplianceColor = (score: number) => {
  if (score >= 80) return 'bg-green-500'
  if (score >= 60) return 'bg-yellow-500'
  return 'bg-red-500'
}
</script>

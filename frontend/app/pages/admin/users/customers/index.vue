<template>
  <ClientOnly>
    <div class="space-y-6">
      <!-- Header with Breadcrumb -->
      <div class="mb-6">
        <UButton to="/admin" variant="ghost" icon="i-heroicons-arrow-left">
          Back to Dashboard
        </UButton>
        <h1 class="text-3xl font-bold mt-4">Customer Management</h1>
        <p class="text-gray-600 mt-2">View and analyze customer consultation patterns</p>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <UCard>
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Total Customers</p>
              <p class="mt-2 text-4xl font-bold">{{ stats.total_customers }}</p>
            </div>
            <div class="p-3 bg-blue-50 rounded-lg">
              <UIcon name="i-heroicons-users-solid" class="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </UCard>

        <UCard>
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Active Customers</p>
              <p class="text-xs text-gray-500 mt-1">Last 30 days</p>
              <p class="mt-2 text-4xl font-bold">{{ stats.active_customers_30d }}</p>
            </div>
            <div class="p-3 bg-green-50 rounded-lg">
              <UIcon name="i-heroicons-user-group-solid" class="w-6 h-6 text-green-600" />
            </div>
          </div>
        </UCard>

        <UCard>
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600">Avg Consultations</p>
              <p class="text-xs text-gray-500 mt-1">Per customer</p>
              <p class="mt-2 text-4xl font-bold">{{ stats.avg_consultations_per_customer?.toFixed(1) || '0.0' }}</p>
            </div>
            <div class="p-3 bg-purple-50 rounded-lg">
              <UIcon name="i-heroicons-chart-bar-solid" class="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </UCard>
      </div>

      <!-- Filters Bar -->
      <UCard>
        <div class="flex flex-wrap gap-4">
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

          <!-- Search by Customer ID -->
          <div class="flex-1 min-w-[300px]">
            <label class="block text-sm font-medium text-gray-700 mb-2">Search Customer</label>
            <UInput
              v-model="filters.search"
              placeholder="Search by customer ID..."
              icon="i-heroicons-magnifying-glass"
              @update:model-value="debouncedSearch"
            />
          </div>

          <!-- Sort Controls -->
          <div class="flex-1 min-w-[200px]">
            <label class="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
            <USelectMenu
              v-model="filters.sortBy"
              :options="sortOptions"
              @update:model-value="applyFilters"
            />
          </div>

          <div class="flex-1 min-w-[150px]">
            <label class="block text-sm font-medium text-gray-700 mb-2">Order</label>
            <USelectMenu
              v-model="filters.sortOrder"
              :options="['desc', 'asc']"
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

      <!-- Error State -->
      <UAlert
        v-if="error"
        color="red"
        variant="solid"
        title="Failed to load customers"
        :description="error.message || 'An error occurred while loading the data.'"
        icon="i-heroicons-exclamation-triangle"
      />

      <!-- Loading State -->
      <div v-if="pending" class="flex items-center justify-center py-12">
        <div class="text-center">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          <p class="mt-4 text-gray-600">Loading customers...</p>
        </div>
      </div>

      <!-- Empty State -->
      <UCard v-else-if="!items || items.length === 0">
        <div class="text-center py-12">
          <UIcon name="i-heroicons-users" class="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 class="text-lg font-semibold text-gray-900 mb-2">No Customers Found</h3>
          <p class="text-gray-600">
            {{ filters.search || filters.fromDate || filters.toDate ? 'Try adjusting your filters' : 'No customers available yet.' }}
          </p>
        </div>
      </UCard>

      <!-- Data Table -->
      <UCard v-else>
        <template #header>
          <div class="flex items-center justify-between">
            <h2 class="text-xl font-semibold">Customers</h2>
            <span class="text-sm text-gray-600">
              Showing {{ items.length }} of {{ pagination.total }} customers
            </span>
          </div>
        </template>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Customer ID
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total Consultations
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  First Consultation
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Consultation
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg Compliance
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg Satisfaction
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="customer in items" :key="customer.customer_id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center gap-2">
                    <code class="text-sm font-mono text-gray-900">
                      {{ truncateId(customer.customer_id) }}
                    </code>
                    <UButton
                      icon="i-heroicons-clipboard"
                      size="xs"
                      variant="ghost"
                      @click="copyToClipboard(customer.customer_id)"
                    />
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <UBadge color="blue" variant="subtle">
                    {{ customer.total_consultations }}
                  </UBadge>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {{ formatDate(customer.first_consultation) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {{ formatDate(customer.last_consultation) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center gap-2">
                    <div class="flex-1 max-w-[100px]">
                      <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          class="h-full rounded-full transition-all"
                          :class="getComplianceColorClass(customer.avg_compliance_score)"
                          :style="{ width: `${customer.avg_compliance_score * 100}%` }"
                        ></div>
                      </div>
                    </div>
                    <UBadge
                      :color="getComplianceColor(customer.avg_compliance_score)"
                      variant="subtle"
                      size="xs"
                    >
                      {{ (customer.avg_compliance_score * 100).toFixed(0) }}%
                    </UBadge>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  <span v-if="customer.avg_satisfaction !== null && customer.avg_satisfaction !== undefined">
                    {{ customer.avg_satisfaction.toFixed(1) }}/5
                  </span>
                  <span v-else class="text-gray-400">-</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <UButton
                    size="xs"
                    @click="navigateTo(`/admin/users/customers/${customer.customer_id}`)"
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
          <p class="text-gray-500">Loading customers...</p>
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
  fromDate: '',
  toDate: '',
  search: '',
  sortBy: 'total_consultations',
  sortOrder: 'desc' as 'asc' | 'desc'
})

const currentPage = ref(1)
const pageSize = 20

// Sort options
const sortOptions = [
  'total_consultations',
  'last_consultation',
  'avg_compliance_score'
]

// Computed query params
const queryParams = computed(() => {
  const params: any = {
    page: currentPage.value,
    page_size: pageSize,
    sort_by: filters.value.sortBy,
    sort_order: filters.value.sortOrder
  }
  if (filters.value.search) params.customer_id = filters.value.search
  if (filters.value.fromDate) params.from_date = filters.value.fromDate
  if (filters.value.toDate) params.to_date = filters.value.toDate
  return params
})

// Fetch data
const { data: apiData, pending, error, refresh } = await useFetch('/api/admin/customers', {
  query: queryParams,
  headers: {
    'Authorization': 'Bearer admin-token'
  },
  watch: false // We'll manually trigger refresh
})

// Computed data
const items = computed(() => apiData.value?.items || [])
const pagination = computed(() => ({
  total: apiData.value?.total || 0,
  page: apiData.value?.page || 1,
  pages: apiData.value?.pages || 1,
  page_size: apiData.value?.page_size || pageSize
}))

const stats = computed(() => apiData.value?.stats || {
  total_customers: 0,
  active_customers_30d: 0,
  avg_consultations_per_customer: 0
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
    fromDate: '',
    toDate: '',
    search: '',
    sortBy: 'total_consultations',
    sortOrder: 'desc'
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
    day: 'numeric'
  })
}

const truncateId = (id: string) => {
  return id.substring(0, 8) + '...'
}

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    console.log('Copied to clipboard:', text)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

// Color coding for compliance scores
const getComplianceColor = (score: number) => {
  if (score >= 0.8) return 'green'
  if (score >= 0.5) return 'yellow'
  return 'red'
}

const getComplianceColorClass = (score: number) => {
  if (score >= 0.8) return 'bg-green-500'
  if (score >= 0.5) return 'bg-yellow-500'
  return 'bg-red-500'
}

// Initial load
onMounted(() => {
  refresh()
})
</script>

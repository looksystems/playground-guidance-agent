<template>
  <ClientOnly>
    <div class="space-y-6">
      <!-- Header with Breadcrumb -->
      <div class="mb-6">
        <UButton to="/admin" variant="ghost" icon="i-heroicons-arrow-left">
          Back to Dashboard
        </UButton>
        <h1 class="text-3xl font-bold mt-4">FCA Knowledge Base</h1>
        <p class="text-gray-600 dark:text-gray-400 mt-2">Browse and search FCA compliance knowledge</p>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <UCard>
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Total Items</p>
              <p class="mt-2 text-4xl font-bold">{{ stats.total }}</p>
            </div>
            <div class="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <UIcon name="i-heroicons-book-open-solid" class="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
        </UCard>

        <UCard>
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Categories</p>
              <p class="mt-2 text-4xl font-bold">{{ stats.categories }}</p>
            </div>
            <div class="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <UIcon name="i-heroicons-folder-open-solid" class="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
          </div>
        </UCard>
      </div>

      <!-- Filters Bar -->
      <UCard>
        <div class="flex flex-wrap gap-4">
          <!-- Category Filter -->
          <div class="flex-1 min-w-[200px]">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Category</label>
            <USelectMenu
              v-model="filters.category"
              :items="categoryOptions"
              placeholder="All Categories"
              @update:model-value="applyFilters"
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

          <!-- Search -->
          <div class="flex-1 min-w-[300px]">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Search</label>
            <UInput
              v-model="filters.search"
              placeholder="Search content..."
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
        title="Failed to load FCA knowledge"
        :description="error.message || 'An error occurred while loading the data.'"
        icon="i-heroicons-exclamation-triangle"
      />

      <!-- Loading State -->
      <div v-if="pending" class="flex items-center justify-center py-12">
        <div class="text-center">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          <p class="mt-4 text-gray-600 dark:text-gray-400">Loading FCA knowledge...</p>
        </div>
      </div>

      <!-- Empty State -->
      <UCard v-else-if="!items || items.length === 0">
        <div class="text-center py-12">
          <UIcon name="i-heroicons-document-text" class="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">No Knowledge Items Found</h3>
          <p class="text-gray-600 dark:text-gray-400">
            {{ filters.search || filters.category ? 'Try adjusting your filters' : 'No FCA knowledge items available yet.' }}
          </p>
        </div>
      </UCard>

      <!-- Data Table -->
      <UCard v-else>
        <template #header>
          <div class="flex items-center justify-between">
            <h2 class="text-xl font-semibold">Knowledge Items</h2>
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
                  Content
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Source
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
            <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="item in items" :key="item.id" class="hover:bg-gray-50 dark:hover:bg-gray-800 dark:bg-gray-800">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900 dark:text-gray-100">
                  {{ item.id.substring(0, 8) }}...
                </td>
                <td class="px-6 py-4 text-sm text-gray-900 dark:text-gray-100 max-w-md">
                  <div class="line-clamp-2">{{ item.content }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <UBadge color="blue" variant="subtle">
                    {{ item.category || 'Uncategorized' }}
                  </UBadge>
                </td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-400 max-w-xs truncate">
                  {{ item.source || '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
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
                    @click="navigateTo(`/admin/knowledge/fca/${item.id}`)"
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
          <p class="text-gray-500">Loading FCA knowledge...</p>
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
  category: null as string | null,
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
  if (filters.value.category) params.category = filters.value.category
  if (filters.value.search) params.search = filters.value.search
  if (filters.value.fromDate) params.from_date = filters.value.fromDate
  if (filters.value.toDate) params.to_date = filters.value.toDate
  return params
})

// Fetch data
const { data: apiData, pending, error, refresh } = await useFetch('/api/admin/fca-knowledge', {
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

// Get unique categories for filter
const categoryOptions = computed(() => {
  if (!apiData.value?.items || apiData.value.items.length === 0) return []
  const categories = new Set(apiData.value.items.map((item: any) => item.category).filter(Boolean))
  return Array.from(categories).sort()
})

const stats = computed(() => ({
  total: apiData.value?.total || 0,
  categories: categoryOptions.value.length
}))

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
    category: null,
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
    day: 'numeric'
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

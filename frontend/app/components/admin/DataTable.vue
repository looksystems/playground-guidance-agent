<template>
  <div class="data-table">
    <!-- Loading Skeleton -->
    <div v-if="loading" class="space-y-3">
      <USkeleton v-for="i in 5" :key="i" class="h-12 w-full" />
    </div>

    <!-- Empty State -->
    <div
      v-else-if="!data || data.length === 0"
      class="flex flex-col items-center justify-center p-12 text-center border border-gray-200 rounded-lg"
    >
      <UIcon name="i-heroicons-inbox" class="w-16 h-16 text-gray-400 mb-4" />
      <p class="text-gray-600">{{ emptyMessage || 'No data available' }}</p>
    </div>

    <!-- Data Table -->
    <div v-else class="overflow-x-auto border border-gray-200 rounded-lg">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th
              v-for="column in columns"
              :key="column.key"
              scope="col"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              :class="{ 'cursor-pointer hover:bg-gray-100 select-none': column.sortable }"
              @click="column.sortable ? toggleSort(column.key) : null"
            >
              <div class="flex items-center gap-2">
                <span>{{ column.label }}</span>
                <UIcon
                  v-if="column.sortable"
                  :name="getSortIcon(column.key)"
                  class="w-4 h-4"
                  :class="sortKey === column.key ? 'text-primary-600' : 'text-gray-400'"
                />
              </div>
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr
            v-for="(row, index) in sortedData"
            :key="index"
            class="hover:bg-gray-50 transition-colors duration-150"
          >
            <td
              v-for="column in columns"
              :key="column.key"
              class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
            >
              <span v-if="column.formatter">
                {{ column.formatter(row[column.key]) }}
              </span>
              <span v-else>
                {{ row[column.key] }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div
      v-if="!loading && data && data.length > 0 && pagination"
      class="flex items-center justify-between mt-4"
    >
      <div class="text-sm text-gray-700">
        Showing
        <span class="font-medium">{{ startIndex + 1 }}</span>
        to
        <span class="font-medium">{{ Math.min(endIndex, data.length) }}</span>
        of
        <span class="font-medium">{{ data.length }}</span>
        results
      </div>

      <div class="flex items-center gap-2">
        <UButton
          icon="i-heroicons-chevron-left"
          color="gray"
          variant="ghost"
          :disabled="currentPage === 1"
          @click="previousPage"
          aria-label="Previous page"
        />
        <span class="text-sm text-gray-700">
          Page {{ currentPage }} of {{ totalPages }}
        </span>
        <UButton
          icon="i-heroicons-chevron-right"
          color="gray"
          variant="ghost"
          :disabled="currentPage === totalPages"
          @click="nextPage"
          aria-label="Next page"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * DataTable Component
 *
 * A reusable data table component with sorting, pagination, and responsive design.
 * Supports custom column formatters, loading states, and empty states.
 *
 * @component
 * @example
 * ```vue
 * <DataTable
 *   :columns="[
 *     { key: 'name', label: 'Name', sortable: true },
 *     { key: 'email', label: 'Email', sortable: true },
 *     { key: 'created_at', label: 'Created', sortable: true, formatter: (val) => new Date(val).toLocaleDateString() }
 *   ]"
 *   :data="users"
 *   :loading="loading"
 *   :pagination="true"
 *   :page-size="10"
 *   empty-message="No users found"
 * />
 * ```
 */

interface Column {
  /** Unique key for the column, matching the data object property */
  key: string
  /** Display label for the column header */
  label: string
  /** Whether the column can be sorted */
  sortable?: boolean
  /** Optional formatter function to transform the cell value */
  formatter?: (value: any) => string
}

interface Props {
  /** Array of column definitions */
  columns: Column[]
  /** Array of data objects to display */
  data: any[]
  /** Whether the table is in a loading state */
  loading?: boolean
  /** Message to display when there is no data */
  emptyMessage?: string
  /** Enable pagination */
  pagination?: boolean
  /** Number of rows per page (only applies when pagination is enabled) */
  pageSize?: number
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  emptyMessage: 'No data available',
  pagination: false,
  pageSize: 10,
})

// Sorting state
const sortKey = ref<string | null>(null)
const sortDirection = ref<'asc' | 'desc'>('asc')

// Pagination state
const currentPage = ref(1)

/**
 * Toggle sort for a column
 */
const toggleSort = (key: string) => {
  if (sortKey.value === key) {
    // Toggle direction if same column
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    // Set new column and default to ascending
    sortKey.value = key
    sortDirection.value = 'asc'
  }
  // Reset to first page when sorting changes
  currentPage.value = 1
}

/**
 * Get the appropriate sort icon for a column
 */
const getSortIcon = (key: string): string => {
  if (sortKey.value !== key) {
    return 'i-heroicons-arrows-up-down'
  }
  return sortDirection.value === 'asc'
    ? 'i-heroicons-chevron-up'
    : 'i-heroicons-chevron-down'
}

/**
 * Computed sorted data
 */
const sortedData = computed(() => {
  if (!props.data || props.data.length === 0) return []

  let result = [...props.data]

  // Apply sorting
  if (sortKey.value) {
    result.sort((a, b) => {
      const aVal = a[sortKey.value!]
      const bVal = b[sortKey.value!]

      if (aVal === bVal) return 0

      let comparison = 0
      if (aVal < bVal) comparison = -1
      if (aVal > bVal) comparison = 1

      return sortDirection.value === 'asc' ? comparison : -comparison
    })
  }

  // Apply pagination
  if (props.pagination) {
    const start = (currentPage.value - 1) * props.pageSize
    const end = start + props.pageSize
    result = result.slice(start, end)
  }

  return result
})

/**
 * Pagination computed properties
 */
const totalPages = computed(() => {
  if (!props.pagination || !props.data) return 1
  return Math.ceil(props.data.length / props.pageSize)
})

const startIndex = computed(() => {
  if (!props.pagination) return 0
  return (currentPage.value - 1) * props.pageSize
})

const endIndex = computed(() => {
  if (!props.pagination) return props.data?.length || 0
  return currentPage.value * props.pageSize
})

/**
 * Navigate to previous page
 */
const previousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

/**
 * Navigate to next page
 */
const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

/**
 * Reset pagination when data changes
 */
watch(() => props.data, () => {
  currentPage.value = 1
})
</script>

<style scoped>
.data-table {
  @apply w-full;
}

/* Ensure table is responsive on small screens */
@media (max-width: 640px) {
  .data-table table {
    @apply text-xs;
  }

  .data-table td,
  .data-table th {
    @apply px-3 py-2;
  }
}
</style>

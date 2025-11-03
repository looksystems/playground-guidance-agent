<template>
  <div class="filter-bar bg-white border border-gray-200 rounded-lg p-4">
    <div class="flex flex-wrap items-end gap-4">
      <!-- Filter Controls -->
      <div
        v-for="filter in filters"
        :key="filter.key"
        class="flex-1 min-w-[200px]"
      >
        <!-- Text Filter -->
        <div v-if="filter.type === 'text'">
          <label
            :for="`filter-${filter.key}`"
            class="block text-sm font-medium text-gray-700 mb-1"
          >
            {{ filter.label }}
          </label>
          <UInput
            :id="`filter-${filter.key}`"
            v-model="filterValues[filter.key]"
            :placeholder="`Filter by ${filter.label.toLowerCase()}...`"
            icon="i-heroicons-magnifying-glass"
            @input="handleFilterChange(filter.key, $event.target.value)"
          />
        </div>

        <!-- Select Filter -->
        <div v-if="filter.type === 'select'">
          <label
            :for="`filter-${filter.key}`"
            class="block text-sm font-medium text-gray-700 mb-1"
          >
            {{ filter.label }}
          </label>
          <USelectMenu
            :id="`filter-${filter.key}`"
            v-model="filterValues[filter.key]"
            :options="filter.options || []"
            value-attribute="value"
            option-attribute="label"
            placeholder="Select..."
            @update:model-value="handleFilterChange(filter.key, $event)"
          />
        </div>

        <!-- Date Range Filter -->
        <div v-if="filter.type === 'date-range'">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            {{ filter.label }}
          </label>
          <div class="flex gap-2">
            <UInput
              v-model="filterValues[`${filter.key}_start`]"
              type="date"
              placeholder="Start date"
              @change="handleDateRangeChange(filter.key)"
            />
            <UInput
              v-model="filterValues[`${filter.key}_end`]"
              type="date"
              placeholder="End date"
              @change="handleDateRangeChange(filter.key)"
            />
          </div>
        </div>

        <!-- Slider Filter -->
        <div v-if="filter.type === 'slider'">
          <label
            :for="`filter-${filter.key}`"
            class="block text-sm font-medium text-gray-700 mb-1"
          >
            {{ filter.label }}: {{ filterValues[filter.key] ?? filter.min ?? 0 }}
          </label>
          <input
            :id="`filter-${filter.key}`"
            v-model.number="filterValues[filter.key]"
            type="range"
            :min="filter.min ?? 0"
            :max="filter.max ?? 100"
            :step="filter.step ?? 1"
            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
            @input="handleFilterChange(filter.key, filterValues[filter.key])"
          />
          <div class="flex justify-between text-xs text-gray-500 mt-1">
            <span>{{ filter.min ?? 0 }}</span>
            <span>{{ filter.max ?? 100 }}</span>
          </div>
        </div>
      </div>

      <!-- Clear All Button -->
      <div class="flex items-center gap-2">
        <UButton
          v-if="activeFilterCount > 0"
          color="gray"
          variant="ghost"
          icon="i-heroicons-x-mark"
          @click="clearAllFilters"
        >
          Clear All
          <UBadge
            v-if="activeFilterCount > 0"
            color="primary"
            class="ml-2"
            :label="activeFilterCount.toString()"
          />
        </UButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * FilterBar Component
 *
 * A reusable filter bar component supporting multiple filter types including
 * text search, select dropdowns, date ranges, and sliders.
 *
 * @component
 * @example
 * ```vue
 * <FilterBar
 *   :filters="[
 *     { type: 'text', key: 'search', label: 'Search' },
 *     { type: 'select', key: 'status', label: 'Status', options: [
 *       { label: 'Active', value: 'active' },
 *       { label: 'Inactive', value: 'inactive' }
 *     ]},
 *     { type: 'date-range', key: 'created', label: 'Created Date' },
 *     { type: 'slider', key: 'score', label: 'Score', min: 0, max: 100, step: 10 }
 *   ]"
 *   @filter-change="handleFilterChange"
 * />
 * ```
 */

interface FilterOption {
  /** Display label for the option */
  label: string
  /** Value for the option */
  value: any
}

interface Filter {
  /** Type of filter control */
  type: 'select' | 'date-range' | 'text' | 'slider'
  /** Unique key for the filter */
  key: string
  /** Display label for the filter */
  label: string
  /** Options for select filters */
  options?: FilterOption[]
  /** Minimum value for slider filters */
  min?: number
  /** Maximum value for slider filters */
  max?: number
  /** Step value for slider filters */
  step?: number
}

interface Props {
  /** Array of filter configurations */
  filters: Filter[]
}

interface Emits {
  (event: 'filter-change', payload: { key: string; value: any }): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

/**
 * Reactive object to store all filter values
 */
const filterValues = reactive<Record<string, any>>({})

/**
 * Initialize filter values with defaults
 */
onMounted(() => {
  props.filters.forEach((filter) => {
    if (filter.type === 'slider') {
      filterValues[filter.key] = filter.min ?? 0
    } else if (filter.type === 'date-range') {
      filterValues[`${filter.key}_start`] = ''
      filterValues[`${filter.key}_end`] = ''
    } else {
      filterValues[filter.key] = ''
    }
  })
})

/**
 * Count of active filters (filters with non-empty values)
 */
const activeFilterCount = computed(() => {
  let count = 0

  props.filters.forEach((filter) => {
    if (filter.type === 'date-range') {
      if (filterValues[`${filter.key}_start`] || filterValues[`${filter.key}_end`]) {
        count++
      }
    } else if (filter.type === 'slider') {
      // Only count if not at default/min value
      if (filterValues[filter.key] !== (filter.min ?? 0)) {
        count++
      }
    } else {
      if (filterValues[filter.key]) {
        count++
      }
    }
  })

  return count
})

/**
 * Handle filter value change and emit event
 */
const handleFilterChange = (key: string, value: any) => {
  emit('filter-change', { key, value })
}

/**
 * Handle date range filter changes
 */
const handleDateRangeChange = (key: string) => {
  const startDate = filterValues[`${key}_start`]
  const endDate = filterValues[`${key}_end`]

  emit('filter-change', {
    key,
    value: {
      start: startDate,
      end: endDate,
    },
  })
}

/**
 * Clear all filter values
 */
const clearAllFilters = () => {
  props.filters.forEach((filter) => {
    if (filter.type === 'slider') {
      filterValues[filter.key] = filter.min ?? 0
      handleFilterChange(filter.key, filter.min ?? 0)
    } else if (filter.type === 'date-range') {
      filterValues[`${filter.key}_start`] = ''
      filterValues[`${filter.key}_end`] = ''
      handleFilterChange(filter.key, { start: '', end: '' })
    } else {
      filterValues[filter.key] = ''
      handleFilterChange(filter.key, '')
    }
  })
}
</script>

<style scoped>
.filter-bar {
  @apply w-full;
}

/* Responsive layout for smaller screens */
@media (max-width: 768px) {
  .filter-bar .flex-1 {
    @apply min-w-full;
  }
}

/* Custom slider styling */
input[type='range']::-webkit-slider-thumb {
  @apply appearance-none w-4 h-4 rounded-full bg-primary-600 cursor-pointer;
}

input[type='range']::-moz-range-thumb {
  @apply w-4 h-4 rounded-full bg-primary-600 cursor-pointer border-0;
}
</style>

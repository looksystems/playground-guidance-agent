<template>
  <UCard>
    <!-- Card Header -->
    <template #header>
      <h3 class="text-lg font-semibold text-gray-900">
        {{ title }}
      </h3>
    </template>

    <!-- Card Body -->
    <div class="space-y-4">
      <div
        v-for="(field, index) in fields"
        :key="index"
        class="detail-field"
        :class="{ 'border-t border-gray-100 pt-4': index > 0 }"
      >
        <div class="grid grid-cols-1 md:grid-cols-3 gap-2">
          <!-- Field Label -->
          <dt class="text-sm font-medium text-gray-500">
            {{ field.label }}
          </dt>

          <!-- Field Value -->
          <dd class="md:col-span-2 text-sm text-gray-900">
            <!-- Text Type (Default) -->
            <div v-if="!field.type || field.type === 'text'" class="flex items-center gap-2">
              <span>{{ field.value }}</span>
              <!-- Copy to clipboard for ID-like fields -->
              <UButton
                v-if="isIdField(field.label)"
                icon="i-heroicons-clipboard-document"
                color="gray"
                variant="ghost"
                size="xs"
                @click="copyToClipboard(field.value)"
                :aria-label="`Copy ${field.label}`"
              />
            </div>

            <!-- Date Type -->
            <div v-else-if="field.type === 'date'">
              {{ formatDate(field.value) }}
            </div>

            <!-- Badge Type -->
            <div v-else-if="field.type === 'badge'">
              <UBadge
                :color="getBadgeColor(field.value)"
                variant="subtle"
              >
                {{ field.value }}
              </UBadge>
            </div>

            <!-- Meter Type (Progress Bar) -->
            <div v-else-if="field.type === 'meter'" class="space-y-1">
              <div class="flex items-center justify-between text-xs">
                <span>{{ field.value }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="h-2 rounded-full transition-all duration-300"
                  :class="getMeterColor(field.value)"
                  :style="{ width: `${Math.min(100, Math.max(0, field.value))}%` }"
                  role="progressbar"
                  :aria-valuenow="field.value"
                  aria-valuemin="0"
                  aria-valuemax="100"
                />
              </div>
            </div>

            <!-- JSON Type (Collapsible) -->
            <div v-else-if="field.type === 'json'">
              <UButton
                v-if="!expandedFields[index]"
                color="gray"
                variant="ghost"
                size="xs"
                icon="i-heroicons-chevron-right"
                @click="toggleField(index)"
              >
                Show JSON
              </UButton>
              <div v-else class="space-y-2">
                <UButton
                  color="gray"
                  variant="ghost"
                  size="xs"
                  icon="i-heroicons-chevron-down"
                  @click="toggleField(index)"
                >
                  Hide JSON
                </UButton>
                <div class="relative">
                  <pre class="bg-gray-50 border border-gray-200 rounded-lg p-3 overflow-x-auto text-xs">{{
                    formatJSON(field.value)
                  }}</pre>
                  <UButton
                    icon="i-heroicons-clipboard-document"
                    color="gray"
                    variant="ghost"
                    size="xs"
                    class="absolute top-2 right-2"
                    @click="copyToClipboard(formatJSON(field.value))"
                    aria-label="Copy JSON"
                  />
                </div>
              </div>
            </div>
          </dd>
        </div>
      </div>
    </div>
  </UCard>
</template>

<script setup lang="ts">
/**
 * DetailCard Component
 *
 * A reusable card component for displaying detailed information with
 * support for various field types including text, dates, badges, progress meters, and JSON.
 *
 * @component
 * @example
 * ```vue
 * <DetailCard
 *   title="User Details"
 *   :fields="[
 *     { label: 'User ID', value: '12345', type: 'text' },
 *     { label: 'Name', value: 'John Doe' },
 *     { label: 'Status', value: 'active', type: 'badge' },
 *     { label: 'Progress', value: 75, type: 'meter' },
 *     { label: 'Created', value: '2024-01-01T00:00:00Z', type: 'date' },
 *     { label: 'Metadata', value: { key: 'value' }, type: 'json' }
 *   ]"
 * />
 * ```
 */

interface Field {
  /** Display label for the field */
  label: string
  /** Value of the field */
  value: any
  /** Type of field display (text, json, date, badge, meter) */
  type?: 'text' | 'json' | 'date' | 'badge' | 'meter'
}

interface Props {
  /** Title displayed in the card header */
  title: string
  /** Array of field configurations */
  fields: Field[]
}

const props = defineProps<Props>()

/**
 * Toast notification composable
 */
const toast = useToast()

/**
 * Track which JSON fields are expanded
 */
const expandedFields = reactive<Record<number, boolean>>({})

/**
 * Toggle JSON field expansion
 */
const toggleField = (index: number) => {
  expandedFields[index] = !expandedFields[index]
}

/**
 * Check if a field label indicates it's an ID field
 */
const isIdField = (label: string): boolean => {
  const lowerLabel = label.toLowerCase()
  return lowerLabel.includes('id') || lowerLabel.includes('key') || lowerLabel.includes('uuid')
}

/**
 * Format a date value for display
 */
const formatDate = (value: any): string => {
  if (!value) return 'N/A'

  try {
    const date = new Date(value)
    if (isNaN(date.getTime())) return value

    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date)
  } catch {
    return value
  }
}

/**
 * Format JSON for display
 */
const formatJSON = (value: any): string => {
  if (typeof value === 'string') {
    try {
      return JSON.stringify(JSON.parse(value), null, 2)
    } catch {
      return value
    }
  }
  return JSON.stringify(value, null, 2)
}

/**
 * Get badge color based on value
 */
const getBadgeColor = (value: any): string => {
  const strValue = String(value).toLowerCase()

  if (strValue === 'active' || strValue === 'success' || strValue === 'completed') {
    return 'green'
  }
  if (strValue === 'inactive' || strValue === 'error' || strValue === 'failed') {
    return 'red'
  }
  if (strValue === 'pending' || strValue === 'warning') {
    return 'yellow'
  }
  if (strValue === 'processing' || strValue === 'info') {
    return 'blue'
  }

  return 'gray'
}

/**
 * Get meter color based on percentage value
 */
const getMeterColor = (value: number): string => {
  if (value >= 80) return 'bg-green-500'
  if (value >= 60) return 'bg-blue-500'
  if (value >= 40) return 'bg-yellow-500'
  if (value >= 20) return 'bg-orange-500'
  return 'bg-red-500'
}

/**
 * Copy text to clipboard
 */
const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    toast.add({
      title: 'Copied to clipboard',
      icon: 'i-heroicons-check-circle',
      color: 'green',
    })
  } catch (error) {
    toast.add({
      title: 'Failed to copy',
      icon: 'i-heroicons-x-circle',
      color: 'red',
    })
  }
}
</script>

<style scoped>
.detail-field {
  @apply transition-all duration-150;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .detail-field .grid {
    @apply grid-cols-1 gap-1;
  }

  .detail-field dt {
    @apply font-semibold;
  }
}

/* JSON pre formatting */
pre {
  font-family: 'Courier New', Courier, monospace;
  line-height: 1.5;
}
</style>

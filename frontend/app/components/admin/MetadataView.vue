<template>
  <div class="metadata-view">
    <!-- Collapsible Header -->
    <div
      v-if="collapsible"
      class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-t-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
      @click="toggleExpanded"
    >
      <div class="flex items-center gap-2">
        <UIcon
          :name="isExpanded ? 'i-heroicons-chevron-down' : 'i-heroicons-chevron-right'"
          class="w-5 h-5 text-gray-600 dark:text-gray-400"
        />
        <h4 class="text-sm font-semibold text-gray-900 dark:text-gray-100">
          {{ title }}
        </h4>
        <UBadge
          v-if="!isExpanded && keyCount > 0"
          color="gray"
          variant="subtle"
          size="xs"
        >
          {{ keyCount }} {{ keyCount === 1 ? 'key' : 'keys' }}
        </UBadge>
      </div>

      <UButton
        v-if="isExpanded"
        icon="i-heroicons-clipboard-document"
        color="gray"
        variant="ghost"
        size="xs"
        @click.stop="copyJSON"
        aria-label="Copy JSON"
      />
    </div>

    <!-- Metadata Content -->
    <div
      v-show="!collapsible || isExpanded"
      class="metadata-content relative"
      :class="{ 'rounded-lg': !collapsible, 'rounded-b-lg': collapsible }"
    >
      <!-- Empty State -->
      <div
        v-if="isEmpty"
        class="flex items-center justify-center p-8 text-gray-500 dark:text-gray-400 text-sm bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700"
        :class="{ 'rounded-lg': !collapsible, 'rounded-b-lg': collapsible }"
      >
        <UIcon name="i-heroicons-document-text" class="w-5 h-5 mr-2" />
        <span>No metadata available</span>
      </div>

      <!-- JSON Display -->
      <div
        v-else
        class="relative"
      >
        <pre
          class="bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 p-4 overflow-x-auto text-sm leading-relaxed border border-gray-200 dark:border-gray-700"
          :class="{ 'rounded-lg': !collapsible, 'rounded-b-lg': collapsible }"
        ><code v-html="highlightedJSON"></code></pre>

        <!-- Copy Button (for non-collapsible) -->
        <UButton
          v-if="!collapsible"
          icon="i-heroicons-clipboard-document"
          color="gray"
          variant="solid"
          size="xs"
          class="absolute top-2 right-2 opacity-70 hover:opacity-100 transition-opacity"
          @click="copyJSON"
          aria-label="Copy JSON"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * MetadataView Component
 *
 * A component for displaying JSON metadata with syntax highlighting,
 * collapsible sections, and copy-to-clipboard functionality.
 *
 * @component
 * @example
 * ```vue
 * <MetadataView
 *   title="User Metadata"
 *   :data="{ role: 'admin', preferences: { theme: 'dark' } }"
 *   :collapsible="true"
 * />
 * ```
 */

interface Props {
  /** JSON data to display */
  data: object | null | undefined
  /** Whether the metadata view can be collapsed */
  collapsible?: boolean
  /** Title for the collapsible header */
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  collapsible: false,
  title: 'Metadata',
})

/**
 * Toast notification composable
 */
const toast = useToast()

/**
 * Track expanded state for collapsible view
 */
const isExpanded = ref(!props.collapsible)

/**
 * Check if data is empty
 */
const isEmpty = computed(() => {
  if (!props.data) return true
  if (typeof props.data !== 'object') return true
  return Object.keys(props.data).length === 0
})

/**
 * Count of keys in the data object
 */
const keyCount = computed(() => {
  if (!props.data || typeof props.data !== 'object') return 0
  return Object.keys(props.data).length
})

/**
 * Formatted JSON string
 */
const formattedJSON = computed(() => {
  if (isEmpty.value) return ''

  try {
    return JSON.stringify(props.data, null, 2)
  } catch (error) {
    console.error('Error formatting JSON:', error)
    return String(props.data)
  }
})

/**
 * Syntax highlighted JSON
 * Simple syntax highlighting using regex replacements with dark mode support
 */
const colorMode = useColorMode()

const highlightedJSON = computed(() => {
  if (isEmpty.value) return ''

  let json = formattedJSON.value

  // Escape HTML
  json = json.replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  const isDark = colorMode.value === 'dark'

  // Highlight different JSON elements with adaptive colors
  json = json
    // String values (but not keys)
    .replace(/: ("(?:[^"\\]|\\.)*")/g, isDark
      ? ': <span class="text-green-400">$1</span>'
      : ': <span class="text-green-700">$1</span>')
    // Keys
    .replace(/("(?:[^"\\]|\\.)*"):/g, isDark
      ? '<span class="text-blue-400">$1</span>:'
      : '<span class="text-blue-700">$1</span>:')
    // Numbers
    .replace(/: (-?\d+\.?\d*)/g, isDark
      ? ': <span class="text-yellow-400">$1</span>'
      : ': <span class="text-orange-600">$1</span>')
    // Booleans
    .replace(/: (true|false)/g, isDark
      ? ': <span class="text-purple-400">$1</span>'
      : ': <span class="text-purple-700">$1</span>')
    // Null
    .replace(/: (null)/g, isDark
      ? ': <span class="text-red-400">$1</span>'
      : ': <span class="text-red-700">$1</span>')

  return json
})

/**
 * Toggle expanded state
 */
const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

/**
 * Copy JSON to clipboard
 */
const copyJSON = async () => {
  try {
    await navigator.clipboard.writeText(formattedJSON.value)
    toast.add({
      title: 'JSON copied to clipboard',
      icon: 'i-heroicons-check-circle',
      color: 'green',
    })
  } catch (error) {
    console.error('Error copying JSON:', error)
    toast.add({
      title: 'Failed to copy JSON',
      description: 'Please try again',
      icon: 'i-heroicons-x-circle',
      color: 'red',
    })
  }
}

/**
 * Watch for data changes and reset expanded state
 */
watch(() => props.data, () => {
  if (!props.collapsible) {
    isExpanded.value = true
  }
})
</script>

<style scoped>
.metadata-view {
  @apply w-full;
}

.metadata-content pre {
  font-family: 'Fira Code', 'Courier New', Courier, monospace;
  line-height: 1.6;
  max-height: 500px;
  overflow-y: auto;
}

/* Custom scrollbar for better aesthetics */
.metadata-content pre::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.metadata-content pre::-webkit-scrollbar-track {
  @apply bg-gray-200 dark:bg-gray-800;
  border-radius: 4px;
}

.metadata-content pre::-webkit-scrollbar-thumb {
  @apply bg-gray-400 dark:bg-gray-600;
  border-radius: 4px;
}

.metadata-content pre::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-500 dark:bg-gray-500;
}

/* Responsive font sizing */
@media (max-width: 640px) {
  .metadata-content pre {
    @apply text-xs;
  }
}

/* Animation for expand/collapse */
.metadata-content {
  transition: all 0.3s ease-in-out;
}
</style>

<template>
  <div>
    <!-- Breadcrumb and Back Button -->
    <div class="mb-6">
      <UButton
        to="/admin/learning/memories"
        variant="ghost"
        icon="i-heroicons-arrow-left"
      >
        Back to Memories
      </UButton>
      <div class="flex items-center gap-2 mt-4">
        <UButton to="/admin" variant="ghost" size="xs">Admin</UButton>
        <span class="text-gray-400">/</span>
        <UButton to="/admin/learning/memories" variant="ghost" size="xs">Memories</UButton>
        <span class="text-gray-400">/</span>
        <span class="text-sm text-gray-600 dark:text-gray-400">{{ id.substring(0, 8) }}...</span>
      </div>
      <h1 class="text-3xl font-bold mt-4">Memory Detail</h1>
    </div>

    <!-- Loading State -->
    <div v-if="pending" class="flex items-center justify-center py-12">
      <div class="text-center">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
        <p class="mt-4 text-gray-600 dark:text-gray-400">Loading memory...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
      <h2 class="text-lg font-semibold text-red-800 dark:text-red-400 mb-2">Error Loading Memory</h2>
      <p class="text-red-600 dark:text-red-400">
        {{ error.statusCode === 404 ? 'Memory not found.' : (error.message || 'Failed to load memory. Please try again.') }}
      </p>
      <UButton class="mt-4" @click="refresh">
        Retry
      </UButton>
    </div>

    <!-- No Data State -->
    <div v-else-if="!item" class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6">
      <h2 class="text-lg font-semibold text-yellow-800 dark:text-yellow-400 mb-2">No Data Available</h2>
      <p class="text-yellow-600 dark:text-yellow-400">This memory does not have any data.</p>
    </div>

    <!-- Main Content -->
    <div v-else class="space-y-6">
      <!-- Main Content Card -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h2 class="text-xl font-semibold">Memory Details</h2>
            <div class="flex items-center gap-2">
              <UBadge
                :color="getMemoryTypeColor(item.memory_type)"
                variant="subtle"
              >
                {{ item.memory_type }}
              </UBadge>
              <UBadge
                :color="item.has_embedding ? 'green' : 'gray'"
                variant="subtle"
              >
                {{ item.has_embedding ? 'Vectorized' : 'No Vector' }}
              </UBadge>
            </div>
          </div>
        </template>

        <div class="space-y-6">
          <!-- ID with Copy -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">ID</label>
            <div class="flex items-center gap-2">
              <code class="flex-1 px-3 py-2 bg-gray-50 dark:bg-gray-800 rounded font-mono text-sm">
                {{ item.id }}
              </code>
              <UButton
                icon="i-heroicons-clipboard"
                size="sm"
                variant="outline"
                @click="copyToClipboard(item.id)"
              >
                Copy
              </UButton>
            </div>
          </div>

          <!-- Description -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Description</label>
            <div class="px-4 py-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <p class="text-gray-900 dark:text-gray-100 whitespace-pre-wrap">{{ item.description }}</p>
            </div>
          </div>

          <!-- Memory Type -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Memory Type</label>
            <UBadge
              :color="getMemoryTypeColor(item.memory_type)"
              variant="subtle"
              size="lg"
            >
              <span class="capitalize">{{ item.memory_type }}</span>
            </UBadge>
          </div>

          <!-- Importance Score -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Importance Score: {{ item.importance.toFixed(3) }}
            </label>
            <div class="space-y-2">
              <div class="w-full bg-gray-200 rounded-full h-6">
                <div
                  class="h-6 rounded-full transition-all flex items-center justify-end pr-2"
                  :class="getImportanceBarColor(item.importance)"
                  :style="{ width: `${item.importance * 100}%` }"
                >
                  <span class="text-xs font-semibold text-white">
                    {{ (item.importance * 100).toFixed(1) }}%
                  </span>
                </div>
              </div>
              <div class="flex justify-between text-xs text-gray-600 dark:text-gray-400">
                <span>Low (0.0)</span>
                <span>Medium (0.5)</span>
                <span>High (1.0)</span>
              </div>
              <UBadge
                :color="getImportanceColor(item.importance)"
                variant="subtle"
              >
                {{ getImportanceLabel(item.importance) }}
              </UBadge>
            </div>
          </div>

          <!-- Vector Embedding Status -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Vector Embedding</label>
            <div class="flex items-center gap-3">
              <UIcon
                :name="item.has_embedding ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'"
                :class="item.has_embedding ? 'text-green-600 dark:text-green-400' : 'text-gray-400'"
                class="w-6 h-6"
              />
              <span :class="item.has_embedding ? 'text-green-700 dark:text-green-400' : 'text-gray-600 dark:text-gray-400'">
                {{ item.has_embedding ? 'Vector embedding present (1536 dimensions)' : 'No vector embedding available' }}
              </span>
            </div>
          </div>
        </div>
      </UCard>

      <!-- Timestamps Card -->
      <UCard>
        <template #header>
          <h2 class="text-xl font-semibold">Timeline</h2>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Created</label>
            <div class="flex items-center gap-2 text-gray-900 dark:text-gray-100">
              <UIcon name="i-heroicons-calendar" class="w-5 h-5 text-gray-400" />
              {{ formatDate(item.timestamp) }}
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Last Accessed</label>
            <div class="flex items-center gap-2 text-gray-900 dark:text-gray-100">
              <UIcon name="i-heroicons-clock" class="w-5 h-5 text-gray-400" />
              {{ formatDate(item.last_accessed_at) }}
            </div>
          </div>
        </div>
      </UCard>

      <!-- Metadata Section -->
      <UCard v-if="item.meta && Object.keys(item.meta).length > 0">
        <template #header>
          <h2 class="text-xl font-semibold">Metadata</h2>
        </template>

        <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
          <pre class="text-sm text-gray-900 dark:text-gray-100 overflow-x-auto">{{ JSON.stringify(item.meta, null, 2) }}</pre>
        </div>
      </UCard>

      <!-- Additional Information -->
      <UCard>
        <template #header>
          <h2 class="text-xl font-semibold">Technical Information</h2>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Description Length</label>
            <p class="text-gray-900 dark:text-gray-100">{{ item.description.length }} characters</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Estimated Tokens</label>
            <p class="text-gray-900 dark:text-gray-100">~{{ Math.ceil(item.description.length / 4) }} tokens</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Word Count</label>
            <p class="text-gray-900 dark:text-gray-100">{{ item.description.split(/\s+/).length }} words</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Status</label>
            <UBadge
              :color="item.has_embedding ? 'green' : 'yellow'"
              variant="subtle"
            >
              {{ item.has_embedding ? 'Ready for Retrieval' : 'Needs Embedding' }}
            </UBadge>
          </div>
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'admin'
})

const route = useRoute()
const id = computed(() => route.params.id as string)

// Fetch memory data
const { data: apiData, pending, error, refresh } = await useFetch(`/api/admin/memories/${id.value}`, {
  headers: {
    'Authorization': 'Bearer admin-token'
  }
})

const item = computed(() => apiData.value)

// Methods
const getMemoryTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    observation: 'blue',
    reflection: 'green',
    plan: 'orange'
  }
  return colors[type] || 'gray'
}

const getImportanceColor = (importance: number) => {
  if (importance > 0.7) return 'green'
  if (importance >= 0.4) return 'yellow'
  return 'gray'
}

const getImportanceBarColor = (importance: number) => {
  if (importance > 0.7) return 'bg-green-500'
  if (importance >= 0.4) return 'bg-yellow-500'
  return 'bg-gray-400'
}

const getImportanceLabel = (importance: number) => {
  if (importance > 0.7) return 'High Importance'
  if (importance >= 0.4) return 'Medium Importance'
  return 'Low Importance'
}

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('en-GB', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    console.log('Copied to clipboard:', text)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}
</script>

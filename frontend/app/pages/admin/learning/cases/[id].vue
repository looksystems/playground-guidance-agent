<template>
  <div>
    <!-- Breadcrumb and Back Button -->
    <div class="mb-6">
      <UButton
        to="/admin/learning/cases"
        variant="ghost"
        icon="i-heroicons-arrow-left"
      >
        Back to Cases
      </UButton>
      <div class="flex items-center gap-2 mt-4">
        <UButton to="/admin" variant="ghost" size="xs" color="indigo">Admin</UButton>
        <span class="text-gray-400">/</span>
        <UButton to="/admin/learning/cases" variant="ghost" size="xs" color="indigo">Cases</UButton>
        <span class="text-gray-400">/</span>
        <span class="text-sm text-gray-600 dark:text-gray-400">{{ id.substring(0, 8) }}...</span>
      </div>
      <h1 class="text-3xl font-bold mt-4">Case Detail</h1>
    </div>

    <!-- Loading State -->
    <div v-if="pending" class="flex items-center justify-center py-12">
      <div class="text-center">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
        <p class="mt-4 text-gray-600 dark:text-gray-400">Loading case...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
      <h2 class="text-lg font-semibold text-red-800 dark:text-red-400 mb-2">Error Loading Case</h2>
      <p class="text-red-600 dark:text-red-400">
        {{ error.statusCode === 404 ? 'Case not found.' : (error.message || 'Failed to load case. Please try again.') }}
      </p>
      <UButton class="mt-4" @click="refresh" color="indigo">
        Retry
      </UButton>
    </div>

    <!-- No Data State -->
    <div v-else-if="!item" class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6">
      <h2 class="text-lg font-semibold text-yellow-800 dark:text-yellow-400 mb-2">No Data Available</h2>
      <p class="text-yellow-600 dark:text-yellow-400">This case does not have any data.</p>
    </div>

    <!-- Main Content -->
    <div v-else class="space-y-6">
      <!-- Main Content Card -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h2 class="text-xl font-semibold">Case Details</h2>
            <div class="flex items-center gap-2">
              <UBadge color="indigo" variant="subtle">
                {{ item.task_type || 'General' }}
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

          <!-- Customer Situation -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Customer Situation</label>
            <div class="px-4 py-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <p class="text-gray-900 dark:text-gray-100 whitespace-pre-wrap">{{ item.customer_situation }}</p>
            </div>
          </div>

          <!-- Task Type -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Task Type</label>
            <UBadge color="indigo" variant="subtle" size="lg">
              {{ item.task_type || 'General' }}
            </UBadge>
          </div>

          <!-- Guidance Provided -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Guidance Provided</label>
            <div class="px-4 py-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
              <p class="text-gray-900 dark:text-gray-100 whitespace-pre-wrap">{{ item.guidance_provided }}</p>
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

          <!-- Created Date -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Created</label>
            <div class="flex items-center gap-2 text-gray-900 dark:text-gray-100">
              <UIcon name="i-heroicons-calendar" class="w-5 h-5 text-gray-400" />
              {{ formatDate(item.timestamp) }}
            </div>
          </div>
        </div>
      </UCard>

      <!-- Outcome Section -->
      <UCard v-if="item.outcome && Object.keys(item.outcome).length > 0">
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-chart-bar" class="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
            <h2 class="text-xl font-semibold">Outcome</h2>
          </div>
        </template>

        <div class="space-y-4">
          <!-- Check if outcome has structured data -->
          <div v-if="typeof item.outcome === 'object'" class="space-y-3">
            <div
              v-for="(value, key) in item.outcome"
              :key="key"
              class="border-l-4 border-indigo-400 pl-4 py-2"
            >
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 capitalize">
                {{ String(key).replace(/_/g, ' ') }}
              </label>
              <div v-if="typeof value === 'object'" class="bg-gray-50 dark:bg-gray-800 rounded p-3">
                <pre class="text-sm text-gray-900 dark:text-gray-100 overflow-x-auto">{{ JSON.stringify(value, null, 2) }}</pre>
              </div>
              <p v-else class="text-gray-900 dark:text-gray-100">{{ value }}</p>
            </div>
          </div>

          <!-- Fallback for non-structured outcome -->
          <div v-else class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
            <pre class="text-sm text-gray-900 dark:text-gray-100 overflow-x-auto">{{ JSON.stringify(item.outcome, null, 2) }}</pre>
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
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Situation Length</label>
            <p class="text-gray-900 dark:text-gray-100">{{ item.customer_situation.length }} characters</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Guidance Length</label>
            <p class="text-gray-900 dark:text-gray-100">{{ item.guidance_provided.length }} characters</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Total Tokens (Est.)</label>
            <p class="text-gray-900 dark:text-gray-100">
              ~{{ Math.ceil((item.customer_situation.length + item.guidance_provided.length) / 4) }} tokens
            </p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Has Outcome</label>
            <UBadge
              :color="item.outcome && Object.keys(item.outcome).length > 0 ? 'green' : 'gray'"
              variant="subtle"
            >
              {{ item.outcome && Object.keys(item.outcome).length > 0 ? 'Yes' : 'No' }}
            </UBadge>
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

// Fetch case data
const { data: apiData, pending, error, refresh } = await useFetch(`/api/admin/cases/${id.value}`, {
  headers: {
    'Authorization': 'Bearer admin-token'
  }
})

const item = computed(() => apiData.value)

// Methods
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

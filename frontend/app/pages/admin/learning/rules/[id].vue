<template>
  <div>
    <!-- Breadcrumb and Back Button -->
    <div class="mb-6">
      <UButton
        to="/admin/learning/rules"
        variant="ghost"
        icon="i-heroicons-arrow-left"
      >
        Back to Rules
      </UButton>
      <div class="flex items-center gap-2 mt-4">
        <UButton to="/admin" variant="ghost" size="xs">Admin</UButton>
        <span class="text-gray-400">/</span>
        <UButton to="/admin/learning/rules" variant="ghost" size="xs">Rules</UButton>
        <span class="text-gray-400">/</span>
        <span class="text-sm text-gray-600">{{ id.substring(0, 8) }}...</span>
      </div>
      <h1 class="text-3xl font-bold mt-4">Rule Detail</h1>
    </div>

    <!-- Loading State -->
    <div v-if="pending" class="flex items-center justify-center py-12">
      <div class="text-center">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
        <p class="mt-4 text-gray-600">Loading rule...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6">
      <h2 class="text-lg font-semibold text-red-800 mb-2">Error Loading Rule</h2>
      <p class="text-red-600">
        {{ error.statusCode === 404 ? 'Rule not found.' : (error.message || 'Failed to load rule. Please try again.') }}
      </p>
      <UButton class="mt-4" @click="refresh">
        Retry
      </UButton>
    </div>

    <!-- No Data State -->
    <div v-else-if="!item" class="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
      <h2 class="text-lg font-semibold text-yellow-800 mb-2">No Data Available</h2>
      <p class="text-yellow-600">This rule does not have any data.</p>
    </div>

    <!-- Main Content -->
    <div v-else class="space-y-6">
      <!-- Main Content Card -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h2 class="text-xl font-semibold">Rule Details</h2>
            <div class="flex items-center gap-2">
              <UBadge color="teal" variant="subtle">
                {{ item.domain || 'General' }}
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
            <label class="block text-sm font-medium text-gray-700 mb-2">ID</label>
            <div class="flex items-center gap-2">
              <code class="flex-1 px-3 py-2 bg-gray-50 rounded font-mono text-sm">
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

          <!-- Principle -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Principle</label>
            <div class="px-4 py-3 bg-teal-50 rounded-lg border border-teal-200">
              <p class="text-gray-900 whitespace-pre-wrap">{{ item.principle }}</p>
            </div>
          </div>

          <!-- Domain -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Domain</label>
            <UBadge color="teal" variant="subtle" size="lg">
              {{ item.domain || 'General' }}
            </UBadge>
          </div>

          <!-- Confidence Score -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Confidence Score: {{ item.confidence.toFixed(3) }}
            </label>
            <div class="space-y-2">
              <div class="w-full bg-gray-200 rounded-full h-6">
                <div
                  class="h-6 rounded-full transition-all flex items-center justify-end pr-2"
                  :class="getConfidenceBarColor(item.confidence)"
                  :style="{ width: `${item.confidence * 100}%` }"
                >
                  <span class="text-xs font-semibold text-white">
                    {{ (item.confidence * 100).toFixed(1) }}%
                  </span>
                </div>
              </div>
              <div class="flex justify-between text-xs text-gray-600">
                <span>Low (0.0)</span>
                <span>Medium (0.5)</span>
                <span>High (1.0)</span>
              </div>
              <UBadge
                :color="getConfidenceColor(item.confidence)"
                variant="subtle"
              >
                {{ getConfidenceLabel(item.confidence) }}
              </UBadge>
            </div>
          </div>

          <!-- Evidence Count -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Supporting Evidence</label>
            <div class="flex items-center gap-3">
              <UBadge color="blue" variant="subtle" size="lg">
                {{ getEvidenceCount(item.supporting_evidence) }} pieces of evidence
              </UBadge>
            </div>
          </div>

          <!-- Vector Embedding Status -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Vector Embedding</label>
            <div class="flex items-center gap-3">
              <UIcon
                :name="item.has_embedding ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'"
                :class="item.has_embedding ? 'text-green-600' : 'text-gray-400'"
                class="w-6 h-6"
              />
              <span :class="item.has_embedding ? 'text-green-700' : 'text-gray-600'">
                {{ item.has_embedding ? 'Vector embedding present (1536 dimensions)' : 'No vector embedding available' }}
              </span>
            </div>
          </div>
        </div>
      </UCard>

      <!-- Supporting Evidence Section -->
      <UCard v-if="item.supporting_evidence && getEvidenceCount(item.supporting_evidence) > 0">
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-document-text" class="w-5 h-5 text-blue-600" />
            <h2 class="text-xl font-semibold">Supporting Evidence</h2>
          </div>
        </template>

        <div class="space-y-4">
          <!-- Array of evidence -->
          <div v-if="Array.isArray(item.supporting_evidence)" class="space-y-3">
            <div
              v-for="(evidence, index) in item.supporting_evidence"
              :key="index"
              class="border-l-4 border-blue-400 pl-4 py-3 bg-blue-50 rounded-r"
            >
              <div class="flex items-start justify-between mb-2">
                <span class="text-xs font-semibold text-blue-700 uppercase">Evidence {{ index + 1 }}</span>
              </div>
              <div v-if="typeof evidence === 'string'" class="text-gray-900">
                {{ evidence }}
              </div>
              <div v-else-if="typeof evidence === 'object'" class="space-y-2">
                <div
                  v-for="(value, key) in evidence"
                  :key="key"
                >
                  <label class="text-xs font-medium text-gray-600 uppercase">{{ String(key) }}</label>
                  <p class="text-gray-900">{{ value }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Object evidence -->
          <div v-else-if="typeof item.supporting_evidence === 'object'" class="space-y-3">
            <div
              v-for="(value, key) in item.supporting_evidence"
              :key="key"
              class="border-l-4 border-blue-400 pl-4 py-3 bg-blue-50 rounded-r"
            >
              <label class="block text-xs font-semibold text-blue-700 uppercase mb-2">{{ String(key) }}</label>
              <div v-if="typeof value === 'object'" class="bg-white rounded p-3">
                <pre class="text-sm text-gray-900 overflow-x-auto">{{ JSON.stringify(value, null, 2) }}</pre>
              </div>
              <p v-else class="text-gray-900">{{ value }}</p>
            </div>
          </div>

          <!-- Fallback -->
          <div v-else class="bg-gray-50 rounded-lg p-4">
            <pre class="text-sm text-gray-900 overflow-x-auto">{{ JSON.stringify(item.supporting_evidence, null, 2) }}</pre>
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
            <label class="block text-sm font-medium text-gray-700 mb-2">Created</label>
            <div class="flex items-center gap-2 text-gray-900">
              <UIcon name="i-heroicons-calendar" class="w-5 h-5 text-gray-400" />
              {{ formatDate(item.created_at) }}
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Last Updated</label>
            <div class="flex items-center gap-2 text-gray-900">
              <UIcon name="i-heroicons-clock" class="w-5 h-5 text-gray-400" />
              {{ formatDate(item.updated_at) }}
            </div>
          </div>
        </div>
      </UCard>

      <!-- Metadata Section -->
      <UCard v-if="item.meta && Object.keys(item.meta).length > 0">
        <template #header>
          <h2 class="text-xl font-semibold">Metadata</h2>
        </template>

        <div class="bg-gray-50 rounded-lg p-4">
          <pre class="text-sm text-gray-900 overflow-x-auto">{{ JSON.stringify(item.meta, null, 2) }}</pre>
        </div>
      </UCard>

      <!-- Additional Information -->
      <UCard>
        <template #header>
          <h2 class="text-xl font-semibold">Technical Information</h2>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Principle Length</label>
            <p class="text-gray-900">{{ item.principle.length }} characters</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Estimated Tokens</label>
            <p class="text-gray-900">~{{ Math.ceil(item.principle.length / 4) }} tokens</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Word Count</label>
            <p class="text-gray-900">{{ item.principle.split(/\s+/).length }} words</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Evidence Count</label>
            <p class="text-gray-900">{{ getEvidenceCount(item.supporting_evidence) }} pieces</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Confidence Level</label>
            <UBadge
              :color="getConfidenceColor(item.confidence)"
              variant="subtle"
            >
              {{ getConfidenceLabel(item.confidence) }}
            </UBadge>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
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

// Fetch rule data
const { data: apiData, pending, error, refresh } = await useFetch(`/api/admin/rules/${id.value}`, {
  headers: {
    'Authorization': 'Bearer admin-token'
  }
})

const item = computed(() => apiData.value)

// Methods
const getConfidenceColor = (confidence: number) => {
  if (confidence > 0.8) return 'green'
  if (confidence >= 0.5) return 'yellow'
  return 'red'
}

const getConfidenceBarColor = (confidence: number) => {
  if (confidence > 0.8) return 'bg-green-500'
  if (confidence >= 0.5) return 'bg-yellow-500'
  return 'bg-red-500'
}

const getConfidenceLabel = (confidence: number) => {
  if (confidence > 0.8) return 'High Confidence'
  if (confidence >= 0.5) return 'Medium Confidence'
  return 'Low Confidence'
}

const getEvidenceCount = (evidence: any) => {
  if (!evidence) return 0
  if (Array.isArray(evidence)) return evidence.length
  if (typeof evidence === 'object') return Object.keys(evidence).length
  return 0
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

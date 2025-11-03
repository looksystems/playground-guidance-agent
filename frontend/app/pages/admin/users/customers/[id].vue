<template>
  <div>
    <!-- Breadcrumb and Back Button -->
    <div class="mb-6">
      <UButton
        to="/admin/users/customers"
        variant="ghost"
        icon="i-heroicons-arrow-left"
      >
        Back to Customers
      </UButton>
      <div class="flex items-center gap-2 mt-4">
        <UButton to="/admin" variant="ghost" size="xs">Admin</UButton>
        <span class="text-gray-400">/</span>
        <UButton to="/admin/users/customers" variant="ghost" size="xs">Customers</UButton>
        <span class="text-gray-400">/</span>
        <span class="text-sm text-gray-600">{{ truncateId(id) }}</span>
      </div>
      <h1 class="text-3xl font-bold mt-4">Customer Profile</h1>
    </div>

    <!-- Loading State -->
    <div v-if="pending" class="flex items-center justify-center py-12">
      <div class="text-center">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        <p class="mt-4 text-gray-600">Loading customer data...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6">
      <h2 class="text-lg font-semibold text-red-800 mb-2">Error Loading Customer</h2>
      <p class="text-red-600">
        {{ error.statusCode === 404 ? 'Customer not found.' : (error.message || 'Failed to load customer data. Please try again.') }}
      </p>
      <UButton class="mt-4" @click="refresh">
        Retry
      </UButton>
    </div>

    <!-- No Data State -->
    <div v-else-if="!customer" class="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
      <h2 class="text-lg font-semibold text-yellow-800 mb-2">No Data Available</h2>
      <p class="text-yellow-600">This customer does not have any data.</p>
    </div>

    <!-- Main Content -->
    <div v-else class="space-y-6">
      <!-- Customer Overview Card -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h2 class="text-xl font-semibold">Customer Overview</h2>
            <UBadge color="blue" variant="subtle">
              {{ customer.total_consultations }} consultation{{ customer.total_consultations !== 1 ? 's' : '' }}
            </UBadge>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Customer ID with Copy -->
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-2">Customer ID</label>
            <div class="flex items-center gap-2">
              <code class="flex-1 px-3 py-2 bg-gray-50 rounded font-mono text-sm">
                {{ customer.customer_id }}
              </code>
              <UButton
                icon="i-heroicons-clipboard"
                size="sm"
                variant="outline"
                @click="copyToClipboard(customer.customer_id)"
              >
                Copy
              </UButton>
            </div>
          </div>

          <!-- Total Consultations -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Total Consultations</label>
            <div class="flex items-center gap-2">
              <UIcon name="i-heroicons-chat-bubble-left-right" class="w-5 h-5 text-blue-500" />
              <span class="text-2xl font-bold text-gray-900">{{ customer.total_consultations }}</span>
            </div>
          </div>

          <!-- Average Compliance Score -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Average Compliance Score</label>
            <div class="space-y-2">
              <div class="flex items-center gap-3">
                <div class="flex-1 h-4 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all"
                    :class="getComplianceColorClass(customer.avg_compliance_score)"
                    :style="{ width: `${customer.avg_compliance_score * 100}%` }"
                  ></div>
                </div>
                <span class="text-lg font-semibold" :class="getComplianceTextColor(customer.avg_compliance_score)">
                  {{ (customer.avg_compliance_score * 100).toFixed(1) }}%
                </span>
              </div>
              <UBadge
                :color="getComplianceColor(customer.avg_compliance_score)"
                variant="subtle"
              >
                {{ getComplianceLabel(customer.avg_compliance_score) }}
              </UBadge>
            </div>
          </div>

          <!-- First Consultation -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">First Consultation</label>
            <div class="flex items-center gap-2 text-gray-900">
              <UIcon name="i-heroicons-calendar" class="w-5 h-5 text-gray-400" />
              {{ formatDate(customer.first_consultation) }}
            </div>
          </div>

          <!-- Last Consultation -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Last Consultation</label>
            <div class="flex items-center gap-2 text-gray-900">
              <UIcon name="i-heroicons-calendar" class="w-5 h-5 text-gray-400" />
              {{ formatDate(customer.last_consultation) }}
            </div>
          </div>

          <!-- Average Satisfaction -->
          <div v-if="customer.avg_satisfaction !== null && customer.avg_satisfaction !== undefined" class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-2">Average Satisfaction</label>
            <div class="space-y-2">
              <div class="flex items-center gap-3">
                <div class="flex-1 h-4 bg-gray-200 rounded-full overflow-hidden max-w-md">
                  <div
                    class="h-full bg-amber-500 rounded-full transition-all"
                    :style="{ width: `${(customer.avg_satisfaction / 5) * 100}%` }"
                  ></div>
                </div>
                <span class="text-lg font-semibold text-gray-900">
                  {{ customer.avg_satisfaction.toFixed(1) }}/5
                </span>
              </div>
            </div>
          </div>
        </div>
      </UCard>

      <!-- Customer Profile Section -->
      <UCard v-if="customer.customer_profile && Object.keys(customer.customer_profile).length > 0">
        <template #header>
          <h2 class="text-xl font-semibold">Customer Profile</h2>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div v-for="(value, key) in customer.customer_profile" :key="key">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              {{ formatProfileKey(key) }}
            </label>
            <div class="text-gray-900">
              <template v-if="typeof value === 'object' && value !== null">
                <pre class="text-sm bg-gray-50 p-3 rounded overflow-x-auto">{{ JSON.stringify(value, null, 2) }}</pre>
              </template>
              <template v-else>
                {{ value || '-' }}
              </template>
            </div>
          </div>
        </div>
      </UCard>

      <!-- Topics Distribution -->
      <UCard v-if="customer.topics && customer.topics.length > 0">
        <template #header>
          <h2 class="text-xl font-semibold">Consultation Topics</h2>
        </template>

        <div class="flex flex-wrap gap-2">
          <UBadge
            v-for="(topic, index) in customer.topics"
            :key="index"
            color="purple"
            variant="subtle"
            size="lg"
          >
            {{ topic }}
          </UBadge>
        </div>
      </UCard>

      <!-- Consultation History -->
      <UCard v-if="customer.recent_consultations && customer.recent_consultations.length > 0">
        <template #header>
          <div class="flex items-center justify-between">
            <h2 class="text-xl font-semibold">Recent Consultations</h2>
            <span class="text-sm text-gray-600">Last 5 consultations</span>
          </div>
        </template>

        <div class="space-y-4">
          <div
            v-for="consultation in customer.recent_consultations"
            :key="consultation.consultation_id"
            class="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1 space-y-2">
                <!-- Consultation Header -->
                <div class="flex items-center gap-3">
                  <code class="text-sm font-mono text-gray-600">
                    {{ truncateId(consultation.consultation_id) }}
                  </code>
                  <UBadge
                    :color="getStatusColor(consultation.status)"
                    variant="subtle"
                    size="xs"
                  >
                    {{ consultation.status }}
                  </UBadge>
                </div>

                <!-- Topic -->
                <div v-if="consultation.topic" class="flex items-center gap-2">
                  <UIcon name="i-heroicons-tag" class="w-4 h-4 text-gray-400" />
                  <span class="text-sm text-gray-700">{{ consultation.topic }}</span>
                </div>

                <!-- Date -->
                <div class="flex items-center gap-2">
                  <UIcon name="i-heroicons-calendar" class="w-4 h-4 text-gray-400" />
                  <span class="text-sm text-gray-600">{{ formatDateTime(consultation.created_at) }}</span>
                </div>

                <!-- Compliance Score -->
                <div v-if="consultation.compliance_score !== null && consultation.compliance_score !== undefined">
                  <div class="flex items-center gap-2">
                    <span class="text-sm font-medium text-gray-700">Compliance:</span>
                    <div class="flex-1 max-w-[150px] h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        class="h-full rounded-full"
                        :class="getComplianceColorClass(consultation.compliance_score)"
                        :style="{ width: `${consultation.compliance_score * 100}%` }"
                      ></div>
                    </div>
                    <UBadge
                      :color="getComplianceColor(consultation.compliance_score)"
                      variant="subtle"
                      size="xs"
                    >
                      {{ (consultation.compliance_score * 100).toFixed(0) }}%
                    </UBadge>
                  </div>
                </div>
              </div>

              <!-- View Button -->
              <div>
                <UButton
                  size="xs"
                  @click="navigateTo(`/admin/consultations/${consultation.consultation_id}`)"
                >
                  View Details
                </UButton>
              </div>
            </div>
          </div>
        </div>
      </UCard>

      <!-- Empty Consultations State -->
      <UCard v-else-if="customer.total_consultations === 0">
        <div class="text-center py-12">
          <UIcon name="i-heroicons-chat-bubble-left-right" class="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 class="text-lg font-semibold text-gray-900 mb-2">No Consultations Yet</h3>
          <p class="text-gray-600">This customer hasn't started any consultations.</p>
        </div>
      </UCard>

      <!-- Compliance Trend Chart (Placeholder) -->
      <UCard v-if="customer.recent_consultations && customer.recent_consultations.length > 1">
        <template #header>
          <h2 class="text-xl font-semibold">Compliance Trend</h2>
        </template>

        <div class="space-y-4">
          <!-- Simple visual representation -->
          <div class="flex items-end gap-2 h-48">
            <div
              v-for="(consultation, index) in customer.recent_consultations.slice().reverse()"
              :key="index"
              class="flex-1 flex flex-col items-center gap-2"
            >
              <div
                class="w-full rounded-t transition-all"
                :class="getComplianceColorClass(consultation.compliance_score || 0)"
                :style="{ height: `${(consultation.compliance_score || 0) * 100}%` }"
              ></div>
              <span class="text-xs text-gray-600">{{ formatShortDate(consultation.created_at) }}</span>
            </div>
          </div>
          <div class="text-sm text-gray-600 text-center">
            Compliance scores over time (most recent consultations)
          </div>
        </div>
      </UCard>

      <!-- Customer Statistics -->
      <UCard>
        <template #header>
          <h2 class="text-xl font-semibold">Customer Statistics</h2>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Customer Since</label>
            <div class="text-2xl font-bold text-gray-900">
              {{ getDaysSince(customer.first_consultation) }} days
            </div>
            <p class="text-sm text-gray-600 mt-1">{{ formatDate(customer.first_consultation) }}</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Days Since Last Visit</label>
            <div class="text-2xl font-bold text-gray-900">
              {{ getDaysSince(customer.last_consultation) }} days
            </div>
            <p class="text-sm text-gray-600 mt-1">{{ formatDate(customer.last_consultation) }}</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Topic Diversity</label>
            <div class="text-2xl font-bold text-gray-900">
              {{ customer.topics?.length || 0 }}
            </div>
            <p class="text-sm text-gray-600 mt-1">Different topics discussed</p>
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

// Fetch customer data
const { data: apiData, pending, error, refresh } = await useFetch(`/api/admin/customers/${id.value}`, {
  headers: {
    'Authorization': 'Bearer admin-token'
  }
})

const customer = computed(() => apiData.value)

// Methods
const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('en-GB', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatDateTime = (dateString: string) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('en-GB', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatShortDate = (dateString: string) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('en-GB', {
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

// Format profile keys (convert snake_case to Title Case)
const formatProfileKey = (key: string) => {
  return key
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
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

const getComplianceTextColor = (score: number) => {
  if (score >= 0.8) return 'text-green-700'
  if (score >= 0.5) return 'text-yellow-700'
  return 'text-red-700'
}

const getComplianceLabel = (score: number) => {
  if (score >= 0.8) return 'High Compliance'
  if (score >= 0.5) return 'Moderate Compliance'
  return 'Low Compliance'
}

// Status colors
const getStatusColor = (status: string) => {
  const statusMap: Record<string, string> = {
    'completed': 'green',
    'active': 'blue',
    'in_progress': 'yellow',
    'pending': 'gray',
    'failed': 'red'
  }
  return statusMap[status?.toLowerCase()] || 'gray'
}

// Calculate days since a date
const getDaysSince = (dateString: string) => {
  if (!dateString) return 0
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now.getTime() - date.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays
}
</script>

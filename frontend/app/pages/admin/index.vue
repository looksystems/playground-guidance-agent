<template>
  <ClientOnly>
    <div class="space-y-8">
    <!-- Error Alert -->
    <UAlert
      v-if="error"
      color="red"
      variant="solid"
      title="Failed to load admin data"
      :description="error.message || 'An error occurred while loading the dashboard data.'"
      icon="i-heroicons-exclamation-triangle"
    />

    <!-- Key Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <UCard data-testid="metric-card">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Consultations</p>
            <p class="mt-2 text-4xl font-bold">{{ metricsData?.consultations?.total?.toLocaleString() || '0' }}</p>
            <div class="mt-2 flex items-center gap-1">
              <UIcon name="i-heroicons-arrow-trending-up-solid" class="w-4 h-4 text-green-600" />
              <span class="text-sm font-medium text-green-600">Last {{ metricsData?.summary?.period_days || 30 }} days</span>
            </div>
          </div>
          <div class="p-3 bg-primary-50 rounded-lg">
            <UIcon name="i-heroicons-chart-bar-solid" class="w-6 h-6 text-primary-600" />
          </div>
        </div>
      </UCard>

      <UCard data-testid="metric-card">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">FCA Compliance</p>
            <p class="mt-2 text-4xl font-bold">{{ metricsData?.consultations?.compliance_rate?.toFixed(1) || '0' }}%</p>
            <div class="mt-2 flex items-center gap-1">
              <UIcon name="i-heroicons-shield-check-solid" class="w-4 h-4 text-green-600" />
              <span class="text-sm font-medium text-green-600">Compliant rate</span>
            </div>
          </div>
          <div class="p-3 bg-green-50 rounded-lg">
            <UIcon name="i-heroicons-shield-check-solid" class="w-6 h-6 text-green-600" />
          </div>
        </div>
      </UCard>

      <UCard data-testid="metric-card">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Satisfaction</p>
            <p class="mt-2 text-4xl font-bold">{{ metricsData?.consultations?.avg_satisfaction?.toFixed(1) || '0' }}/10</p>
            <p class="mt-2 text-sm text-gray-600">Average rating</p>
          </div>
          <div class="p-3 bg-yellow-50 rounded-lg">
            <UIcon name="i-heroicons-star-solid" class="w-6 h-6 text-yellow-600" />
          </div>
        </div>
      </UCard>
    </div>

    <!-- Chart -->
    <UCard>
      <template #header>
        <h2 class="text-xl font-semibold">Compliance Over Time</h2>
      </template>
      <ClientOnly>
        <AdminLineChart :data="complianceData" :height="300" />
      </ClientOnly>
    </UCard>

    <!-- Recent Consultations Table -->
    <UCard>
      <template #header>
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-semibold">Recent Consultations</h2>
          <div class="flex gap-2">
            <UButton icon="i-heroicons-funnel" variant="outline">Filters</UButton>
            <UButton icon="i-heroicons-arrow-down-tray" variant="outline">Export</UButton>
          </div>
        </div>
      </template>

      <div v-if="!apiData || tableRows.length === 0" class="flex items-center justify-center py-12">
        <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin text-gray-400" />
        <span class="ml-2 text-gray-500">Loading consultations...</span>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customer</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Topic</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Messages</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Compliance</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Satisfaction</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="row in tableRows" :key="row.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ row.id.substring(0, 8) }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ row.customer }}</td>
              <td class="px-6 py-4 text-sm text-gray-900">{{ row.topic }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ row.date }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ row.messages }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <UBadge :color="getComplianceColor(row.compliance)" variant="subtle">
                  {{ row.compliance }}%
                </UBadge>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <div class="flex items-center gap-2">
                  <span>{{ row.satisfactionEmoji }}</span>
                  <span>{{ row.satisfactionText }}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <UButton size="xs" @click="navigateTo(`/admin/consultations/${row.id}`)">
                  View
                </UButton>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </UCard>
  </div>
  <template #fallback>
    <div class="flex items-center justify-center min-h-screen">
      <div class="text-center">
        <UIcon name="i-heroicons-arrow-path" class="w-12 h-12 animate-spin text-gray-400 mx-auto mb-4" />
        <p class="text-gray-500">Loading dashboard...</p>
      </div>
    </div>
  </template>
  </ClientOnly>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  ssr: false // Disable SSR to avoid hydration mismatches with client-only data
})

const columns = [
  { key: 'id', label: 'ID', sortable: true, id: 'id' },
  { key: 'customer', label: 'Customer', sortable: true, id: 'customer' },
  { key: 'topic', label: 'Topic', id: 'topic' },
  { key: 'date', label: 'Date', sortable: true, id: 'date' },
  { key: 'messages', label: 'Messages', id: 'messages' },
  { key: 'compliance', label: 'Compliance', id: 'compliance' },
  { key: 'satisfaction', label: 'Satisfaction', id: 'satisfaction' },
  { key: 'actions', label: 'Actions', id: 'actions' }
]

interface ConsultationRow {
  id: string
  customer: string
  topic: string
  date: string
  messages: number
  compliance: number
  satisfactionEmoji: string
  satisfactionText: string
}

// Reactive state for consultations
const apiData = ref<any>(null)
const pending = ref(true)
const error = ref<any>(null)

// Reactive state for metrics
const metricsData = ref<any>(null)

// Fetch metrics data on client-side mount
onMounted(async () => {
  try {
    const metricsResponse = await $fetch('/api/admin/metrics', {
      headers: {
        'Authorization': 'Bearer admin-token'
      }
    })
    metricsData.value = metricsResponse
  } catch (e) {
    console.error('Failed to fetch metrics:', e)
  }
})

// Fetch consultations data on client-side mount
onMounted(async () => {
  try {
    pending.value = true
    const response = await $fetch('/api/admin/consultations', {
      headers: {
        'Authorization': 'Bearer admin-token'
      }
    })
    apiData.value = response
  } catch (e: any) {
    console.error('Failed to fetch consultations:', e)
    error.value = e
  } finally {
    pending.value = false
  }
})

// Create a separate ref for table rows to ensure reactivity
const tableRows = ref<ConsultationRow[]>([])

// Transform API data to match table structure
const consultations = computed(() => {
  if (!apiData.value || !apiData.value.items) {
    return []
  }

  const transformed = apiData.value.items.map((item: any) => {
    // Extract first customer message as topic
    const customerMessages = item.conversation.filter((msg: any) => msg.role === 'customer')
    const topic = customerMessages.length > 0
      ? customerMessages[0].content.substring(0, 50) + (customerMessages[0].content.length > 50 ? '...' : '')
      : 'General Consultation'

    // Calculate compliance score (convert from 0-1 to percentage)
    const complianceScore = Math.round(item.metrics.avg_compliance_score * 100)

    // Format satisfaction
    const satisfaction = item.metrics.customer_satisfaction || 0
    let satisfactionEmoji = '😊'
    let satisfactionText = 'Satisfied'

    if (satisfaction >= 8) {
      satisfactionEmoji = '😊'
      satisfactionText = 'Satisfied'
    } else if (satisfaction >= 6) {
      satisfactionEmoji = '😐'
      satisfactionText = 'Neutral'
    } else if (satisfaction > 0) {
      satisfactionEmoji = '😟'
      satisfactionText = 'Unsatisfied'
    } else {
      satisfactionEmoji = '⏳'
      satisfactionText = 'In Progress'
    }

    return {
      id: item.id,
      customer: item.customer_name,
      topic,
      date: new Date(item.created_at).toLocaleDateString('en-GB'),
      messages: item.metrics.message_count,
      compliance: complianceScore,
      satisfactionEmoji,
      satisfactionText
    }
  })

  return transformed
})

// Watch for changes and update tableRows to ensure reactivity
watch(consultations, (newValue) => {
  tableRows.value = [...newValue]
}, { immediate: true })

// Reactive state for time-series data
const timeSeriesData = ref<any>(null)

// Fetch time-series data on client-side mount
onMounted(async () => {
  try {
    const response = await $fetch('/api/admin/metrics/time-series?days=180', {
      headers: {
        'Authorization': 'Bearer admin-token'
      }
    })
    timeSeriesData.value = response
  } catch (e) {
    console.error('Failed to fetch time-series data:', e)
  }
})

// Transform time-series data to chart format
const complianceData = computed(() => {
  if (!timeSeriesData.value || !timeSeriesData.value.data_points) {
    return {
      labels: [],
      datasets: []
    }
  }

  const points = timeSeriesData.value.data_points
  const labels = points.map((p: any) => {
    const date = new Date(p.date)
    return date.toLocaleDateString('en-GB', { month: 'short', day: 'numeric' })
  })

  const data = points.map((p: any) => Math.round(p.avg_compliance * 100))

  return {
    labels,
    datasets: [
      {
        label: 'FCA Compliance Score',
        data,
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.4
      }
    ]
  }
})

const getComplianceColor = (score: number): 'success' | 'warning' | 'error' => {
  if (score >= 95) return 'success'
  if (score >= 85) return 'warning'
  return 'error'
}
</script>

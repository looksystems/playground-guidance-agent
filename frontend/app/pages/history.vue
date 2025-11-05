<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
    <div class="max-w-7xl mx-auto px-4">
      <div class="mb-8">
        <NuxtLink to="/" class="flex items-center gap-2 text-primary-700 dark:text-primary-400 hover:text-primary-900 dark:hover:text-primary-300 mb-4">
          <UIcon name="i-heroicons-arrow-left" />
          <span>Back to Home</span>
        </NuxtLink>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">My Consultations</h1>
      </div>

      <!-- Filter Tabs -->
      <UTabs :items="tabs" v-model="activeTab" class="mb-6" />

      <!-- Search -->
      <UInput
        v-model="search"
        icon="i-heroicons-magnifying-glass"
        placeholder="Search consultations"
        size="lg"
        class="mb-6"
      />

      <!-- Consultations List -->
      <div v-if="filteredConsultations.length > 0" class="space-y-4">
        <UCard
          v-for="consultation in filteredConsultations"
          :key="consultation.id"
          class="hover:shadow-lg dark:hover:shadow-gray-950/50 transition-shadow cursor-pointer"
          @click="navigateTo(`/consultation/${consultation.id}`)"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <h3 class="text-xl font-semibold mb-2 text-gray-900 dark:text-gray-100">{{ consultation.title }}</h3>
              <div class="text-sm text-gray-600 dark:text-gray-400 space-x-2 mb-2">
                <span>Advisor: {{ consultation.advisor }}</span>
                <span>•</span>
                <span>{{ consultation.date }}</span>
                <span>•</span>
                <UBadge :color="consultation.status === 'active' ? 'success' : 'neutral'">
                  {{ consultation.status }}
                </UBadge>
              </div>
              <p class="text-gray-700 dark:text-gray-300 mb-3">"{{ consultation.preview }}"</p>
              <div class="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                <span>{{ consultation.messages }} messages</span>
                <UBadge :color="consultation.compliance >= 95 ? 'success' : 'warning'">
                  {{ consultation.compliance }}% compliance
                </UBadge>
                <span>{{ consultation.satisfactionEmoji }} {{ consultation.satisfactionText }}</span>
              </div>
            </div>
            <UButton
              :label="consultation.status === 'active' ? 'Continue' : 'View'"
              :icon="consultation.status === 'active' ? 'i-heroicons-arrow-right' : 'i-heroicons-eye'"
              color="indigo"
              @click.stop="navigateTo(`/consultation/${consultation.id}`)"
            />
          </div>
        </UCard>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12">
        <UIcon name="i-heroicons-inbox" class="w-16 h-16 mx-auto text-gray-400 dark:text-gray-500 mb-4" />
        <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">No consultations found</h3>
        <p class="text-gray-600 dark:text-gray-400 mb-6">{{ search ? 'Try adjusting your search' : 'Start your first consultation' }}</p>
        <UButton to="/" size="lg" color="indigo">
          Start New Consultation
        </UButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const activeTab = ref(0)
const search = ref('')

const tabs = computed(() => {
  const all = consultations.value.length
  const active = consultations.value.filter(c => c.status === 'active').length
  const completed = consultations.value.filter(c => c.status === 'completed').length

  return [
    { label: `All (${all})` },
    { label: `Active (${active})` },
    { label: `Completed (${completed})` }
  ]
})

// Fetch consultations from API
const { data: apiData, pending, error } = await useFetch('/api/consultations')

// Fetch detailed data for each consultation to get metrics and preview
const consultationsWithDetails = ref<any[]>([])

// Load consultation details including metrics
const loadConsultationDetails = async () => {
  if (!apiData.value?.items) {
    consultationsWithDetails.value = []
    return
  }

  const detailsPromises = apiData.value.items.map(async (c: any) => {
    try {
      // Fetch both detail (for preview) and metrics in parallel
      const [detailResponse, metricsResponse] = await Promise.all([
        $fetch(`/api/consultations/${c.id}`),
        $fetch(`/api/consultations/${c.id}/metrics`)
      ])

      const detail: any = detailResponse
      const metrics: any = metricsResponse

      // Extract first customer message for preview
      const customerMessages = detail.conversation?.filter((msg: any) => msg.role === 'customer') || []
      const firstCustomerMessage = customerMessages.length > 0 ? customerMessages[0].content : ''
      const preview = firstCustomerMessage
        ? firstCustomerMessage.substring(0, 100) + (firstCustomerMessage.length > 100 ? '...' : '')
        : (c.status === 'active' ? 'Consultation in progress...' : 'No messages yet')

      // Determine satisfaction from outcome
      let satisfactionEmoji = ''
      let satisfactionText = ''

      if (c.status === 'completed' && detail.outcome) {
        const satisfaction = detail.outcome.customer_satisfaction
        if (satisfaction !== null && satisfaction !== undefined) {
          if (satisfaction >= 8) {
            satisfactionEmoji = '😊'
            satisfactionText = 'Satisfied'
          } else if (satisfaction >= 6) {
            satisfactionEmoji = '😐'
            satisfactionText = 'Neutral'
          } else {
            satisfactionEmoji = '😟'
            satisfactionText = 'Needs improvement'
          }
        } else {
          satisfactionEmoji = '❓'
          satisfactionText = 'No feedback'
        }
      } else {
        satisfactionEmoji = '⏳'
        satisfactionText = 'In progress'
      }

      return {
        id: c.id,
        title: 'Pension Consultation',
        advisor: c.advisor_name,
        date: new Date(c.created_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }),
        status: c.status,
        preview: preview,
        messages: metrics.message_count || 0,
        compliance: Math.round((metrics.avg_compliance_score || 0) * 100),
        satisfactionEmoji: satisfactionEmoji,
        satisfactionText: satisfactionText
      }
    } catch (err) {
      console.error(`Failed to load details for consultation ${c.id}:`, err)
      // Fallback to basic data if detail fetch fails
      return {
        id: c.id,
        title: 'Pension Consultation',
        advisor: c.advisor_name,
        date: new Date(c.created_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }),
        status: c.status,
        preview: 'Unable to load details',
        messages: 0,
        compliance: 0,
        satisfactionEmoji: '❌',
        satisfactionText: 'Error'
      }
    }
  })

  consultationsWithDetails.value = await Promise.all(detailsPromises)
}

// Load details when API data is available
watch(apiData, async (newData) => {
  if (newData) {
    await loadConsultationDetails()
  }
}, { immediate: true })

// Transform API data to match UI format
const consultations = computed(() => consultationsWithDetails.value)

const filteredConsultations = computed(() => {
  let filtered = consultations.value

  // Filter by tab
  if (activeTab.value === 1) {
    // Active only
    filtered = filtered.filter(c => c.status === 'active')
  } else if (activeTab.value === 2) {
    // Completed only
    filtered = filtered.filter(c => c.status === 'completed')
  }

  // Filter by search
  if (search.value) {
    const searchLower = search.value.toLowerCase()
    filtered = filtered.filter(c =>
      c.title.toLowerCase().includes(searchLower) ||
      c.advisor.toLowerCase().includes(searchLower) ||
      c.preview.toLowerCase().includes(searchLower)
    )
  }

  return filtered
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-7xl mx-auto px-4">
      <div class="mb-8">
        <NuxtLink to="/" class="flex items-center gap-2 text-primary-700 hover:text-primary-900 mb-4">
          <UIcon name="i-heroicons-arrow-left" />
          <span>Back to Home</span>
        </NuxtLink>
        <h1 class="text-3xl font-bold">My Consultations</h1>
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
          class="hover:shadow-lg transition-shadow cursor-pointer"
          @click="navigateTo(`/consultation/${consultation.id}`)"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <h3 class="text-xl font-semibold mb-2">{{ consultation.title }}</h3>
              <div class="text-sm text-gray-600 space-x-2 mb-2">
                <span>Advisor: {{ consultation.advisor }}</span>
                <span>•</span>
                <span>{{ consultation.date }}</span>
                <span>•</span>
                <UBadge :color="consultation.status === 'active' ? 'success' : 'neutral'">
                  {{ consultation.status }}
                </UBadge>
              </div>
              <p class="text-gray-700 mb-3">"{{ consultation.preview }}"</p>
              <div class="flex items-center gap-4 text-sm">
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
              @click.stop="navigateTo(`/consultation/${consultation.id}`)"
            />
          </div>
        </UCard>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12">
        <UIcon name="i-heroicons-inbox" class="w-16 h-16 mx-auto text-gray-400 mb-4" />
        <h3 class="text-xl font-semibold text-gray-900 mb-2">No consultations found</h3>
        <p class="text-gray-600 mb-6">{{ search ? 'Try adjusting your search' : 'Start your first consultation' }}</p>
        <UButton to="/" size="lg">
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

// Transform API data to match UI format
const consultations = computed(() => {
  if (!apiData.value?.items) return []

  return apiData.value.items.map((c: any) => ({
    id: c.id,
    title: 'Pension Consultation', // Could be enhanced with conversation summary
    advisor: c.advisor_name,
    date: new Date(c.created_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }),
    status: c.status,
    preview: 'Consultation in progress...', // Could extract first customer message
    messages: 0, // Would need to count conversation array
    compliance: 0, // Would need to calculate from conversation
    satisfactionEmoji: '😊',
    satisfactionText: 'In progress'
  }))
})

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

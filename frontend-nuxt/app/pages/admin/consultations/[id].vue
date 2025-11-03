<template>
  <div>
    <div class="mb-6">
      <UButton to="/admin" variant="ghost" icon="i-heroicons-arrow-left">
        Back to Dashboard
      </UButton>
      <h1 class="text-3xl font-bold mt-4">Consultation Review: {{ id }}</h1>
    </div>

    <!-- Loading State -->
    <div v-if="pending" class="flex items-center justify-center py-12">
      <div class="text-center">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
        <p class="mt-4 text-gray-600">Loading consultation data...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6">
      <h2 class="text-lg font-semibold text-red-800 mb-2">Error Loading Consultation</h2>
      <p class="text-red-600">{{ error.message || 'Failed to load consultation data. Please try again.' }}</p>
      <UButton class="mt-4" @click="refreshNuxtData()">
        Retry
      </UButton>
    </div>

    <!-- No Data State -->
    <div v-else-if="!consultation" class="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
      <h2 class="text-lg font-semibold text-yellow-800 mb-2">No Data Available</h2>
      <p class="text-yellow-600">This consultation does not have any data yet.</p>
    </div>

    <!-- Main Content -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-4 gap-6">
      <!-- Overview Sidebar -->
      <div class="lg:col-span-1">
        <UCard>
          <template #header>
            <h2 class="text-xl font-semibold">Overview</h2>
          </template>

          <div class="space-y-4">
            <div>
              <div class="text-sm font-medium text-gray-600">Customer</div>
              <div>{{ consultation?.customer }}</div>
            </div>

            <div>
              <div class="text-sm font-medium text-gray-600">Age</div>
              <div>{{ consultation?.age }}</div>
            </div>

            <div>
              <div class="text-sm font-medium text-gray-600 mb-2">Compliance</div>
              <UMeter
                :value="(consultation?.compliance || 0) * 100"
                :max="100"
                color="success"
              />
              <div class="text-sm mt-1">{{ ((consultation?.compliance || 0) * 100).toFixed(1) }}%</div>
            </div>

            <div class="pt-4 space-y-2">
              <UButton block icon="i-heroicons-document-arrow-down">
                Export PDF
              </UButton>
              <UButton block variant="outline" icon="i-heroicons-folder-plus">
                Add to Cases
              </UButton>
            </div>
          </div>
        </UCard>
      </div>

      <!-- Transcript -->
      <div class="lg:col-span-2">
        <UCard>
          <template #header>
            <h2 class="text-xl font-semibold">Conversation Transcript</h2>
          </template>

          <div class="space-y-4">
            <div
              v-for="(turn, index) in consultation?.transcript"
              :key="index"
              class="border-l-4 pl-4"
              :class="turn.isAdvisor ? 'border-orange-500' : 'border-blue-500'"
            >
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-semibold">
                  {{ turn.isAdvisor ? 'Advisor' : 'Customer' }} - Turn {{ turn.turn }}
                </span>
                <span class="text-xs text-gray-600">{{ turn.timestamp }}</span>
              </div>

              <p class="text-gray-900 mb-2">"{{ turn.content }}"</p>

              <div v-if="turn.complianceScore" class="flex items-center gap-2">
                <UBadge
                  :color="turn.complianceScore >= 0.95 ? 'success' : 'warning'"
                  variant="soft"
                >
                  {{ (turn.complianceScore * 100).toFixed(0) }}%
                </UBadge>
              </div>
            </div>
          </div>
        </UCard>
      </div>

      <!-- Learning Insights -->
      <div class="lg:col-span-1">
        <UCard>
          <template #header>
            <h2 class="text-xl font-semibold">Learning Insights</h2>
          </template>

          <div class="space-y-4">
            <div>
              <div class="text-sm font-medium text-gray-600 mb-2">Retrieved Cases</div>
              <div class="text-sm">{{ consultation?.insights?.cases }} relevant past consultations</div>
            </div>

            <div>
              <div class="text-sm font-medium text-gray-600 mb-2">Applied Rules</div>
              <ul class="space-y-1">
                <li
                  v-for="rule in consultation?.insights?.rules"
                  :key="rule"
                  class="text-sm"
                >
                  "{{ rule }}"
                </li>
              </ul>
            </div>
          </div>
        </UCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'admin'
})

const route = useRoute()
const id = computed(() => route.params.id as string)

// Fetch consultation data from backend admin API
const { data: apiData, pending, error } = await useFetch(`/api/admin/consultations/${id.value}`, {
  headers: {
    'Authorization': 'Bearer admin-token'
  }
})

// Transform API data to match the expected UI structure
const consultation = computed(() => {
  if (!apiData.value) return null

  // Transform conversation to transcript format expected by UI
  const transcript = apiData.value.conversation
    .filter((turn: any) => turn.role !== 'system') // Exclude system messages from transcript
    .map((turn: any, index: number) => ({
      turn: index + 1,
      isAdvisor: turn.role === 'advisor',
      content: turn.content,
      timestamp: new Date(turn.timestamp).toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      }),
      complianceScore: turn.compliance_score
    }))

  // Extract insights from metadata or use defaults
  const insights = {
    cases: apiData.value.outcome?.retrieved_cases || 0,
    rules: apiData.value.outcome?.applied_rules || [
      'FCA COBS 9.2: Assess client suitability',
      'FCA COBS 4.2: Communicate clearly',
      'FCA COBS 2.1: Act with integrity'
    ]
  }

  return {
    customer: apiData.value.customer_name,
    age: apiData.value.customer_age,
    compliance: apiData.value.metrics?.avg_compliance_score || 0,
    transcript,
    insights
  }
})
</script>

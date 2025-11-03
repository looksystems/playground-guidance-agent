<template>
  <div>
    <div class="mb-6">
      <UButton to="/admin" variant="ghost" icon="i-heroicons-arrow-left">
        Back to Dashboard
      </UButton>
      <h1 class="text-3xl font-bold mt-4">Consultation Review: {{ id }}</h1>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
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

// Mock data for development
const consultation = ref({
  customer: 'John Smith',
  age: 45,
  compliance: 0.98,
  transcript: [
    {
      turn: 1,
      isAdvisor: false,
      content: 'I am interested in retirement planning options.',
      timestamp: '10:00 AM',
      complianceScore: null
    },
    {
      turn: 2,
      isAdvisor: true,
      content: 'I would be happy to help you with retirement planning. Before we proceed, I need to understand your current financial situation and goals. Can you tell me about your current age and when you plan to retire?',
      timestamp: '10:01 AM',
      complianceScore: 0.98
    },
    {
      turn: 3,
      isAdvisor: false,
      content: 'I am 45 years old and I would like to retire at 65.',
      timestamp: '10:02 AM',
      complianceScore: null
    },
    {
      turn: 4,
      isAdvisor: true,
      content: 'Thank you for that information. To provide you with suitable advice, I need to assess your attitude to risk. This is a regulatory requirement under FCA guidelines. Can you tell me how comfortable you are with investment risk?',
      timestamp: '10:03 AM',
      complianceScore: 0.96
    }
  ],
  insights: {
    cases: 12,
    rules: [
      'FCA COBS 9.2: Assess client suitability',
      'FCA COBS 4.2: Communicate clearly',
      'Pension transfer requirements'
    ]
  }
})
</script>

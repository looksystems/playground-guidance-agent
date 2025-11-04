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
        <p class="mt-4 text-gray-600 dark:text-gray-400">Loading consultation data...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
      <h2 class="text-lg font-semibold text-red-800 dark:text-red-400 mb-2">Error Loading Consultation</h2>
      <p class="text-red-600 dark:text-red-400">{{ error.message || 'Failed to load consultation data. Please try again.' }}</p>
      <UButton class="mt-4" @click="refreshNuxtData()">
        Retry
      </UButton>
    </div>

    <!-- No Data State -->
    <div v-else-if="!consultation" class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6">
      <h2 class="text-lg font-semibold text-yellow-800 dark:text-yellow-400 mb-2">No Data Available</h2>
      <p class="text-yellow-600 dark:text-yellow-400">This consultation does not have any data yet.</p>
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
              <div class="text-sm font-medium text-gray-600 dark:text-gray-400">Customer</div>
              <div>{{ consultation?.customer }}</div>
            </div>

            <div>
              <div class="text-sm font-medium text-gray-600 dark:text-gray-400">Age</div>
              <div>{{ consultation?.age }}</div>
            </div>

            <div>
              <div class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Compliance</div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="h-2 rounded-full transition-all"
                  :class="(consultation?.compliance || 0) >= 0.8 ? 'bg-green-50 dark:bg-green-900/200' : (consultation?.compliance || 0) >= 0.6 ? 'bg-yellow-50 dark:bg-yellow-900/200' : 'bg-red-50 dark:bg-red-900/200'"
                  :style="{ width: `${((consultation?.compliance || 0) * 100)}%` }"
                ></div>
              </div>
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
                <span class="text-xs text-gray-600 dark:text-gray-400">{{ turn.timestamp }}</span>
              </div>

              <div class="prose prose-sm max-w-none text-gray-900 dark:text-gray-100 mb-2" v-html="renderMarkdown(turn.content)" />

              <div v-if="turn.complianceScore" class="flex items-center gap-2">
                <!-- Compliance Badge - Clickable if reasoning is available -->
                <UBadge
                  :data-testid="turn.compliance_reasoning ? 'compliance-badge' : undefined"
                  :color="getComplianceColor(turn.complianceScore)"
                  variant="soft"
                  :class="turn.compliance_reasoning ? 'cursor-pointer' : ''"
                  @click="turn.compliance_reasoning ? toggleReasoning(index) : null"
                >
                  {{ (turn.complianceScore * 100).toFixed(0) }}%
                  <UIcon
                    v-if="turn.compliance_reasoning"
                    :name="expandedReasoning[index] ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'"
                    class="ml-1"
                  />
                </UBadge>
              </div>

              <!-- Expandable Reasoning Section (NEW) -->
              <UCard
                v-if="turn.isAdvisor && turn.compliance_reasoning && expandedReasoning[index]"
                class="mt-3 bg-gray-50 dark:bg-gray-800"
              >
                <div class="space-y-3">
                  <!-- Pass/Fail Status -->
                  <div class="flex items-center gap-2">
                    <UBadge
                      v-if="turn.compliance_passed !== undefined"
                      :color="turn.compliance_passed ? 'green' : 'red'"
                      variant="solid"
                    >
                      {{ turn.compliance_passed ? 'PASSED' : 'FAILED' }}
                    </UBadge>
                    <UBadge
                      v-if="turn.requires_human_review"
                      color="orange"
                      variant="solid"
                    >
                      Requires Review
                    </UBadge>
                  </div>

                  <!-- Compliance Issues -->
                  <div v-if="turn.compliance_issues && turn.compliance_issues.length > 0">
                    <h4 class="font-semibold text-sm mb-2">Issues Found:</h4>
                    <ul class="space-y-2">
                      <li
                        v-for="(issue, issueIndex) in turn.compliance_issues"
                        :key="issueIndex"
                        class="flex items-start gap-2"
                      >
                        <UBadge
                          :color="getSeverityColor(issue.severity)"
                          size="xs"
                          variant="solid"
                        >
                          {{ issue.severity }}
                        </UBadge>
                        <span class="text-sm text-gray-700 dark:text-gray-300">{{ issue.description }}</span>
                      </li>
                    </ul>
                  </div>

                  <!-- Detailed Reasoning -->
                  <div>
                    <h4 class="font-semibold text-sm mb-2">Detailed Analysis:</h4>
                    <pre class="text-xs whitespace-pre-wrap bg-white dark:bg-gray-900 p-3 rounded border border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-100 overflow-x-auto">{{ turn.compliance_reasoning }}</pre>
                  </div>
                </div>
              </UCard>
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
              <div class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Retrieved Cases</div>
              <div class="text-sm">{{ consultation?.insights?.cases }} relevant past consultations</div>
            </div>

            <div>
              <div class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Applied Rules</div>
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
import { marked } from 'marked'

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

// Reactive state for expandable reasoning sections
const expandedReasoning = ref<Record<number, boolean>>({})

// Helper function to toggle reasoning section
const toggleReasoning = (index: number) => {
  expandedReasoning.value[index] = !expandedReasoning.value[index]
}

// Helper function to get compliance score color
const getComplianceColor = (score: number) => {
  if (score >= 0.85) return 'green'
  if (score >= 0.7) return 'yellow'
  return 'red'
}

// Helper function to get severity color
const getSeverityColor = (severity: string) => {
  switch (severity?.toLowerCase()) {
    case 'critical': return 'red'
    case 'major': return 'orange'
    case 'minor': return 'yellow'
    default: return 'gray'
  }
}

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
      complianceScore: turn.compliance_score,
      // Add new reasoning-related fields
      compliance_reasoning: turn.compliance_reasoning,
      compliance_issues: turn.compliance_issues,
      compliance_passed: turn.compliance_passed,
      requires_human_review: turn.requires_human_review
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

const renderMarkdown = (text: string) => marked.parse(text)
</script>

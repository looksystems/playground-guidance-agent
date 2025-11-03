<template>
  <div class="space-y-8">
    <!-- Key Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <UCard data-testid="metric-card">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total Consultations</p>
            <p class="mt-2 text-4xl font-bold">1,247</p>
            <div class="mt-2 flex items-center gap-1">
              <UIcon name="i-heroicons-arrow-trending-up-solid" class="w-4 h-4 text-green-600" />
              <span class="text-sm font-medium text-green-600">+12%</span>
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
            <p class="mt-2 text-4xl font-bold">96.4%</p>
            <div class="mt-2 flex items-center gap-1">
              <UIcon name="i-heroicons-arrow-trending-up-solid" class="w-4 h-4 text-green-600" />
              <span class="text-sm font-medium text-green-600">+1.2%</span>
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
            <p class="mt-2 text-4xl font-bold">4.2/5.0</p>
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

      <UTable :columns="columns" :rows="consultations" :loading="pending">
        <template #compliance-data="{ row }">
          <UBadge
            :color="getComplianceColor((row as any).compliance)"
            variant="subtle"
          >
            {{ (row as any).compliance }}%
          </UBadge>
        </template>

        <template #satisfaction-data="{ row }">
          <div class="flex items-center gap-2">
            <span>{{ (row as any).satisfactionEmoji }}</span>
            <span class="text-sm">{{ (row as any).satisfactionText }}</span>
          </div>
        </template>

        <template #actions-data="{ row }">
          <UButton
            size="xs"
            @click="navigateTo(`/admin/consultations/${row.id}`)"
          >
            View
          </UButton>
        </template>
      </UTable>
    </UCard>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'admin'
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

// Mock data for development
const consultations = ref<ConsultationRow[]>([
  {
    id: 'C-001',
    customer: 'John Smith',
    topic: 'Retirement Planning',
    date: '2025-11-01',
    messages: 12,
    compliance: 98,
    satisfactionEmoji: '😊',
    satisfactionText: 'Satisfied'
  },
  {
    id: 'C-002',
    customer: 'Jane Doe',
    topic: 'Investment Strategy',
    date: '2025-11-01',
    messages: 8,
    compliance: 96,
    satisfactionEmoji: '😊',
    satisfactionText: 'Satisfied'
  },
  {
    id: 'C-003',
    customer: 'Bob Johnson',
    topic: 'Tax Planning',
    date: '2025-10-31',
    messages: 15,
    compliance: 94,
    satisfactionEmoji: '😐',
    satisfactionText: 'Neutral'
  }
])

const pending = ref(false)

const complianceData = ref({
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
  datasets: [
    {
      label: 'FCA Compliance Score',
      data: [94.2, 95.1, 95.8, 96.0, 96.2, 96.4],
      borderColor: 'rgb(34, 197, 94)',
      backgroundColor: 'rgba(34, 197, 94, 0.1)',
      tension: 0.4
    }
  ]
})

const getComplianceColor = (score: number): 'success' | 'warning' | 'error' => {
  if (score >= 95) return 'success'
  if (score >= 85) return 'warning'
  return 'error'
}
</script>

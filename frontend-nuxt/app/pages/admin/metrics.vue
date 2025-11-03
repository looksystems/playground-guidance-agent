<template>
  <div class="space-y-8">
    <div>
      <h1 class="text-3xl font-bold text-gray-900">Metrics & Analytics</h1>
      <p class="mt-2 text-gray-600">Detailed performance metrics and analytics</p>
    </div>

    <!-- Performance Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <UCard>
        <div>
          <p class="text-sm font-medium text-gray-600">Avg Response Time</p>
          <p class="mt-2 text-3xl font-bold">2.3s</p>
          <div class="mt-2 flex items-center gap-1">
            <UIcon name="i-heroicons-arrow-trending-down-solid" class="w-4 h-4 text-green-600" />
            <span class="text-sm font-medium text-green-600">-0.3s</span>
          </div>
        </div>
      </UCard>

      <UCard>
        <div>
          <p class="text-sm font-medium text-gray-600">Customer Retention</p>
          <p class="mt-2 text-3xl font-bold">87%</p>
          <div class="mt-2 flex items-center gap-1">
            <UIcon name="i-heroicons-arrow-trending-up-solid" class="w-4 h-4 text-green-600" />
            <span class="text-sm font-medium text-green-600">+5%</span>
          </div>
        </div>
      </UCard>

      <UCard>
        <div>
          <p class="text-sm font-medium text-gray-600">Active Sessions</p>
          <p class="mt-2 text-3xl font-bold">142</p>
          <div class="mt-2 flex items-center gap-1">
            <UIcon name="i-heroicons-arrow-trending-up-solid" class="w-4 h-4 text-green-600" />
            <span class="text-sm font-medium text-green-600">+12</span>
          </div>
        </div>
      </UCard>

      <UCard>
        <div>
          <p class="text-sm font-medium text-gray-600">Completion Rate</p>
          <p class="mt-2 text-3xl font-bold">94%</p>
          <div class="mt-2 flex items-center gap-1">
            <UIcon name="i-heroicons-arrow-trending-up-solid" class="w-4 h-4 text-green-600" />
            <span class="text-sm font-medium text-green-600">+2%</span>
          </div>
        </div>
      </UCard>
    </div>

    <!-- Compliance Breakdown -->
    <UCard>
      <template #header>
        <h2 class="text-xl font-semibold">Compliance Breakdown</h2>
      </template>
      <div class="space-y-4">
        <div v-for="item in complianceBreakdown" :key="item.category" class="flex items-center justify-between">
          <div class="flex-1">
            <div class="flex items-center justify-between mb-1">
              <span class="text-sm font-medium text-gray-700">{{ item.category }}</span>
              <span class="text-sm font-semibold text-gray-900">{{ item.score }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div
                class="h-2 rounded-full"
                :class="item.score >= 95 ? 'bg-green-600' : item.score >= 85 ? 'bg-yellow-600' : 'bg-red-600'"
                :style="{ width: `${item.score}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </UCard>

    <!-- Usage Statistics -->
    <UCard>
      <template #header>
        <h2 class="text-xl font-semibold">Usage Statistics</h2>
      </template>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 class="text-sm font-medium text-gray-600 mb-3">Top Topics</h3>
          <div class="space-y-2">
            <div v-for="topic in topTopics" :key="topic.name" class="flex items-center justify-between">
              <span class="text-sm text-gray-700">{{ topic.name }}</span>
              <span class="text-sm font-semibold text-gray-900">{{ topic.count }}</span>
            </div>
          </div>
        </div>
        <div>
          <h3 class="text-sm font-medium text-gray-600 mb-3">Peak Hours</h3>
          <div class="space-y-2">
            <div v-for="hour in peakHours" :key="hour.time" class="flex items-center justify-between">
              <span class="text-sm text-gray-700">{{ hour.time }}</span>
              <span class="text-sm font-semibold text-gray-900">{{ hour.sessions }} sessions</span>
            </div>
          </div>
        </div>
      </div>
    </UCard>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'admin'
})

const complianceBreakdown = ref([
  { category: 'Risk Assessment', score: 98 },
  { category: 'Documentation', score: 96 },
  { category: 'Disclosure Requirements', score: 94 },
  { category: 'Client Suitability', score: 97 },
  { category: 'Regulatory Reporting', score: 95 }
])

const topTopics = ref([
  { name: 'Retirement Planning', count: 342 },
  { name: 'Investment Strategy', count: 298 },
  { name: 'Tax Planning', count: 187 },
  { name: 'Estate Planning', count: 156 },
  { name: 'Pension Transfers', count: 142 }
])

const peakHours = ref([
  { time: '9:00 AM - 10:00 AM', sessions: 45 },
  { time: '2:00 PM - 3:00 PM', sessions: 52 },
  { time: '10:00 AM - 11:00 AM', sessions: 38 },
  { time: '3:00 PM - 4:00 PM', sessions: 41 }
])
</script>

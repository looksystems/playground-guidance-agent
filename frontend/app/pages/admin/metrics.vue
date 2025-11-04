<template>
  <div class="space-y-8">
    <div>
      <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Metrics & Analytics</h1>
      <p class="mt-2 text-gray-600 dark:text-gray-400">Detailed performance metrics and analytics</p>
    </div>

    <!-- Performance Metrics -->
    <div v-if="pending" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <UCard v-for="i in 4" :key="i">
        <div class="animate-pulse">
          <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-32 mb-2"></div>
          <div class="h-8 bg-gray-200 dark:bg-gray-700 rounded w-20 mb-2"></div>
          <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-16"></div>
        </div>
      </UCard>
    </div>

    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
      <p class="text-red-800 dark:text-red-400">Failed to load metrics: {{ error.message }}</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <UCard>
        <div>
          <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Avg Response Time</p>
          <p class="mt-2 text-3xl font-bold text-gray-900 dark:text-gray-100">{{ performanceMetrics.avg_response_time }}s</p>
          <p class="mt-2 text-xs text-gray-500 dark:text-gray-500">First response time</p>
        </div>
      </UCard>

      <UCard>
        <div>
          <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Customer Retention</p>
          <p class="mt-2 text-3xl font-bold text-gray-900 dark:text-gray-100">{{ performanceMetrics.customer_retention }}%</p>
          <p class="mt-2 text-xs text-gray-500 dark:text-gray-500">Returning customers</p>
        </div>
      </UCard>

      <UCard>
        <div>
          <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Active Sessions</p>
          <p class="mt-2 text-3xl font-bold text-gray-900 dark:text-gray-100">{{ performanceMetrics.active_sessions }}</p>
          <p class="mt-2 text-xs text-gray-500 dark:text-gray-500">Currently active</p>
        </div>
      </UCard>

      <UCard>
        <div>
          <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Completion Rate</p>
          <p class="mt-2 text-3xl font-bold text-gray-900 dark:text-gray-100">{{ performanceMetrics.completion_rate }}%</p>
          <p class="mt-2 text-xs text-gray-500 dark:text-gray-500">Consultations completed</p>
        </div>
      </UCard>
    </div>

    <!-- Compliance Breakdown -->
    <UCard v-if="!pending && !error">
      <template #header>
        <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Compliance Breakdown</h2>
      </template>
      <div v-if="complianceBreakdown.length > 0" class="space-y-4">
        <div v-for="item in complianceBreakdown" :key="item.category" class="flex items-center justify-between">
          <div class="flex-1">
            <div class="flex items-center justify-between mb-1">
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ item.category }}</span>
              <span class="text-sm font-semibold text-gray-900 dark:text-gray-100">{{ item.score }}%</span>
            </div>
            <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                class="h-2 rounded-full"
                :class="item.score >= 95 ? 'bg-green-600 dark:bg-green-500' : item.score >= 85 ? 'bg-yellow-600 dark:bg-yellow-500' : 'bg-red-600 dark:bg-red-500'"
                :style="{ width: `${item.score}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="text-center text-gray-500 dark:text-gray-400 py-4">
        No compliance data available
      </div>
    </UCard>

    <!-- Usage Statistics -->
    <UCard v-if="!pending && !error">
      <template #header>
        <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Usage Statistics</h2>
      </template>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-3">Top Topics</h3>
          <div v-if="topTopics.length > 0" class="space-y-2">
            <div v-for="topic in topTopics" :key="topic.name" class="flex items-center justify-between">
              <span class="text-sm text-gray-700 dark:text-gray-300">{{ topic.name }}</span>
              <span class="text-sm font-semibold text-gray-900 dark:text-gray-100">{{ topic.count }}</span>
            </div>
          </div>
          <div v-else class="text-center text-gray-500 dark:text-gray-400 py-2">
            No topic data available
          </div>
        </div>
        <div>
          <h3 class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-3">Peak Hours</h3>
          <div v-if="peakHours.length > 0" class="space-y-2">
            <div v-for="hour in peakHours" :key="hour.time" class="flex items-center justify-between">
              <span class="text-sm text-gray-700 dark:text-gray-300">{{ hour.time }}</span>
              <span class="text-sm font-semibold text-gray-900 dark:text-gray-100">{{ hour.sessions }} sessions</span>
            </div>
          </div>
          <div v-else class="text-center text-gray-500 dark:text-gray-400 py-2">
            No peak hour data available
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

// Fetch metrics from backend API
const { data: metricsData, pending, error } = await useFetch('/api/admin/metrics', {
  query: { days: 30 },
  headers: {
    'Authorization': 'Bearer admin-token'
  }
})

// Extract metrics from API response with defaults
const performanceMetrics = computed(() => metricsData.value?.performance_metrics || {
  avg_response_time: 0,
  customer_retention: 0,
  active_sessions: 0,
  completion_rate: 0
})

const complianceBreakdown = computed(() => metricsData.value?.compliance_breakdown || [])
const topTopics = computed(() => metricsData.value?.top_topics || [])
const peakHours = computed(() => metricsData.value?.peak_hours || [])
const summary = computed(() => metricsData.value?.summary || {
  total_consultations: 0,
  completed_consultations: 0,
  avg_satisfaction: 0,
  period_days: 30
})
</script>

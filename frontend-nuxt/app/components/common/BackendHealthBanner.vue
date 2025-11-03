<template>
  <div v-if="shouldShowBanner" :data-testid="'health-banner'" :class="bannerClasses">
    <div class="flex items-center justify-between gap-4 p-4">
      <div class="flex items-center gap-3">
        <UIcon
          v-if="isChecking"
          name="i-heroicons-arrow-path"
          class="w-5 h-5 animate-spin"
          data-testid="checking-indicator"
        />
        <UIcon
          v-else-if="isErrorState"
          name="i-heroicons-exclamation-circle"
          class="w-5 h-5"
        />
        <UIcon
          v-else
          name="i-heroicons-exclamation-triangle"
          class="w-5 h-5"
        />

        <div class="flex-1">
          <p class="font-semibold">{{ bannerMessage }}</p>
          <p v-if="serviceDetails" class="text-sm opacity-90">{{ serviceDetails }}</p>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <UButton
          data-testid="retry-button"
          :disabled="isChecking"
          size="sm"
          variant="outline"
          @click="handleRetry"
        >
          {{ isChecking ? 'Checking...' : 'Retry' }}
        </UButton>

        <UButton
          v-if="dismissible"
          data-testid="dismiss-button"
          size="sm"
          variant="ghost"
          icon="i-heroicons-x-mark"
          @click="handleDismiss"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useHealthCheck } from '~/composables/useHealthCheck'

const props = withDefaults(defineProps<{
  autoCheck?: boolean
  dismissible?: boolean
  customMessage?: string
}>(), {
  autoCheck: false,
  dismissible: true,
  customMessage: ''
})

const emit = defineEmits<{
  healthStatusChanged: [isHealthy: boolean]
}>()

// Use the health check composable
const { isHealthy, isChecking, healthStatus, error, checkHealth } = useHealthCheck()

// Local state
const isDismissed = ref(false)

// Auto-check on mount if prop is set
if (props.autoCheck) {
  checkHealth()
}

// Computed properties
const shouldShowBanner = computed(() => {
  return !isHealthy.value && !isDismissed.value
})

const isErrorState = computed(() => {
  return healthStatus.value?.status === 'unhealthy' || error.value !== null
})

const bannerClasses = computed(() => {
  const baseClasses = 'rounded-lg border'

  if (isErrorState.value) {
    return `${baseClasses} error bg-red-50 border-red-200 text-red-900`
  } else {
    return `${baseClasses} warning bg-yellow-50 border-yellow-200 text-yellow-900`
  }
})

const bannerMessage = computed(() => {
  if (props.customMessage) {
    return props.customMessage
  }

  if (error.value) {
    if (error.value.includes('Network')) {
      return 'Network error - Unable to connect to backend'
    }
    return 'Backend service unavailable'
  }

  if (healthStatus.value?.status === 'unhealthy') {
    return 'Backend service is currently unavailable'
  }

  if (healthStatus.value?.status === 'degraded') {
    return 'Backend service is running in degraded mode'
  }

  return 'Backend service unavailable'
})

const serviceDetails = computed(() => {
  if (!healthStatus.value) {
    return null
  }

  const failedServices: string[] = []

  if (!healthStatus.value.database) {
    failedServices.push('database')
  }

  if (!healthStatus.value.llm) {
    failedServices.push('AI service')
  }

  if (failedServices.length > 0) {
    return `Issues with: ${failedServices.join(', ')}`
  }

  return null
})

// Event handlers
const handleRetry = async () => {
  await checkHealth()
}

const handleDismiss = () => {
  isDismissed.value = true
}

// Watch health status changes and emit event
watch(isHealthy, (newValue) => {
  emit('healthStatusChanged', newValue)
})
</script>

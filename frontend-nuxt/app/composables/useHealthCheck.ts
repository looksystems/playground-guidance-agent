import { ref, onMounted, onUnmounted } from 'vue'

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy'
  database: boolean
  llm: boolean
  timestamp: string
}

export interface UseHealthCheckOptions {
  autoCheck?: boolean
  backendUrl?: string
  pollInterval?: number
}

export const useHealthCheck = (options: UseHealthCheckOptions = {}) => {
  const {
    autoCheck = false,
    backendUrl = 'http://localhost:8000',
    pollInterval = 0
  } = options

  // Reactive state
  const isHealthy = ref(false)
  const isChecking = ref(false)
  const healthStatus = ref<HealthStatus | null>(null)
  const error = ref<string | null>(null)

  let pollIntervalId: ReturnType<typeof setTimeout> | null = null
  let isPolling = false

  // Check health function
  const checkHealth = async () => {
    isChecking.value = true
    error.value = null

    try {
      const response = await $fetch<HealthStatus>(`${backendUrl}/health`)

      // Validate response has required fields
      if (!response || typeof response.status !== 'string') {
        isHealthy.value = false
        healthStatus.value = null
        return
      }

      healthStatus.value = response
      isHealthy.value = response.status === 'healthy'
    } catch (err: any) {
      isHealthy.value = false
      healthStatus.value = null
      error.value = err.message || 'Health check failed'
    } finally {
      isChecking.value = false
      // Schedule next poll after check completes (if polling is enabled)
      if (isPolling && pollInterval > 0) {
        pollIntervalId = setTimeout(() => {
          pollIntervalId = null // Clear before calling checkHealth
          checkHealth()
        }, pollInterval)
      }
    }
  }

  const startPolling = () => {
    if (isPolling || pollInterval <= 0) return
    isPolling = true
    // Schedule the first poll
    pollIntervalId = setTimeout(() => {
      pollIntervalId = null // Clear before calling checkHealth
      checkHealth()
    }, pollInterval)
  }

  const stopPolling = () => {
    isPolling = false
    if (pollIntervalId) {
      clearTimeout(pollIntervalId)
      pollIntervalId = null
    }
  }

  // Auto-check immediately if requested
  if (autoCheck) {
    // Use setTimeout(0) to run on next tick (works better with fake timers in tests)
    setTimeout(async () => {
      await checkHealth()

      // Setup polling if interval is specified
      if (pollInterval > 0) {
        isPolling = true
        startPolling()
      }
    }, 0)
  }

  // Cleanup polling on unmount (if in a component context)
  try {
    onUnmounted(() => {
      stopPolling()
    })
  } catch (e) {
    // Not in a component context, that's ok
  }

  return {
    isHealthy,
    isChecking,
    healthStatus,
    error,
    checkHealth
  }
}

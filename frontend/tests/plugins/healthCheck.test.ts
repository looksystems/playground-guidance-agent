/**
 * Tests for health check plugin/middleware.
 *
 * Following TDD principles - these tests are written BEFORE implementation.
 * They should fail initially (red phase) and pass after implementation (green phase).
 *
 * This plugin runs health checks on app startup and periodically during runtime.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref } from 'vue'

// Mock the useHealthCheck composable
vi.mock('~/composables/useHealthCheck', () => ({
  useHealthCheck: vi.fn()
}))

describe('Health Check Plugin', () => {
  let mockUseHealthCheck: any

  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()

    mockUseHealthCheck = {
      isHealthy: ref(true),
      isChecking: ref(false),
      healthStatus: ref(null),
      error: ref(null),
      checkHealth: vi.fn().mockResolvedValue(undefined)
    }

    const { useHealthCheck } = require('~/composables/useHealthCheck')
    vi.mocked(useHealthCheck).mockReturnValue(mockUseHealthCheck)
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('should be defined as a plugin', () => {
    const healthCheckPlugin = require('~/plugins/healthCheck').default
    expect(healthCheckPlugin).toBeDefined()
    expect(healthCheckPlugin).toBeTypeOf('function')
  })

  it('should check health on app initialization', async () => {
    const healthCheckPlugin = require('~/plugins/healthCheck').default

    // Mock Nuxt app context
    const mockNuxtApp = {
      provide: vi.fn(),
      hook: vi.fn()
    }

    await healthCheckPlugin(mockNuxtApp)

    expect(mockUseHealthCheck.checkHealth).toHaveBeenCalled()
  })

  it('should provide health check composable to the app', async () => {
    const healthCheckPlugin = require('~/plugins/healthCheck').default

    const mockNuxtApp = {
      provide: vi.fn(),
      hook: vi.fn()
    }

    await healthCheckPlugin(mockNuxtApp)

    expect(mockNuxtApp.provide).toHaveBeenCalled()
    expect(mockNuxtApp.provide).toHaveBeenCalledWith(
      expect.stringContaining('health'),
      expect.any(Object)
    )
  })

  it('should setup periodic health checks', async () => {
    const healthCheckPlugin = require('~/plugins/healthCheck').default

    const mockNuxtApp = {
      provide: vi.fn(),
      hook: vi.fn()
    }

    await healthCheckPlugin(mockNuxtApp)

    // Initial check
    expect(mockUseHealthCheck.checkHealth).toHaveBeenCalledTimes(1)

    // Advance time by 30 seconds (default interval)
    vi.advanceTimersByTime(30000)
    await vi.runAllTimersAsync()

    expect(mockUseHealthCheck.checkHealth).toHaveBeenCalledTimes(2)
  })

  it('should allow configuring check interval', async () => {
    const healthCheckPlugin = require('~/plugins/healthCheck').default

    const mockNuxtApp = {
      provide: vi.fn(),
      hook: vi.fn(),
      $config: {
        public: {
          healthCheckInterval: 60000 // 1 minute
        }
      }
    }

    await healthCheckPlugin(mockNuxtApp)

    // Initial check
    expect(mockUseHealthCheck.checkHealth).toHaveBeenCalledTimes(1)

    // Advance time by 30 seconds - should NOT trigger
    vi.advanceTimersByTime(30000)
    await vi.runAllTimersAsync()
    expect(mockUseHealthCheck.checkHealth).toHaveBeenCalledTimes(1)

    // Advance time by another 30 seconds (total 60s) - should trigger
    vi.advanceTimersByTime(30000)
    await vi.runAllTimersAsync()
    expect(mockUseHealthCheck.checkHealth).toHaveBeenCalledTimes(2)
  })

  it('should cleanup interval on app unmount', async () => {
    const healthCheckPlugin = require('~/plugins/healthCheck').default

    const mockNuxtApp = {
      provide: vi.fn(),
      hook: vi.fn()
    }

    await healthCheckPlugin(mockNuxtApp)

    // Get the cleanup function passed to app:unmounted hook
    const hookCalls = mockNuxtApp.hook.mock.calls
    const unmountHook = hookCalls.find(call => call[0] === 'app:unmounted')

    expect(unmountHook).toBeDefined()

    // Call the cleanup function
    if (unmountHook) {
      const cleanup = unmountHook[1]
      cleanup()

      // After cleanup, advancing time should not trigger more checks
      const callsBefore = mockUseHealthCheck.checkHealth.mock.calls.length
      vi.advanceTimersByTime(60000)
      await vi.runAllTimersAsync()
      const callsAfter = mockUseHealthCheck.checkHealth.mock.calls.length

      expect(callsAfter).toBe(callsBefore)
    }
  })

  it('should handle errors during health check gracefully', async () => {
    mockUseHealthCheck.checkHealth.mockRejectedValue(new Error('Health check failed'))

    const healthCheckPlugin = require('~/plugins/healthCheck').default

    const mockNuxtApp = {
      provide: vi.fn(),
      hook: vi.fn()
    }

    // Should not throw error
    await expect(healthCheckPlugin(mockNuxtApp)).resolves.not.toThrow()
  })

  it('should not start periodic checks if disabled in config', async () => {
    const healthCheckPlugin = require('~/plugins/healthCheck').default

    const mockNuxtApp = {
      provide: vi.fn(),
      hook: vi.fn(),
      $config: {
        public: {
          healthCheckEnabled: false
        }
      }
    }

    await healthCheckPlugin(mockNuxtApp)

    // Should still do initial check
    expect(mockUseHealthCheck.checkHealth).toHaveBeenCalledTimes(1)

    // Should not setup periodic checks
    vi.advanceTimersByTime(30000)
    await vi.runAllTimersAsync()
    expect(mockUseHealthCheck.checkHealth).toHaveBeenCalledTimes(1)
  })

  it('should expose health status to global state', async () => {
    const healthCheckPlugin = require('~/plugins/healthCheck').default

    const mockNuxtApp = {
      provide: vi.fn(),
      hook: vi.fn(),
      payload: {
        state: {}
      }
    }

    await healthCheckPlugin(mockNuxtApp)

    // Should provide access to health check state
    const provideCalls = mockNuxtApp.provide.mock.calls
    const healthProvide = provideCalls.find(call =>
      call[0] === 'healthCheck' || call[0] === 'backendHealth'
    )

    expect(healthProvide).toBeDefined()
    expect(healthProvide?.[1]).toMatchObject({
      isHealthy: expect.any(Object),
      checkHealth: expect.any(Function)
    })
  })

  it('should retry failed health checks with exponential backoff', async () => {
    let callCount = 0
    mockUseHealthCheck.checkHealth.mockImplementation(() => {
      callCount++
      if (callCount < 3) {
        mockUseHealthCheck.isHealthy.value = false
        return Promise.reject(new Error('Failed'))
      }
      mockUseHealthCheck.isHealthy.value = true
      return Promise.resolve()
    })

    const healthCheckPlugin = require('~/plugins/healthCheck').default

    const mockNuxtApp = {
      provide: vi.fn(),
      hook: vi.fn(),
      $config: {
        public: {
          healthCheckRetryEnabled: true,
          healthCheckRetryMax: 3
        }
      }
    }

    await healthCheckPlugin(mockNuxtApp)

    // Initial check (fails)
    expect(mockUseHealthCheck.checkHealth).toHaveBeenCalledTimes(1)

    // First retry after 2 seconds
    vi.advanceTimersByTime(2000)
    await vi.runAllTimersAsync()
    expect(mockUseHealthCheck.checkHealth).toHaveBeenCalledTimes(2)

    // Second retry after 4 seconds (exponential backoff)
    vi.advanceTimersByTime(4000)
    await vi.runAllTimersAsync()
    expect(mockUseHealthCheck.checkHealth).toHaveBeenCalledTimes(3)

    // Success - should stop retrying
    expect(mockUseHealthCheck.isHealthy.value).toBe(true)
  })

  it('should log health check results in development mode', async () => {
    const consoleLog = vi.spyOn(console, 'log').mockImplementation(() => {})

    const healthCheckPlugin = require('~/plugins/healthCheck').default

    const mockNuxtApp = {
      provide: vi.fn(),
      hook: vi.fn(),
      $config: {
        public: {
          dev: true
        }
      }
    }

    await healthCheckPlugin(mockNuxtApp)

    expect(consoleLog).toHaveBeenCalledWith(
      expect.stringContaining('health'),
      expect.anything()
    )

    consoleLog.mockRestore()
  })
})

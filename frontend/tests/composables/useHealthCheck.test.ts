/**
 * Tests for useHealthCheck composable.
 *
 * Following TDD principles - these tests are written BEFORE implementation.
 * They should fail initially (red phase) and pass after implementation (green phase).
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref } from 'vue'

// Mock $fetch globally
global.$fetch = vi.fn() as any

describe('useHealthCheck', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('should be defined as a function', () => {
    // This test will fail until we create the composable
    const { useHealthCheck } = require('~/composables/useHealthCheck')
    expect(useHealthCheck).toBeTypeOf('function')
  })

  it('should return expected reactive properties', () => {
    const { useHealthCheck } = require('~/composables/useHealthCheck')
    const { isHealthy, isChecking, healthStatus, error, checkHealth } = useHealthCheck()

    expect(isHealthy).toBeDefined()
    expect(isChecking).toBeDefined()
    expect(healthStatus).toBeDefined()
    expect(error).toBeDefined()
    expect(checkHealth).toBeTypeOf('function')
  })

  it('should initialize with default values', () => {
    const { useHealthCheck } = require('~/composables/useHealthCheck')
    const { isHealthy, isChecking, healthStatus, error } = useHealthCheck()

    // Initial state before any check
    expect(isHealthy.value).toBe(false)
    expect(isChecking.value).toBe(false)
    expect(healthStatus.value).toBeNull()
    expect(error.value).toBeNull()
  })

  it('should call backend health endpoint', async () => {
    vi.mocked($fetch).mockResolvedValue({
      status: 'healthy',
      database: true,
      llm: true,
      timestamp: new Date().toISOString()
    })

    const { useHealthCheck } = require('~/composables/useHealthCheck')
    const { checkHealth } = useHealthCheck()

    await checkHealth()

    expect($fetch).toHaveBeenCalledWith('http://localhost:8000/health')
  })

  it('should set isChecking to true while checking', async () => {
    let resolvePromise: (value: any) => void
    const promise = new Promise((resolve) => {
      resolvePromise = resolve
    })

    vi.mocked($fetch).mockReturnValue(promise as any)

    const { useHealthCheck } = require('~/composables/useHealthCheck')
    const { isChecking, checkHealth } = useHealthCheck()

    const checkPromise = checkHealth()

    // Should be checking during the request
    expect(isChecking.value).toBe(true)

    resolvePromise!({
      status: 'healthy',
      database: true,
      llm: true,
      timestamp: new Date().toISOString()
    })

    await checkPromise

    // Should not be checking after request completes
    expect(isChecking.value).toBe(false)
  })

  it('should set isHealthy to true when backend is healthy', async () => {
    vi.mocked($fetch).mockResolvedValue({
      status: 'healthy',
      database: true,
      llm: true,
      timestamp: new Date().toISOString()
    })

    const { useHealthCheck } = require('~/composables/useHealthCheck')
    const { isHealthy, checkHealth } = useHealthCheck()

    await checkHealth()

    expect(isHealthy.value).toBe(true)
  })

  it('should set isHealthy to false when backend status is degraded', async () => {
    vi.mocked($fetch).mockResolvedValue({
      status: 'degraded',
      database: true,
      llm: false,
      timestamp: new Date().toISOString()
    })

    const { useHealthCheck } = require('~/composables/useHealthCheck')
    const { isHealthy, checkHealth } = useHealthCheck()

    await checkHealth()

    expect(isHealthy.value).toBe(false)
  })

  it('should set isHealthy to false when backend status is unhealthy', async () => {
    vi.mocked($fetch).mockResolvedValue({
      status: 'unhealthy',
      database: false,
      llm: false,
      timestamp: new Date().toISOString()
    })

    const { useHealthCheck } = require('~/composables/useHealthCheck')
    const { isHealthy, checkHealth } = useHealthCheck()

    await checkHealth()

    expect(isHealthy.value).toBe(false)
  })

  it('should store full health status response', async () => {
    const mockResponse = {
      status: 'healthy',
      database: true,
      llm: true,
      timestamp: new Date().toISOString()
    }

    vi.mocked($fetch).mockResolvedValue(mockResponse)

    const { useHealthCheck } = require('~/composables/useHealthCheck')
    const { healthStatus, checkHealth } = useHealthCheck()

    await checkHealth()

    expect(healthStatus.value).toEqual(mockResponse)
  })

  it('should handle network errors gracefully', async () => {
    const networkError = new Error('Network request failed')
    vi.mocked($fetch).mockRejectedValue(networkError)

    const { useHealthCheck } = require('~/composables/useHealthCheck')
    const { isHealthy, error, checkHealth } = useHealthCheck()

    await checkHealth()

    expect(isHealthy.value).toBe(false)
    expect(error.value).toBeDefined()
    expect(error.value).toContain('Network request failed')
  })

  it('should handle timeout errors', async () => {
    const timeoutError = new Error('Request timeout')
    vi.mocked($fetch).mockRejectedValue(timeoutError)

    const { useHealthCheck } = require('~/composables/useHealthCheck')
    const { isHealthy, error, checkHealth } = useHealthCheck()

    await checkHealth()

    expect(isHealthy.value).toBe(false)
    expect(error.value).toBeTruthy()
  })

  it('should handle backend returning 500 error', async () => {
    const serverError = new Error('Internal Server Error')
    vi.mocked($fetch).mockRejectedValue(serverError)

    const { useHealthCheck } = require('~/composables/useHealthCheck')
    const { isHealthy, error, checkHealth } = useHealthCheck()

    await checkHealth()

    expect(isHealthy.value).toBe(false)
    expect(error.value).toBeTruthy()
  })

  it('should clear previous error on successful check', async () => {
    const { useHealthCheck } = require('~/composables/useHealthCheck')
    const { error, checkHealth } = useHealthCheck()

    // First call fails
    vi.mocked($fetch).mockRejectedValue(new Error('Failed'))
    await checkHealth()
    expect(error.value).toBeTruthy()

    // Second call succeeds
    vi.mocked($fetch).mockResolvedValue({
      status: 'healthy',
      database: true,
      llm: true,
      timestamp: new Date().toISOString()
    })
    await checkHealth()

    expect(error.value).toBeNull()
  })

  it('should support automatic health check on mount with autoCheck option', async () => {
    vi.mocked($fetch).mockResolvedValue({
      status: 'healthy',
      database: true,
      llm: true,
      timestamp: new Date().toISOString()
    })

    const { useHealthCheck } = require('~/composables/useHealthCheck')
    const { checkHealth } = useHealthCheck({ autoCheck: true })

    // Wait a bit for auto-check to trigger
    await new Promise(resolve => setTimeout(resolve, 10))

    expect($fetch).toHaveBeenCalled()
  })

  it('should not auto-check when autoCheck is false', async () => {
    const { useHealthCheck } = require('~/composables/useHealthCheck')
    useHealthCheck({ autoCheck: false })

    await new Promise(resolve => setTimeout(resolve, 10))

    expect($fetch).not.toHaveBeenCalled()
  })

  it('should support custom backend URL', async () => {
    vi.mocked($fetch).mockResolvedValue({
      status: 'healthy',
      database: true,
      llm: true,
      timestamp: new Date().toISOString()
    })

    const { useHealthCheck } = require('~/composables/useHealthCheck')
    const { checkHealth } = useHealthCheck({
      backendUrl: 'http://custom-backend:9000'
    })

    await checkHealth()

    expect($fetch).toHaveBeenCalledWith('http://custom-backend:9000/health')
  })

  it('should allow retrying failed health checks', async () => {
    let callCount = 0
    vi.mocked($fetch).mockImplementation(() => {
      callCount++
      if (callCount < 3) {
        return Promise.reject(new Error('Failed'))
      }
      return Promise.resolve({
        status: 'healthy',
        database: true,
        llm: true,
        timestamp: new Date().toISOString()
      })
    })

    const { useHealthCheck } = require('~/composables/useHealthCheck')
    const { isHealthy, checkHealth } = useHealthCheck()

    // First attempt fails
    await checkHealth()
    expect(isHealthy.value).toBe(false)

    // Second attempt fails
    await checkHealth()
    expect(isHealthy.value).toBe(false)

    // Third attempt succeeds
    await checkHealth()
    expect(isHealthy.value).toBe(true)
  })

  it('should provide detailed health status information', async () => {
    vi.mocked($fetch).mockResolvedValue({
      status: 'degraded',
      database: true,
      llm: false,
      timestamp: new Date().toISOString()
    })

    const { useHealthCheck } = require('~/composables/useHealthCheck')
    const { healthStatus, checkHealth } = useHealthCheck()

    await checkHealth()

    expect(healthStatus.value?.status).toBe('degraded')
    expect(healthStatus.value?.database).toBe(true)
    expect(healthStatus.value?.llm).toBe(false)
  })

  it('should handle malformed response from backend', async () => {
    vi.mocked($fetch).mockResolvedValue({
      // Missing required fields
      timestamp: new Date().toISOString()
    })

    const { useHealthCheck } = require('~/composables/useHealthCheck')
    const { isHealthy, error, checkHealth } = useHealthCheck()

    await checkHealth()

    // Should treat malformed response as unhealthy
    expect(isHealthy.value).toBe(false)
  })

  it('should support polling with interval option', async () => {
    vi.useFakeTimers()

    vi.mocked($fetch).mockResolvedValue({
      status: 'healthy',
      database: true,
      llm: true,
      timestamp: new Date().toISOString()
    })

    const { useHealthCheck } = require('~/composables/useHealthCheck')
    useHealthCheck({
      autoCheck: true,
      pollInterval: 5000 // 5 seconds
    })

    // Initial call
    await vi.runAllTimersAsync()
    expect($fetch).toHaveBeenCalledTimes(1)

    // After 5 seconds
    vi.advanceTimersByTime(5000)
    await vi.runAllTimersAsync()
    expect($fetch).toHaveBeenCalledTimes(2)

    // After another 5 seconds
    vi.advanceTimersByTime(5000)
    await vi.runAllTimersAsync()
    expect($fetch).toHaveBeenCalledTimes(3)

    vi.useRealTimers()
  })
})

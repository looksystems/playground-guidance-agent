/**
 * Tests for BackendHealthBanner component.
 *
 * Following TDD principles - these tests are written BEFORE implementation.
 * They should fail initially (red phase) and pass after implementation (green phase).
 *
 * This component displays a banner when the backend is unavailable or degraded.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref } from 'vue'

// Mock the useHealthCheck composable
vi.mock('~/composables/useHealthCheck', () => ({
  useHealthCheck: vi.fn()
}))

describe('BackendHealthBanner', () => {
  let mockUseHealthCheck: any

  beforeEach(() => {
    vi.clearAllMocks()

    // Default mock implementation
    mockUseHealthCheck = {
      isHealthy: ref(true),
      isChecking: ref(false),
      healthStatus: ref(null),
      error: ref(null),
      checkHealth: vi.fn()
    }

    const { useHealthCheck } = require('~/composables/useHealthCheck')
    vi.mocked(useHealthCheck).mockReturnValue(mockUseHealthCheck)
  })

  it('should be defined as a component', () => {
    const BackendHealthBanner = require('~/components/common/BackendHealthBanner.vue').default
    expect(BackendHealthBanner).toBeDefined()
  })

  it('should not display banner when backend is healthy', () => {
    mockUseHealthCheck.isHealthy.value = true

    const BackendHealthBanner = require('~/components/common/BackendHealthBanner.vue').default
    const wrapper = mount(BackendHealthBanner)

    expect(wrapper.find('[data-testid="health-banner"]').exists()).toBe(false)
  })

  it('should display banner when backend is unhealthy', () => {
    mockUseHealthCheck.isHealthy.value = false
    mockUseHealthCheck.healthStatus.value = {
      status: 'unhealthy',
      database: false,
      llm: false
    }

    const BackendHealthBanner = require('~/components/common/BackendHealthBanner.vue').default
    const wrapper = mount(BackendHealthBanner)

    expect(wrapper.find('[data-testid="health-banner"]').exists()).toBe(true)
  })

  it('should display banner when backend is degraded', () => {
    mockUseHealthCheck.isHealthy.value = false
    mockUseHealthCheck.healthStatus.value = {
      status: 'degraded',
      database: true,
      llm: false
    }

    const BackendHealthBanner = require('~/components/common/BackendHealthBanner.vue').default
    const wrapper = mount(BackendHealthBanner)

    expect(wrapper.find('[data-testid="health-banner"]').exists()).toBe(true)
  })

  it('should display error message when backend is completely down', () => {
    mockUseHealthCheck.isHealthy.value = false
    mockUseHealthCheck.healthStatus.value = {
      status: 'unhealthy',
      database: false,
      llm: false
    }

    const BackendHealthBanner = require('~/components/common/BackendHealthBanner.vue').default
    const wrapper = mount(BackendHealthBanner)

    const banner = wrapper.find('[data-testid="health-banner"]')
    expect(banner.text()).toContain('backend')
    expect(banner.text()).toContain('unavailable')
  })

  it('should display warning message when backend is degraded', () => {
    mockUseHealthCheck.isHealthy.value = false
    mockUseHealthCheck.healthStatus.value = {
      status: 'degraded',
      database: true,
      llm: false
    }

    const BackendHealthBanner = require('~/components/common/BackendHealthBanner.vue').default
    const wrapper = mount(BackendHealthBanner)

    const banner = wrapper.find('[data-testid="health-banner"]')
    expect(banner.text()).toContain('degraded')
  })

  it('should show specific error when network error occurs', () => {
    mockUseHealthCheck.isHealthy.value = false
    mockUseHealthCheck.error.value = 'Network request failed'

    const BackendHealthBanner = require('~/components/common/BackendHealthBanner.vue').default
    const wrapper = mount(BackendHealthBanner)

    const banner = wrapper.find('[data-testid="health-banner"]')
    expect(banner.text()).toContain('Network')
  })

  it('should have retry button when backend is down', () => {
    mockUseHealthCheck.isHealthy.value = false
    mockUseHealthCheck.healthStatus.value = {
      status: 'unhealthy',
      database: false,
      llm: false
    }

    const BackendHealthBanner = require('~/components/common/BackendHealthBanner.vue').default
    const wrapper = mount(BackendHealthBanner)

    expect(wrapper.find('[data-testid="retry-button"]').exists()).toBe(true)
  })

  it('should call checkHealth when retry button is clicked', async () => {
    mockUseHealthCheck.isHealthy.value = false
    mockUseHealthCheck.healthStatus.value = {
      status: 'unhealthy',
      database: false,
      llm: false
    }

    const BackendHealthBanner = require('~/components/common/BackendHealthBanner.vue').default
    const wrapper = mount(BackendHealthBanner)

    const retryButton = wrapper.find('[data-testid="retry-button"]')
    await retryButton.trigger('click')

    expect(mockUseHealthCheck.checkHealth).toHaveBeenCalled()
  })

  it('should show loading state while checking health', () => {
    mockUseHealthCheck.isHealthy.value = false
    mockUseHealthCheck.isChecking.value = true

    const BackendHealthBanner = require('~/components/common/BackendHealthBanner.vue').default
    const wrapper = mount(BackendHealthBanner)

    expect(wrapper.find('[data-testid="checking-indicator"]').exists()).toBe(true)
  })

  it('should disable retry button while checking', () => {
    mockUseHealthCheck.isHealthy.value = false
    mockUseHealthCheck.isChecking.value = true

    const BackendHealthBanner = require('~/components/common/BackendHealthBanner.vue').default
    const wrapper = mount(BackendHealthBanner)

    const retryButton = wrapper.find('[data-testid="retry-button"]')
    expect(retryButton.attributes('disabled')).toBeDefined()
  })

  it('should use error styling for unhealthy status', () => {
    mockUseHealthCheck.isHealthy.value = false
    mockUseHealthCheck.healthStatus.value = {
      status: 'unhealthy',
      database: false,
      llm: false
    }

    const BackendHealthBanner = require('~/components/common/BackendHealthBanner.vue').default
    const wrapper = mount(BackendHealthBanner)

    const banner = wrapper.find('[data-testid="health-banner"]')
    expect(banner.classes()).toContain('error')
  })

  it('should use warning styling for degraded status', () => {
    mockUseHealthCheck.isHealthy.value = false
    mockUseHealthCheck.healthStatus.value = {
      status: 'degraded',
      database: true,
      llm: false
    }

    const BackendHealthBanner = require('~/components/common/BackendHealthBanner.vue').default
    const wrapper = mount(BackendHealthBanner)

    const banner = wrapper.find('[data-testid="health-banner"]')
    expect(banner.classes()).toContain('warning')
  })

  it('should show which services are down', () => {
    mockUseHealthCheck.isHealthy.value = false
    mockUseHealthCheck.healthStatus.value = {
      status: 'degraded',
      database: true,
      llm: false
    }

    const BackendHealthBanner = require('~/components/common/BackendHealthBanner.vue').default
    const wrapper = mount(BackendHealthBanner)

    const banner = wrapper.find('[data-testid="health-banner"]')
    expect(banner.text()).toContain('AI')
  })

  it('should hide banner on dismiss button click', async () => {
    mockUseHealthCheck.isHealthy.value = false
    mockUseHealthCheck.healthStatus.value = {
      status: 'degraded',
      database: true,
      llm: false
    }

    const BackendHealthBanner = require('~/components/common/BackendHealthBanner.vue').default
    const wrapper = mount(BackendHealthBanner)

    expect(wrapper.find('[data-testid="health-banner"]').exists()).toBe(true)

    const dismissButton = wrapper.find('[data-testid="dismiss-button"]')
    await dismissButton.trigger('click')

    expect(wrapper.find('[data-testid="health-banner"]').exists()).toBe(false)
  })

  it('should support prop to prevent dismissing', () => {
    mockUseHealthCheck.isHealthy.value = false
    mockUseHealthCheck.healthStatus.value = {
      status: 'unhealthy',
      database: false,
      llm: false
    }

    const BackendHealthBanner = require('~/components/common/BackendHealthBanner.vue').default
    const wrapper = mount(BackendHealthBanner, {
      props: {
        dismissible: false
      }
    })

    expect(wrapper.find('[data-testid="dismiss-button"]').exists()).toBe(false)
  })

  it('should check health on mount with autoCheck prop', () => {
    const BackendHealthBanner = require('~/components/common/BackendHealthBanner.vue').default
    mount(BackendHealthBanner, {
      props: {
        autoCheck: true
      }
    })

    expect(mockUseHealthCheck.checkHealth).toHaveBeenCalled()
  })

  it('should not check health on mount without autoCheck prop', () => {
    const BackendHealthBanner = require('~/components/common/BackendHealthBanner.vue').default
    mount(BackendHealthBanner, {
      props: {
        autoCheck: false
      }
    })

    expect(mockUseHealthCheck.checkHealth).not.toHaveBeenCalled()
  })

  it('should emit event when health status changes', async () => {
    const BackendHealthBanner = require('~/components/common/BackendHealthBanner.vue').default
    const wrapper = mount(BackendHealthBanner)

    // Change health status
    mockUseHealthCheck.isHealthy.value = false
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('healthStatusChanged')).toBeTruthy()
  })

  it('should show different messages for database vs LLM failures', () => {
    // Test database failure
    mockUseHealthCheck.isHealthy.value = false
    mockUseHealthCheck.healthStatus.value = {
      status: 'degraded',
      database: false,
      llm: true
    }

    const BackendHealthBanner = require('~/components/common/BackendHealthBanner.vue').default
    const wrapper = mount(BackendHealthBanner)

    expect(wrapper.find('[data-testid="health-banner"]').text()).toContain('database')
  })

  it('should support custom message prop', () => {
    mockUseHealthCheck.isHealthy.value = false
    mockUseHealthCheck.healthStatus.value = {
      status: 'unhealthy',
      database: false,
      llm: false
    }

    const BackendHealthBanner = require('~/components/common/BackendHealthBanner.vue').default
    const wrapper = mount(BackendHealthBanner, {
      props: {
        customMessage: 'System maintenance in progress'
      }
    })

    expect(wrapper.find('[data-testid="health-banner"]').text()).toContain('System maintenance')
  })
})

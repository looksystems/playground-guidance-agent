import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import CustomerProfileForm from '~/components/forms/CustomerProfileForm.vue'

describe('CustomerProfileForm - API Integration Tests', () => {
  let fetchMock: ReturnType<typeof vi.fn>
  let navigateToMock: ReturnType<typeof vi.fn>

  beforeEach(() => {
    vi.clearAllMocks()
    fetchMock = vi.fn()
    navigateToMock = vi.fn()
    global.$fetch = fetchMock
    global.navigateTo = navigateToMock
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('API Endpoint Verification', () => {
    it('should call POST /api/consultations endpoint', async () => {
      // Arrange
      const mockResponse = {
        id: 'consultation-123',
        customer_id: 'customer-456',
        advisor_name: 'AI Advisor',
        status: 'active',
        created_at: '2024-01-01T00:00:00Z'
      }
      fetchMock.mockResolvedValue(mockResponse)

      const wrapper = mount(CustomerProfileForm, {
        global: {
          stubs: {
            UCard: { template: '<div><slot name="header" /><slot /></div>' },
            UForm: {
              template: '<form @submit.prevent="$attrs.onSubmit"><slot /></form>',
              props: ['schema', 'state']
            },
            UFormField: {
              template: '<div><slot /></div>',
              props: ['label', 'name', 'required', 'size']
            },
            UInput: {
              template: '<input v-bind="$attrs" @input="$emit(\'update:modelValue\', $event.target.value)" />',
              props: ['modelValue', 'name', 'type', 'placeholder', 'size', 'min', 'max', 'required']
            },
            URadioGroup: {
              template: '<div />',
              props: ['modelValue', 'items', 'required']
            },
            UAlert: { template: '<div />' },
            UButton: {
              template: '<button type="submit"><slot /></button>',
              props: ['type', 'size', 'block', 'loading', 'disabled']
            },
            UIcon: { template: '<span />' }
          }
        }
      })

      // Act
      const formData = {
        firstName: 'John',
        age: 55,
        topic: 'consolidation'
      }
      await wrapper.vm.onSubmit({ data: formData })
      await flushPromises()

      // Assert
      expect(fetchMock).toHaveBeenCalledTimes(1)
      expect(fetchMock).toHaveBeenCalledWith(
        '/api/consultations',
        expect.any(Object)
      )
    })

    it('should use POST method for the API call', async () => {
      // Arrange
      const mockResponse = {
        id: 'consultation-123',
        customer_id: 'customer-456',
        advisor_name: 'AI Advisor',
        status: 'active',
        created_at: '2024-01-01T00:00:00Z'
      }
      fetchMock.mockResolvedValue(mockResponse)

      const wrapper = mount(CustomerProfileForm, {
        global: {
          stubs: {
            UCard: { template: '<div><slot /></div>' },
            UForm: { template: '<form @submit.prevent="$attrs.onSubmit"><slot /></form>' },
            UFormField: { template: '<div><slot /></div>' },
            UInput: { template: '<input />' },
            URadioGroup: { template: '<div />' },
            UAlert: { template: '<div />' },
            UButton: { template: '<button type="submit" />' }
          }
        }
      })

      // Act
      await wrapper.vm.onSubmit({
        data: { firstName: 'John', age: 55, topic: 'consolidation' }
      })
      await flushPromises()

      // Assert
      expect(fetchMock).toHaveBeenCalledWith(
        '/api/consultations',
        expect.objectContaining({
          method: 'POST'
        })
      )
    })
  })

  describe('Request Payload Mapping', () => {
    it('should map firstName to name in the request payload', async () => {
      // Arrange
      const mockResponse = {
        id: 'consultation-123',
        customer_id: 'customer-456',
        advisor_name: 'AI Advisor',
        status: 'active',
        created_at: '2024-01-01T00:00:00Z'
      }
      fetchMock.mockResolvedValue(mockResponse)

      const wrapper = mount(CustomerProfileForm, {
        global: {
          stubs: {
            UCard: { template: '<div><slot /></div>' },
            UForm: { template: '<form @submit.prevent="$attrs.onSubmit"><slot /></form>' },
            UFormField: { template: '<div><slot /></div>' },
            UInput: { template: '<input />' },
            URadioGroup: { template: '<div />' },
            UAlert: { template: '<div />' },
            UButton: { template: '<button type="submit" />' }
          }
        }
      })

      // Act
      await wrapper.vm.onSubmit({
        data: { firstName: 'Jane', age: 60, topic: 'withdrawal' }
      })
      await flushPromises()

      // Assert
      expect(fetchMock).toHaveBeenCalledWith(
        '/api/consultations',
        expect.objectContaining({
          body: expect.objectContaining({
            name: 'Jane'
          })
        })
      )
    })

    it('should map topic to initial_query in the request payload', async () => {
      // Arrange
      const mockResponse = {
        id: 'consultation-123',
        customer_id: 'customer-456',
        advisor_name: 'AI Advisor',
        status: 'active',
        created_at: '2024-01-01T00:00:00Z'
      }
      fetchMock.mockResolvedValue(mockResponse)

      const wrapper = mount(CustomerProfileForm, {
        global: {
          stubs: {
            UCard: { template: '<div><slot /></div>' },
            UForm: { template: '<form @submit.prevent="$attrs.onSubmit"><slot /></form>' },
            UFormField: { template: '<div><slot /></div>' },
            UInput: { template: '<input />' },
            URadioGroup: { template: '<div />' },
            UAlert: { template: '<div />' },
            UButton: { template: '<button type="submit" />' }
          }
        }
      })

      // Act
      await wrapper.vm.onSubmit({
        data: { firstName: 'Jane', age: 60, topic: 'understanding' }
      })
      await flushPromises()

      // Assert
      expect(fetchMock).toHaveBeenCalledWith(
        '/api/consultations',
        expect.objectContaining({
          body: expect.objectContaining({
            initial_query: 'understanding'
          })
        })
      )
    })

    it('should pass age directly without transformation', async () => {
      // Arrange
      const mockResponse = {
        id: 'consultation-123',
        customer_id: 'customer-456',
        advisor_name: 'AI Advisor',
        status: 'active',
        created_at: '2024-01-01T00:00:00Z'
      }
      fetchMock.mockResolvedValue(mockResponse)

      const wrapper = mount(CustomerProfileForm, {
        global: {
          stubs: {
            UCard: { template: '<div><slot /></div>' },
            UForm: { template: '<form @submit.prevent="$attrs.onSubmit"><slot /></form>' },
            UFormField: { template: '<div><slot /></div>' },
            UInput: { template: '<input />' },
            URadioGroup: { template: '<div />' },
            UAlert: { template: '<div />' },
            UButton: { template: '<button type="submit" />' }
          }
        }
      })

      // Act
      await wrapper.vm.onSubmit({
        data: { firstName: 'Jane', age: 65, topic: 'tax' }
      })
      await flushPromises()

      // Assert
      expect(fetchMock).toHaveBeenCalledWith(
        '/api/consultations',
        expect.objectContaining({
          body: expect.objectContaining({
            age: 65
          })
        })
      )
    })

    it('should send complete payload with all three required fields', async () => {
      // Arrange
      const mockResponse = {
        id: 'consultation-123',
        customer_id: 'customer-456',
        advisor_name: 'AI Advisor',
        status: 'active',
        created_at: '2024-01-01T00:00:00Z'
      }
      fetchMock.mockResolvedValue(mockResponse)

      const wrapper = mount(CustomerProfileForm, {
        global: {
          stubs: {
            UCard: { template: '<div><slot /></div>' },
            UForm: { template: '<form @submit.prevent="$attrs.onSubmit"><slot /></form>' },
            UFormField: { template: '<div><slot /></div>' },
            UInput: { template: '<input />' },
            URadioGroup: { template: '<div />' },
            UAlert: { template: '<div />' },
            UButton: { template: '<button type="submit" />' }
          }
        }
      })

      // Act
      await wrapper.vm.onSubmit({
        data: { firstName: 'Alice', age: 70, topic: 'other' }
      })
      await flushPromises()

      // Assert
      expect(fetchMock).toHaveBeenCalledWith(
        '/api/consultations',
        expect.objectContaining({
          method: 'POST',
          body: {
            name: 'Alice',
            age: 70,
            initial_query: 'other'
          }
        })
      )
    })

    it('should not send firstName field in the payload', async () => {
      // Arrange
      const mockResponse = {
        id: 'consultation-123',
        customer_id: 'customer-456',
        advisor_name: 'AI Advisor',
        status: 'active',
        created_at: '2024-01-01T00:00:00Z'
      }
      fetchMock.mockResolvedValue(mockResponse)

      const wrapper = mount(CustomerProfileForm, {
        global: {
          stubs: {
            UCard: { template: '<div><slot /></div>' },
            UForm: { template: '<form @submit.prevent="$attrs.onSubmit"><slot /></form>' },
            UFormField: { template: '<div><slot /></div>' },
            UInput: { template: '<input />' },
            URadioGroup: { template: '<div />' },
            UAlert: { template: '<div />' },
            UButton: { template: '<button type="submit" />' }
          }
        }
      })

      // Act
      await wrapper.vm.onSubmit({
        data: { firstName: 'Bob', age: 50, topic: 'consolidation' }
      })
      await flushPromises()

      // Assert
      const callArgs = fetchMock.mock.calls[0][1]
      expect(callArgs.body).not.toHaveProperty('firstName')
    })

    it('should not send topic field in the payload', async () => {
      // Arrange
      const mockResponse = {
        id: 'consultation-123',
        customer_id: 'customer-456',
        advisor_name: 'AI Advisor',
        status: 'active',
        created_at: '2024-01-01T00:00:00Z'
      }
      fetchMock.mockResolvedValue(mockResponse)

      const wrapper = mount(CustomerProfileForm, {
        global: {
          stubs: {
            UCard: { template: '<div><slot /></div>' },
            UForm: { template: '<form @submit.prevent="$attrs.onSubmit"><slot /></form>' },
            UFormField: { template: '<div><slot /></div>' },
            UInput: { template: '<input />' },
            URadioGroup: { template: '<div />' },
            UAlert: { template: '<div />' },
            UButton: { template: '<button type="submit" />' }
          }
        }
      })

      // Act
      await wrapper.vm.onSubmit({
        data: { firstName: 'Bob', age: 50, topic: 'consolidation' }
      })
      await flushPromises()

      // Assert
      const callArgs = fetchMock.mock.calls[0][1]
      expect(callArgs.body).not.toHaveProperty('topic')
    })
  })

  describe('Response Handling', () => {
    it('should navigate to consultation page on successful response', async () => {
      // Arrange
      const mockResponse = {
        id: 'consultation-789',
        customer_id: 'customer-101',
        advisor_name: 'AI Advisor',
        status: 'active',
        created_at: '2024-01-01T00:00:00Z'
      }
      fetchMock.mockResolvedValue(mockResponse)

      const wrapper = mount(CustomerProfileForm, {
        global: {
          stubs: {
            UCard: { template: '<div><slot /></div>' },
            UForm: { template: '<form @submit.prevent="$attrs.onSubmit"><slot /></form>' },
            UFormField: { template: '<div><slot /></div>' },
            UInput: { template: '<input />' },
            URadioGroup: { template: '<div />' },
            UAlert: { template: '<div />' },
            UButton: { template: '<button type="submit" />' }
          }
        }
      })

      // Act
      await wrapper.vm.onSubmit({
        data: { firstName: 'Charlie', age: 45, topic: 'withdrawal' }
      })
      await flushPromises()

      // Assert
      expect(navigateToMock).toHaveBeenCalledTimes(1)
      expect(navigateToMock).toHaveBeenCalledWith('/consultation/consultation-789')
    })

    it('should use the id from response for navigation', async () => {
      // Arrange
      const mockResponse = {
        id: 'unique-consultation-id-999',
        customer_id: 'customer-999',
        advisor_name: 'AI Advisor',
        status: 'active',
        created_at: '2024-01-01T00:00:00Z'
      }
      fetchMock.mockResolvedValue(mockResponse)

      const wrapper = mount(CustomerProfileForm, {
        global: {
          stubs: {
            UCard: { template: '<div><slot /></div>' },
            UForm: { template: '<form @submit.prevent="$attrs.onSubmit"><slot /></form>' },
            UFormField: { template: '<div><slot /></div>' },
            UInput: { template: '<input />' },
            URadioGroup: { template: '<div />' },
            UAlert: { template: '<div />' },
            UButton: { template: '<button type="submit" />' }
          }
        }
      })

      // Act
      await wrapper.vm.onSubmit({
        data: { firstName: 'Diana', age: 55, topic: 'understanding' }
      })
      await flushPromises()

      // Assert
      expect(navigateToMock).toHaveBeenCalledWith('/consultation/unique-consultation-id-999')
    })

    it('should handle response with all expected ConsultationResponse fields', async () => {
      // Arrange
      const mockResponse = {
        id: 'consultation-555',
        customer_id: 'customer-555',
        advisor_name: 'Senior AI Advisor',
        status: 'active',
        created_at: '2024-01-15T10:30:00Z'
      }
      fetchMock.mockResolvedValue(mockResponse)

      const wrapper = mount(CustomerProfileForm, {
        global: {
          stubs: {
            UCard: { template: '<div><slot /></div>' },
            UForm: { template: '<form @submit.prevent="$attrs.onSubmit"><slot /></form>' },
            UFormField: { template: '<div><slot /></div>' },
            UInput: { template: '<input />' },
            URadioGroup: { template: '<div />' },
            UAlert: { template: '<div />' },
            UButton: { template: '<button type="submit" />' }
          }
        }
      })

      // Act
      await wrapper.vm.onSubmit({
        data: { firstName: 'Eve', age: 62, topic: 'tax' }
      })
      await flushPromises()

      // Assert - verify that all response fields are accessible
      expect(fetchMock).toHaveBeenCalled()
      expect(navigateToMock).toHaveBeenCalledWith('/consultation/consultation-555')
    })
  })

  describe('Error Handling', () => {
    it('should display error message when API call fails', async () => {
      // Arrange
      const errorMessage = 'Network connection failed'
      fetchMock.mockRejectedValue(new Error(errorMessage))

      const wrapper = mount(CustomerProfileForm, {
        global: {
          stubs: {
            UCard: { template: '<div><slot /></div>' },
            UForm: { template: '<form @submit.prevent="$attrs.onSubmit"><slot /></form>' },
            UFormField: { template: '<div><slot /></div>' },
            UInput: { template: '<input />' },
            URadioGroup: { template: '<div />' },
            UAlert: { template: '<div><slot /></div>' },
            UButton: { template: '<button type="submit" />' }
          }
        }
      })

      // Act
      await wrapper.vm.onSubmit({
        data: { firstName: 'Frank', age: 48, topic: 'consolidation' }
      })
      await flushPromises()

      // Assert
      const alertComponent = wrapper.findComponent({ name: 'UAlert' })
      expect(alertComponent.exists()).toBe(true)
    })

    it('should show user-friendly error message for API errors', async () => {
      // Arrange
      const apiError = {
        data: {
          message: 'Customer profile validation failed'
        }
      }
      fetchMock.mockRejectedValue(apiError)

      const wrapper = mount(CustomerProfileForm, {
        global: {
          stubs: {
            UCard: { template: '<div><slot /></div>' },
            UForm: { template: '<form @submit.prevent="$attrs.onSubmit"><slot /></form>' },
            UFormField: { template: '<div><slot /></div>' },
            UInput: { template: '<input />' },
            URadioGroup: { template: '<div />' },
            UAlert: {
              template: '<div class="alert" v-if="title">{{ title }}</div>',
              props: ['color', 'variant', 'title', 'closeButton']
            },
            UButton: { template: '<button type="submit" />' }
          }
        }
      })

      // Act
      await wrapper.vm.onSubmit({
        data: { firstName: 'Grace', age: 52, topic: 'withdrawal' }
      })
      await flushPromises()

      // Assert
      await wrapper.vm.$nextTick()
      const alertComponent = wrapper.findComponent({ name: 'UAlert' })
      expect(alertComponent.exists()).toBe(true)
      expect(alertComponent.props('title')).toBe('Customer profile validation failed')
    })

    it('should show fallback error message when error has no message', async () => {
      // Arrange
      fetchMock.mockRejectedValue({})

      const wrapper = mount(CustomerProfileForm, {
        global: {
          stubs: {
            UCard: { template: '<div><slot /></div>' },
            UForm: { template: '<form @submit.prevent="$attrs.onSubmit"><slot /></form>' },
            UFormField: { template: '<div><slot /></div>' },
            UInput: { template: '<input />' },
            URadioGroup: { template: '<div />' },
            UAlert: {
              template: '<div class="alert" v-if="title">{{ title }}</div>',
              props: ['color', 'variant', 'title', 'closeButton']
            },
            UButton: { template: '<button type="submit" />' }
          }
        }
      })

      // Act
      await wrapper.vm.onSubmit({
        data: { firstName: 'Henry', age: 58, topic: 'understanding' }
      })
      await flushPromises()

      // Assert
      await wrapper.vm.$nextTick()
      const alertComponent = wrapper.findComponent({ name: 'UAlert' })
      expect(alertComponent.props('title')).toBe('Failed to start consultation. Please try again.')
    })

    it('should not navigate when API call fails', async () => {
      // Arrange
      fetchMock.mockRejectedValue(new Error('Server error'))

      const wrapper = mount(CustomerProfileForm, {
        global: {
          stubs: {
            UCard: { template: '<div><slot /></div>' },
            UForm: { template: '<form @submit.prevent="$attrs.onSubmit"><slot /></form>' },
            UFormField: { template: '<div><slot /></div>' },
            UInput: { template: '<input />' },
            URadioGroup: { template: '<div />' },
            UAlert: { template: '<div />' },
            UButton: { template: '<button type="submit" />' }
          }
        }
      })

      // Act
      await wrapper.vm.onSubmit({
        data: { firstName: 'Iris', age: 42, topic: 'tax' }
      })
      await flushPromises()

      // Assert
      expect(navigateToMock).not.toHaveBeenCalled()
    })

    it('should handle 400 Bad Request errors', async () => {
      // Arrange
      const badRequestError = {
        data: {
          message: 'Invalid age value'
        },
        statusCode: 400
      }
      fetchMock.mockRejectedValue(badRequestError)

      const wrapper = mount(CustomerProfileForm, {
        global: {
          stubs: {
            UCard: { template: '<div><slot /></div>' },
            UForm: { template: '<form @submit.prevent="$attrs.onSubmit"><slot /></form>' },
            UFormField: { template: '<div><slot /></div>' },
            UInput: { template: '<input />' },
            URadioGroup: { template: '<div />' },
            UAlert: {
              template: '<div class="alert">{{ title }}</div>',
              props: ['color', 'variant', 'title', 'closeButton']
            },
            UButton: { template: '<button type="submit" />' }
          }
        }
      })

      // Act
      await wrapper.vm.onSubmit({
        data: { firstName: 'Jack', age: 17, topic: 'consolidation' }
      })
      await flushPromises()

      // Assert
      await wrapper.vm.$nextTick()
      const alertComponent = wrapper.findComponent({ name: 'UAlert' })
      expect(alertComponent.props('title')).toBe('Invalid age value')
    })

    it('should handle 500 Internal Server Error', async () => {
      // Arrange
      const serverError = {
        data: {
          message: 'Internal server error occurred'
        },
        statusCode: 500
      }
      fetchMock.mockRejectedValue(serverError)

      const wrapper = mount(CustomerProfileForm, {
        global: {
          stubs: {
            UCard: { template: '<div><slot /></div>' },
            UForm: { template: '<form @submit.prevent="$attrs.onSubmit"><slot /></form>' },
            UFormField: { template: '<div><slot /></div>' },
            UInput: { template: '<input />' },
            URadioGroup: { template: '<div />' },
            UAlert: {
              template: '<div class="alert">{{ title }}</div>',
              props: ['color', 'variant', 'title', 'closeButton']
            },
            UButton: { template: '<button type="submit" />' }
          }
        }
      })

      // Act
      await wrapper.vm.onSubmit({
        data: { firstName: 'Kate', age: 67, topic: 'withdrawal' }
      })
      await flushPromises()

      // Assert
      await wrapper.vm.$nextTick()
      const alertComponent = wrapper.findComponent({ name: 'UAlert' })
      expect(alertComponent.props('title')).toBe('Internal server error occurred')
    })
  })

  describe('Loading States', () => {
    it('should set loading state to true when submitting', async () => {
      // Arrange
      let resolvePromise: (value: any) => void
      const pendingPromise = new Promise((resolve) => {
        resolvePromise = resolve
      })
      fetchMock.mockReturnValue(pendingPromise)

      const wrapper = mount(CustomerProfileForm, {
        global: {
          stubs: {
            UCard: { template: '<div><slot /></div>' },
            UForm: { template: '<form @submit.prevent="$attrs.onSubmit"><slot /></form>' },
            UFormField: { template: '<div><slot /></div>' },
            UInput: { template: '<input />' },
            URadioGroup: { template: '<div />' },
            UAlert: { template: '<div />' },
            UButton: {
              template: '<button :disabled="loading"><slot /></button>',
              props: ['type', 'size', 'block', 'loading', 'disabled']
            }
          }
        }
      })

      // Act
      const submitPromise = wrapper.vm.onSubmit({
        data: { firstName: 'Laura', age: 53, topic: 'understanding' }
      })

      // Assert - check loading state during submission
      await wrapper.vm.$nextTick()
      const button = wrapper.findComponent({ name: 'UButton' })
      expect(button.props('loading')).toBe(true)
      expect(button.props('disabled')).toBe(true)

      // Cleanup
      resolvePromise!({
        id: 'test-123',
        customer_id: 'customer-123',
        advisor_name: 'AI Advisor',
        status: 'active',
        created_at: '2024-01-01T00:00:00Z'
      })
      await submitPromise
      await flushPromises()
    })

    it('should set loading state to false after successful submission', async () => {
      // Arrange
      const mockResponse = {
        id: 'consultation-444',
        customer_id: 'customer-444',
        advisor_name: 'AI Advisor',
        status: 'active',
        created_at: '2024-01-01T00:00:00Z'
      }
      fetchMock.mockResolvedValue(mockResponse)

      const wrapper = mount(CustomerProfileForm, {
        global: {
          stubs: {
            UCard: { template: '<div><slot /></div>' },
            UForm: { template: '<form @submit.prevent="$attrs.onSubmit"><slot /></form>' },
            UFormField: { template: '<div><slot /></div>' },
            UInput: { template: '<input />' },
            URadioGroup: { template: '<div />' },
            UAlert: { template: '<div />' },
            UButton: {
              template: '<button :disabled="loading"><slot /></button>',
              props: ['type', 'size', 'block', 'loading', 'disabled']
            }
          }
        }
      })

      // Act
      await wrapper.vm.onSubmit({
        data: { firstName: 'Mike', age: 59, topic: 'tax' }
      })
      await flushPromises()

      // Assert
      await wrapper.vm.$nextTick()
      const button = wrapper.findComponent({ name: 'UButton' })
      expect(button.props('loading')).toBe(false)
      expect(button.props('disabled')).toBe(false)
    })

    it('should set loading state to false after failed submission', async () => {
      // Arrange
      fetchMock.mockRejectedValue(new Error('Network error'))

      const wrapper = mount(CustomerProfileForm, {
        global: {
          stubs: {
            UCard: { template: '<div><slot /></div>' },
            UForm: { template: '<form @submit.prevent="$attrs.onSubmit"><slot /></form>' },
            UFormField: { template: '<div><slot /></div>' },
            UInput: { template: '<input />' },
            URadioGroup: { template: '<div />' },
            UAlert: { template: '<div />' },
            UButton: {
              template: '<button :disabled="loading"><slot /></button>',
              props: ['type', 'size', 'block', 'loading', 'disabled']
            }
          }
        }
      })

      // Act
      await wrapper.vm.onSubmit({
        data: { firstName: 'Nancy', age: 44, topic: 'other' }
      })
      await flushPromises()

      // Assert
      await wrapper.vm.$nextTick()
      const button = wrapper.findComponent({ name: 'UButton' })
      expect(button.props('loading')).toBe(false)
      expect(button.props('disabled')).toBe(false)
    })

    it('should disable submit button during loading', async () => {
      // Arrange
      let resolvePromise: (value: any) => void
      const pendingPromise = new Promise((resolve) => {
        resolvePromise = resolve
      })
      fetchMock.mockReturnValue(pendingPromise)

      const wrapper = mount(CustomerProfileForm, {
        global: {
          stubs: {
            UCard: { template: '<div><slot /></div>' },
            UForm: { template: '<form @submit.prevent="$attrs.onSubmit"><slot /></form>' },
            UFormField: { template: '<div><slot /></div>' },
            UInput: { template: '<input />' },
            URadioGroup: { template: '<div />' },
            UAlert: { template: '<div />' },
            UButton: {
              template: '<button :disabled="disabled"><slot /></button>',
              props: ['type', 'size', 'block', 'loading', 'disabled']
            }
          }
        }
      })

      // Act
      const submitPromise = wrapper.vm.onSubmit({
        data: { firstName: 'Oscar', age: 51, topic: 'consolidation' }
      })

      // Assert
      await wrapper.vm.$nextTick()
      const button = wrapper.findComponent({ name: 'UButton' })
      expect(button.props('disabled')).toBe(true)

      // Cleanup
      resolvePromise!({
        id: 'test-123',
        customer_id: 'customer-123',
        advisor_name: 'AI Advisor',
        status: 'active',
        created_at: '2024-01-01T00:00:00Z'
      })
      await submitPromise
      await flushPromises()
    })

    it('should clear error message before new submission', async () => {
      // Arrange
      fetchMock.mockRejectedValueOnce(new Error('First error'))

      const wrapper = mount(CustomerProfileForm, {
        global: {
          stubs: {
            UCard: { template: '<div><slot /></div>' },
            UForm: { template: '<form @submit.prevent="$attrs.onSubmit"><slot /></form>' },
            UFormField: { template: '<div><slot /></div>' },
            UInput: { template: '<input />' },
            URadioGroup: { template: '<div />' },
            UAlert: {
              template: '<div v-if="title" class="alert">{{ title }}</div>',
              props: ['color', 'variant', 'title', 'closeButton']
            },
            UButton: { template: '<button type="submit" />' }
          }
        }
      })

      // First submission with error
      await wrapper.vm.onSubmit({
        data: { firstName: 'Paul', age: 46, topic: 'withdrawal' }
      })
      await flushPromises()
      await wrapper.vm.$nextTick()

      // Verify error is shown
      let alertComponent = wrapper.findComponent({ name: 'UAlert' })
      expect(alertComponent.exists()).toBe(true)

      // Second submission (successful)
      const mockResponse = {
        id: 'consultation-777',
        customer_id: 'customer-777',
        advisor_name: 'AI Advisor',
        status: 'active',
        created_at: '2024-01-01T00:00:00Z'
      }
      fetchMock.mockResolvedValueOnce(mockResponse)

      // Act
      await wrapper.vm.onSubmit({
        data: { firstName: 'Paul', age: 46, topic: 'withdrawal' }
      })
      await flushPromises()
      await wrapper.vm.$nextTick()

      // Assert - error should be cleared
      alertComponent = wrapper.findComponent({ name: 'UAlert' })
      expect(alertComponent.props('title')).toBe('')
    })
  })

  describe('Form UI Tests (existing)', () => {
    it('renders the form header correctly', () => {
      const wrapper = mount(CustomerProfileForm, {
        global: {
          stubs: {
            UCard: {
              template: '<div><slot name="header" /><slot /></div>'
            },
            UForm: {
              template: '<form @submit="$attrs.onSubmit"><slot /></form>'
            },
            UFormField: {
              template: '<div><slot /></div>'
            },
            UInput: {
              template: '<input v-bind="$attrs" />'
            },
            URadioGroup: {
              template: '<div />'
            },
            UButton: {
              template: '<button type="submit"><slot /></button>'
            }
          }
        }
      })

      expect(wrapper.html()).toContain('Start Your Pension Guidance Consultation')
    })

    it('has all required form fields', () => {
      const wrapper = mount(CustomerProfileForm, {
        global: {
          stubs: {
            UCard: {
              template: '<div><slot name="header" /><slot /></div>'
            },
            UForm: {
              template: '<form><slot /></form>'
            },
            UFormField: {
              template: '<div><slot /></div>'
            },
            UInput: {
              template: '<input :name="$attrs.name" v-bind="$attrs" />'
            },
            URadioGroup: {
              template: '<div />'
            },
            UButton: {
              template: '<button />'
            }
          }
        }
      })

      expect(wrapper.find('input[name="firstName"]').exists()).toBe(true)
      expect(wrapper.find('input[name="age"]').exists()).toBe(true)
    })

    it('initializes form with empty values', () => {
      const wrapper = mount(CustomerProfileForm, {
        global: {
          stubs: {
            UCard: {
              template: '<div><slot /></div>'
            },
            UForm: {
              template: '<form><slot /></form>'
            },
            UFormField: {
              template: '<div><slot /></div>'
            },
            UInput: {
              template: '<input />'
            },
            URadioGroup: {
              template: '<div />'
            },
            UButton: {
              template: '<button />'
            }
          }
        }
      })

      expect(wrapper.vm.form.firstName).toBe('')
      expect(wrapper.vm.form.age).toBeUndefined()
      expect(wrapper.vm.form.topic).toBe('')
    })

    it('has topic options for radio group', () => {
      const wrapper = mount(CustomerProfileForm, {
        global: {
          stubs: {
            UCard: {
              template: '<div><slot /></div>'
            },
            UForm: {
              template: '<form><slot /></form>'
            },
            UFormField: {
              template: '<div><slot /></div>'
            },
            UInput: {
              template: '<input />'
            },
            URadioGroup: {
              template: '<div />'
            },
            UButton: {
              template: '<button />'
            }
          }
        }
      })

      expect(wrapper.vm.topicOptions).toBeDefined()
      expect(wrapper.vm.topicOptions.length).toBeGreaterThan(0)
      expect(wrapper.vm.topicOptions[0]).toHaveProperty('value')
      expect(wrapper.vm.topicOptions[0]).toHaveProperty('label')
    })
  })
})

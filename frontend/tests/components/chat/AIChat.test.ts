import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref } from 'vue'
import AIChat from '~/components/chat/AIChat.vue'

// Mock @ai-sdk/vue
vi.mock('@ai-sdk/vue', () => ({
  Chat: vi.fn().mockImplementation(() => ({
    messages: []
  }))
}))

// Mock marked
vi.mock('marked', () => ({
  marked: {
    parse: vi.fn((text: string) => text)
  }
}))

describe('AIChat Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders message input', () => {
    const wrapper = mount(AIChat, {
      props: {
        consultationId: 'test-id'
      },
      global: {
        stubs: {
          UTextarea: {
            template: '<textarea v-bind="$attrs" />'
          },
          UButton: {
            template: '<button type="submit"><slot /></button>'
          }
        }
      }
    })

    expect(wrapper.find('textarea').exists()).toBe(true)
  })

  it('has submit button', () => {
    const wrapper = mount(AIChat, {
      props: {
        consultationId: 'test-id'
      },
      global: {
        stubs: {
          UTextarea: {
            template: '<textarea />'
          },
          UButton: {
            template: '<button type="submit">Send</button>'
          }
        }
      }
    })

    const submitButton = wrapper.find('button[type="submit"]')
    expect(submitButton.exists()).toBe(true)
    expect(submitButton.text()).toContain('Send')
  })

  it('renders messages container', () => {
    const wrapper = mount(AIChat, {
      props: {
        consultationId: 'test-id'
      },
      global: {
        stubs: {
          UTextarea: {
            template: '<textarea />'
          },
          UButton: {
            template: '<button />'
          }
        }
      }
    })

    expect(wrapper.find('[class*="flex-1"]').exists()).toBe(true)
  })

  it('displays messages when available', async () => {
    const wrapper = mount(AIChat, {
      props: {
        consultationId: 'test-id'
      },
      global: {
        stubs: {
          UTextarea: {
            template: '<textarea />'
          },
          UButton: {
            template: '<button />'
          },
          UIcon: {
            template: '<span />'
          }
        }
      }
    })

    // Access component instance and push messages to the array
    // wrapper.vm.messages is a Ref<UIMessage[]>, we modify the array inside
    wrapper.vm.messages.push(
      { id: '1', role: 'user', parts: [{ type: 'text', text: 'Hello' }] },
      { id: '2', role: 'assistant', parts: [{ type: 'text', text: 'Hi there!' }] }
    )

    await wrapper.vm.$nextTick()

    expect(wrapper.html()).toContain('Hello')
    expect(wrapper.html()).toContain('Hi there!')
  })

  it('shows loading indicator when loading', async () => {
    const wrapper = mount(AIChat, {
      props: {
        consultationId: 'test-id'
      },
      global: {
        stubs: {
          UTextarea: {
            template: '<textarea />'
          },
          UButton: {
            template: '<button />'
          }
        }
      }
    })

    // Access component instance and manually set loading state
    // wrapper.vm.isLoading is already a ref, we need to check if it's unwrapped by defineExpose
    // In Vue 3 with composition API, exposed refs are auto-unwrapped
    wrapper.vm.isLoading = true

    await wrapper.vm.$nextTick()

    expect(wrapper.html()).toContain('animate-bounce')
  })

  it('receives consultationId prop', () => {
    const wrapper = mount(AIChat, {
      props: {
        consultationId: 'test-consultation-123'
      },
      global: {
        stubs: {
          UTextarea: {
            template: '<textarea />'
          },
          UButton: {
            template: '<button />'
          }
        }
      }
    })

    expect(wrapper.props('consultationId')).toBe('test-consultation-123')
  })
})

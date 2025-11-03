import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ConsultationPage from '~/pages/consultation/[id].vue'

// Mock useRoute
const mockRoute = {
  params: { id: 'test-consultation-id' }
}

vi.mock('vue-router', () => ({
  useRoute: () => mockRoute
}))

describe('Consultation Chat Page', () => {
  it('renders chat interface', () => {
    const wrapper = mount(ConsultationPage, {
      global: {
        stubs: {
          NuxtLink: {
            template: '<a><slot /></a>'
          },
          UIcon: {
            template: '<span />'
          },
          UButton: {
            template: '<button />'
          },
          UDropdown: {
            template: '<div><slot /></div>'
          },
          UAvatar: {
            template: '<div />'
          },
          UBadge: {
            template: '<span><slot /></span>'
          },
          ChatAIChat: {
            template: '<div data-testid="chat-container" />'
          }
        },
        mocks: {
          $route: mockRoute
        }
      }
    })

    expect(wrapper.find('[data-testid="chat-container"]').exists()).toBe(true)
  })

  it('renders header with back button', () => {
    const wrapper = mount(ConsultationPage, {
      global: {
        stubs: {
          NuxtLink: {
            template: '<a :to="$attrs.to"><slot /></a>',
            props: ['to']
          },
          UIcon: {
            template: '<span />'
          },
          UButton: {
            template: '<button />'
          },
          UDropdown: {
            template: '<div />'
          },
          UAvatar: {
            template: '<div />'
          },
          UBadge: {
            template: '<span />'
          },
          ChatAIChat: {
            template: '<div />'
          }
        },
        mocks: {
          $route: mockRoute
        }
      }
    })

    expect(wrapper.html()).toContain('Back to Home')
  })

  it('renders advisor information', () => {
    const wrapper = mount(ConsultationPage, {
      global: {
        stubs: {
          NuxtLink: {
            template: '<a><slot /></a>'
          },
          UIcon: {
            template: '<span />'
          },
          UButton: {
            template: '<button />'
          },
          UDropdown: {
            template: '<div />'
          },
          UAvatar: {
            template: '<div />'
          },
          UBadge: {
            template: '<span><slot /></span>'
          },
          ChatAIChat: {
            template: '<div />'
          }
        },
        mocks: {
          $route: mockRoute
        }
      }
    })

    expect(wrapper.html()).toContain('Sarah')
    expect(wrapper.html()).toContain('Pension Guidance Specialist')
  })

  it('renders active status badge', () => {
    const wrapper = mount(ConsultationPage, {
      global: {
        stubs: {
          NuxtLink: {
            template: '<a><slot /></a>'
          },
          UIcon: {
            template: '<span />'
          },
          UButton: {
            template: '<button />'
          },
          UDropdown: {
            template: '<div />'
          },
          UAvatar: {
            template: '<div />'
          },
          UBadge: {
            template: '<span><slot /></span>'
          },
          ChatAIChat: {
            template: '<div />'
          }
        },
        mocks: {
          $route: mockRoute
        }
      }
    })

    expect(wrapper.html()).toContain('Active')
  })

  it('renders consultation title', () => {
    const wrapper = mount(ConsultationPage, {
      global: {
        stubs: {
          NuxtLink: {
            template: '<a><slot /></a>'
          },
          UIcon: {
            template: '<span />'
          },
          UButton: {
            template: '<button />'
          },
          UDropdown: {
            template: '<div />'
          },
          UAvatar: {
            template: '<div />'
          },
          UBadge: {
            template: '<span />'
          },
          ChatAIChat: {
            template: '<div />'
          }
        },
        mocks: {
          $route: mockRoute
        }
      }
    })

    expect(wrapper.html()).toContain('Consultation with Sarah')
  })

  it('has menu dropdown', () => {
    const wrapper = mount(ConsultationPage, {
      global: {
        stubs: {
          NuxtLink: {
            template: '<a><slot /></a>'
          },
          UIcon: {
            template: '<span />'
          },
          UButton: {
            template: '<button />'
          },
          UDropdown: {
            name: 'UDropdown',
            template: '<div><slot /></div>'
          },
          UAvatar: {
            template: '<div />'
          },
          UBadge: {
            template: '<span />'
          },
          ChatAIChat: {
            template: '<div />'
          }
        },
        mocks: {
          $route: mockRoute
        }
      }
    })

    expect(wrapper.html()).toContain('ellipsis-vertical')
  })
})

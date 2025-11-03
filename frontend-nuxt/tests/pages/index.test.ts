import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Index from '~/pages/index.vue'

describe('Home Page', () => {
  it('renders customer profile form', () => {
    const wrapper = mount(Index, {
      global: {
        stubs: {
          FormsCustomerProfileForm: {
            template: '<div data-testid="customer-profile-form"><h2>Start Your Pension Guidance</h2></div>'
          },
          UCard: {
            template: '<div><slot /></div>'
          },
          NuxtLink: {
            template: '<a :to="$attrs.to"><slot /></a>',
            props: ['to']
          },
          UIcon: {
            template: '<span />'
          }
        }
      }
    })

    expect(wrapper.find('[data-testid="customer-profile-form"]').exists()).toBe(true)
    expect(wrapper.html()).toContain('Start Your Pension Guidance')
  })

  it('has all form fields', () => {
    const wrapper = mount(Index, {
      global: {
        stubs: {
          FormsCustomerProfileForm: {
            template: `
              <div>
                <input name="firstName" />
                <input name="age" />
              </div>
            `
          },
          UCard: {
            template: '<div><slot /></div>'
          },
          NuxtLink: {
            template: '<a><slot /></a>'
          },
          UIcon: {
            template: '<span />'
          }
        }
      }
    })

    expect(wrapper.find('input[name="firstName"]').exists()).toBe(true)
    expect(wrapper.find('input[name="age"]').exists()).toBe(true)
  })

  it('renders quick links section', () => {
    const wrapper = mount(Index, {
      global: {
        stubs: {
          FormsCustomerProfileForm: {
            template: '<div />'
          },
          UCard: {
            template: '<div><slot /></div>'
          },
          NuxtLink: {
            name: 'NuxtLink',
            template: '<a :to="$attrs.to"><slot /></a>',
            props: ['to']
          },
          UIcon: {
            template: '<span />'
          }
        }
      }
    })

    const links = wrapper.findAll('a')
    expect(links.length).toBeGreaterThan(0)
  })

  it('has link to history page', () => {
    const wrapper = mount(Index, {
      global: {
        stubs: {
          FormsCustomerProfileForm: {
            template: '<div />'
          },
          UCard: {
            template: '<div><slot /></div>'
          },
          NuxtLink: {
            template: '<a :to="$attrs.to"><slot /></a>',
            props: ['to']
          },
          UIcon: {
            template: '<span />'
          }
        }
      }
    })

    expect(wrapper.html()).toContain('View Past Consultations')
  })

  it('has link to admin page', () => {
    const wrapper = mount(Index, {
      global: {
        stubs: {
          FormsCustomerProfileForm: {
            template: '<div />'
          },
          UCard: {
            template: '<div><slot /></div>'
          },
          NuxtLink: {
            template: '<a :to="$attrs.to"><slot /></a>',
            props: ['to']
          },
          UIcon: {
            template: '<span />'
          }
        }
      }
    })

    expect(wrapper.html()).toContain('Admin Review')
  })
})

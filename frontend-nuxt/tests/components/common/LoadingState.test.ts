import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import LoadingState from '~/components/common/LoadingState.vue'

describe('LoadingState', () => {
  it('renders spinner variant by default', () => {
    const wrapper = mount(LoadingState)
    expect(wrapper.find('[data-testid="spinner"]').exists()).toBe(true)
  })

  it('renders spinner variant with message', () => {
    const wrapper = mount(LoadingState, {
      props: {
        variant: 'spinner',
        message: 'Loading data...'
      }
    })
    expect(wrapper.find('[data-testid="spinner"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Loading data...')
  })

  it('renders skeleton variant', () => {
    const wrapper = mount(LoadingState, {
      props: { variant: 'skeleton' }
    })
    expect(wrapper.find('[data-testid="skeleton"]').exists()).toBe(true)
  })

  it('renders overlay variant', () => {
    const wrapper = mount(LoadingState, {
      props: { variant: 'overlay' }
    })
    expect(wrapper.find('[data-testid="overlay"]').exists()).toBe(true)
  })

  it('overlay variant has fixed positioning', () => {
    const wrapper = mount(LoadingState, {
      props: { variant: 'overlay' }
    })
    const overlay = wrapper.find('[data-testid="overlay"]')
    expect(overlay.classes()).toContain('fixed')
  })
})

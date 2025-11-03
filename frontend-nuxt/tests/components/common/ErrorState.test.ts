import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ErrorState from '~/components/common/ErrorState.vue'

describe('ErrorState', () => {
  it('renders default error message', () => {
    const wrapper = mount(ErrorState)
    expect(wrapper.text()).toContain('Something went wrong')
  })

  it('renders custom error message', () => {
    const wrapper = mount(ErrorState, {
      props: { message: 'Custom error occurred' }
    })
    expect(wrapper.text()).toContain('Custom error occurred')
  })

  it('renders custom title', () => {
    const wrapper = mount(ErrorState, {
      props: { title: 'Custom Error Title' }
    })
    expect(wrapper.text()).toContain('Custom Error Title')
  })

  it('emits retry event when button clicked', async () => {
    const wrapper = mount(ErrorState)
    const button = wrapper.findAll('button')[0]
    await button.trigger('click')
    expect(wrapper.emitted('retry')).toBeTruthy()
    expect(wrapper.emitted('retry')).toHaveLength(1)
  })

  it('shows home button when showHome is true', () => {
    const wrapper = mount(ErrorState, {
      props: { showHome: true }
    })
    const buttons = wrapper.findAll('button')
    expect(buttons.length).toBeGreaterThan(1)
    expect(wrapper.text()).toContain('Go Home')
  })

  it('hides home button by default', () => {
    const wrapper = mount(ErrorState)
    expect(wrapper.text()).not.toContain('Go Home')
  })
})

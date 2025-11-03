import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DefaultLayout from '~/layouts/default.vue'

describe('Default Layout', () => {
  it('renders header with navigation', () => {
    const wrapper = mount(DefaultLayout)
    expect(wrapper.find('header').exists()).toBe(true)
    expect(wrapper.text()).toContain('Pension Guidance Service')
  })

  it('renders main slot area', () => {
    const wrapper = mount(DefaultLayout, {
      slots: {
        default: '<div class="test-content">Test Content</div>'
      }
    })
    expect(wrapper.find('main').exists()).toBe(true)
    expect(wrapper.html()).toContain('test-content')
  })

  it('renders footer with security message', () => {
    const wrapper = mount(DefaultLayout)
    expect(wrapper.find('footer').exists()).toBe(true)
    expect(wrapper.text()).toContain('confidential and secure')
  })

  it('has sticky header', () => {
    const wrapper = mount(DefaultLayout)
    const header = wrapper.find('header')
    expect(header.classes()).toContain('sticky')
  })
})

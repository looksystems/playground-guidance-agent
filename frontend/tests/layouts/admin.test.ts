import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import AdminLayout from '~/layouts/admin.vue'

describe('Admin Layout', () => {
  it('renders sidebar navigation', () => {
    const wrapper = mount(AdminLayout)
    expect(wrapper.find('aside').exists()).toBe(true)
  })

  it('renders navigation buttons', () => {
    const wrapper = mount(AdminLayout)
    const nav = wrapper.find('nav')
    expect(nav.exists()).toBe(true)
  })

  it('renders main content area', () => {
    const wrapper = mount(AdminLayout)
    expect(wrapper.find('main').exists()).toBe(true)
  })

  it('renders admin title', () => {
    const wrapper = mount(AdminLayout)
    expect(wrapper.text()).toContain('Admin')
  })
})

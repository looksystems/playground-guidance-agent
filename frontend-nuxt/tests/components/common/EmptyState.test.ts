import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import EmptyState from '~/components/common/EmptyState.vue'

describe('EmptyState', () => {
  it('renders default empty message', () => {
    const wrapper = mount(EmptyState)
    expect(wrapper.text()).toContain('Nothing here yet')
  })

  it('renders custom message', () => {
    const wrapper = mount(EmptyState, {
      props: { message: 'No items found' }
    })
    expect(wrapper.text()).toContain('No items found')
  })

  it('renders custom title', () => {
    const wrapper = mount(EmptyState, {
      props: { title: 'Empty List' }
    })
    expect(wrapper.text()).toContain('Empty List')
  })

  it('renders action button when actionLabel provided', () => {
    const wrapper = mount(EmptyState, {
      props: {
        actionLabel: 'Create New',
        actionTo: '/new'
      }
    })
    expect(wrapper.text()).toContain('Create New')
    const button = wrapper.find('button')
    expect(button.exists()).toBe(true)
  })

  it('does not render action button when no actionLabel', () => {
    const wrapper = mount(EmptyState)
    const button = wrapper.find('button')
    expect(button.exists()).toBe(false)
  })

  it('uses custom icon when provided', () => {
    const wrapper = mount(EmptyState, {
      props: { icon: 'i-heroicons-folder' }
    })
    // Icon should be rendered with custom class
    expect(wrapper.html()).toContain('i-heroicons-folder')
  })
})

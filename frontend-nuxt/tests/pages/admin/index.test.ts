import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import AdminDashboard from '~/pages/admin/index.vue'

describe('Admin Dashboard', () => {
  it('renders metric cards', () => {
    const wrapper = mount(AdminDashboard)
    const metricCards = wrapper.findAll('[data-testid="metric-card"]')
    expect(metricCards.length).toBeGreaterThan(0)
  })

  it('renders key metrics section', () => {
    const wrapper = mount(AdminDashboard)
    expect(wrapper.text()).toContain('Total Consultations')
    expect(wrapper.text()).toContain('FCA Compliance')
    expect(wrapper.text()).toContain('Satisfaction')
  })

  it('renders consultations table', () => {
    const wrapper = mount(AdminDashboard)
    expect(wrapper.text()).toContain('Recent Consultations')
  })

  it('renders compliance chart section', () => {
    const wrapper = mount(AdminDashboard)
    expect(wrapper.text()).toContain('Compliance Over Time')
  })
})

import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useConsultationsStore } from '~/stores/consultations'

describe('Consultations Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('initializes with empty state', () => {
    const store = useConsultationsStore()
    expect(store.consultations).toEqual([])
    expect(store.activeConsultation).toBeNull()
  })

  it('adds consultation to store', () => {
    const store = useConsultationsStore()
    const consultation = {
      id: '1',
      customerId: 'c1',
      customer: 'John Doe',
      topic: 'Retirement',
      status: 'active' as const,
      messages: 5,
      compliance: 95,
      satisfaction: 4,
      satisfactionEmoji: '😊',
      satisfactionText: 'Good',
      date: '2024-01-01',
      advisor: 'AI Assistant',
      preview: 'Discussion about retirement planning'
    }

    store.addConsultation(consultation)
    expect(store.consultations).toHaveLength(1)
    expect(store.consultations[0].id).toBe('1')
  })

  it('sets active consultation', () => {
    const store = useConsultationsStore()
    const consultation = {
      id: '1',
      customerId: 'c1',
      customer: 'John Doe',
      topic: 'Retirement',
      status: 'active' as const,
      messages: 5,
      compliance: 95,
      satisfaction: 4,
      satisfactionEmoji: '😊',
      satisfactionText: 'Good',
      date: '2024-01-01',
      advisor: 'AI Assistant',
      preview: 'Discussion about retirement planning'
    }

    store.setActiveConsultation(consultation)
    expect(store.activeConsultation).toBeDefined()
    expect(store.activeConsultation?.id).toBe('1')
  })

  it('updates existing consultation', () => {
    const store = useConsultationsStore()
    const consultation = {
      id: '1',
      customerId: 'c1',
      customer: 'John Doe',
      topic: 'Retirement',
      status: 'active' as const,
      messages: 5,
      compliance: 95,
      satisfaction: 4,
      satisfactionEmoji: '😊',
      satisfactionText: 'Good',
      date: '2024-01-01',
      advisor: 'AI Assistant',
      preview: 'Discussion about retirement planning'
    }

    store.addConsultation(consultation)
    store.updateConsultation('1', { status: 'completed', messages: 10 })

    expect(store.consultations[0].status).toBe('completed')
    expect(store.consultations[0].messages).toBe(10)
  })

  it('does not update non-existent consultation', () => {
    const store = useConsultationsStore()
    const consultation = {
      id: '1',
      customerId: 'c1',
      customer: 'John Doe',
      topic: 'Retirement',
      status: 'active' as const,
      messages: 5,
      compliance: 95,
      satisfaction: 4,
      satisfactionEmoji: '😊',
      satisfactionText: 'Good',
      date: '2024-01-01',
      advisor: 'AI Assistant',
      preview: 'Discussion about retirement planning'
    }

    store.addConsultation(consultation)
    store.updateConsultation('999', { status: 'completed' })

    expect(store.consultations[0].status).toBe('active')
  })

  it('handles multiple consultations', () => {
    const store = useConsultationsStore()

    const consultation1 = {
      id: '1',
      customerId: 'c1',
      customer: 'John Doe',
      topic: 'Retirement',
      status: 'active' as const,
      messages: 5,
      compliance: 95,
      satisfaction: 4,
      satisfactionEmoji: '😊',
      satisfactionText: 'Good',
      date: '2024-01-01',
      advisor: 'AI Assistant',
      preview: 'Discussion about retirement planning'
    }

    const consultation2 = {
      id: '2',
      customerId: 'c2',
      customer: 'Jane Smith',
      topic: 'Investment',
      status: 'completed' as const,
      messages: 8,
      compliance: 98,
      satisfaction: 5,
      satisfactionEmoji: '😍',
      satisfactionText: 'Excellent',
      date: '2024-01-02',
      advisor: 'AI Assistant',
      preview: 'Investment portfolio review'
    }

    store.addConsultation(consultation1)
    store.addConsultation(consultation2)

    expect(store.consultations).toHaveLength(2)
    expect(store.consultations[0].id).toBe('1')
    expect(store.consultations[1].id).toBe('2')
  })

  it('clears active consultation', () => {
    const store = useConsultationsStore()
    const consultation = {
      id: '1',
      customerId: 'c1',
      customer: 'John Doe',
      topic: 'Retirement',
      status: 'active' as const,
      messages: 5,
      compliance: 95,
      satisfaction: 4,
      satisfactionEmoji: '😊',
      satisfactionText: 'Good',
      date: '2024-01-01',
      advisor: 'AI Assistant',
      preview: 'Discussion about retirement planning'
    }

    store.setActiveConsultation(consultation)
    expect(store.activeConsultation).toBeDefined()

    store.setActiveConsultation(null)
    expect(store.activeConsultation).toBeNull()
  })
})

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'
import { useConsultation } from '~/composables/useConsultation'

describe('useConsultation', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('fetches consultation list', async () => {
    vi.mocked(useFetch).mockResolvedValue({
      data: ref({
        items: [
          { id: '1', customerId: 'c1', status: 'active' },
          { id: '2', customerId: 'c2', status: 'completed' }
        ],
        total: 2,
        page: 1,
        limit: 10,
        pages: 1
      }),
      error: ref(null),
      pending: ref(false),
      refresh: vi.fn(),
      execute: vi.fn(),
      status: ref('success')
    } as any)

    const { listConsultations } = useConsultation()
    const result = await listConsultations({ page: 1, limit: 10 })

    expect(result).toBeDefined()
    expect(result.items).toHaveLength(2)
    expect(result.total).toBe(2)
  })

  it('fetches single consultation by id', async () => {
    vi.mocked(useFetch).mockResolvedValue({
      data: ref({
        id: '1',
        customerId: 'c1',
        customerName: 'John Doe',
        status: 'active',
        createdAt: '2024-01-01',
        messages: []
      }),
      error: ref(null),
      pending: ref(false),
      refresh: vi.fn(),
      execute: vi.fn(),
      status: ref('success')
    } as any)

    const { getConsultation } = useConsultation()
    const result = await getConsultation('1')

    expect(result).toBeDefined()
    expect(result.id).toBe('1')
    expect(result.customerName).toBe('John Doe')
  })

  it('creates new consultation', async () => {
    vi.mocked(useFetch).mockResolvedValue({
      data: ref({
        id: 'new-1',
        customerId: 'c1',
        status: 'active',
        createdAt: '2024-01-01'
      }),
      error: ref(null),
      pending: ref(false),
      refresh: vi.fn(),
      execute: vi.fn(),
      status: ref('success')
    } as any)

    const { createConsultation } = useConsultation()
    const result = await createConsultation({
      id: 'c1',
      firstName: 'John',
      lastName: 'Doe',
      age: 55,
      createdAt: '2024-01-01'
    })

    expect(result).toBeDefined()
    expect(result.id).toBe('new-1')
    expect(result.status).toBe('active')
  })

  it('ends consultation', async () => {
    vi.mocked(useFetch).mockResolvedValue({
      data: ref({
        id: '1',
        customerId: 'c1',
        customerName: 'John Doe',
        status: 'completed',
        createdAt: '2024-01-01',
        completedAt: '2024-01-02',
        messages: []
      }),
      error: ref(null),
      pending: ref(false),
      refresh: vi.fn(),
      execute: vi.fn(),
      status: ref('success')
    } as any)

    const { endConsultation } = useConsultation()
    const result = await endConsultation('1', 5)

    expect(result).toBeDefined()
    expect(result.status).toBe('completed')
    expect(result.completedAt).toBeDefined()
  })

  it('fetches consultation metrics', async () => {
    vi.mocked(useFetch).mockResolvedValue({
      data: ref({
        complianceScore: 95,
        responseCount: 10,
        averageResponseTime: 2.5,
        topicsCovered: ['retirement', 'savings']
      }),
      error: ref(null),
      pending: ref(false),
      refresh: vi.fn(),
      execute: vi.fn(),
      status: ref('success')
    } as any)

    const { getMetrics } = useConsultation()
    const result = await getMetrics('1')

    expect(result).toBeDefined()
    expect(result.complianceScore).toBe(95)
    expect(result.topicsCovered).toHaveLength(2)
  })

  it('handles errors when fetching consultations', async () => {
    vi.mocked(useFetch).mockResolvedValue({
      data: ref(null),
      error: ref(new Error('Network error')),
      pending: ref(false),
      refresh: vi.fn(),
      execute: vi.fn(),
      status: ref('error')
    } as any)

    const { listConsultations } = useConsultation()

    await expect(listConsultations({ page: 1, limit: 10 })).rejects.toThrow('Failed to fetch consultations')
  })

  it('filters consultations by status', async () => {
    vi.mocked(useFetch).mockResolvedValue({
      data: ref({
        items: [{ id: '1', status: 'active' }],
        total: 1,
        page: 1,
        limit: 10,
        pages: 1
      }),
      error: ref(null),
      pending: ref(false),
      refresh: vi.fn(),
      execute: vi.fn(),
      status: ref('success')
    } as any)

    const { listConsultations } = useConsultation()
    const result = await listConsultations({
      page: 1,
      limit: 10,
      status: 'active'
    })

    expect(result.items).toHaveLength(1)
    expect(result.items[0].status).toBe('active')
  })
})

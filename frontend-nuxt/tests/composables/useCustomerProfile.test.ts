import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'
import { useCustomerProfile } from '~/composables/useCustomerProfile'

describe('useCustomerProfile', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('gets customer profile by id', async () => {
    vi.mocked(useFetch).mockResolvedValue({
      data: ref({
        id: 'test-123',
        firstName: 'John',
        lastName: 'Doe',
        age: 55,
        email: 'john@example.com',
        createdAt: '2024-01-01'
      }),
      error: ref(null),
      pending: ref(false),
      refresh: vi.fn(),
      execute: vi.fn(),
      status: ref('success')
    } as any)

    const { getProfile } = useCustomerProfile()
    const result = await getProfile('test-123')

    expect(result).toBeDefined()
    expect(result.id).toBe('test-123')
    expect(result.firstName).toBe('John')
  })

  it('updates customer profile', async () => {
    vi.mocked(useFetch).mockResolvedValue({
      data: ref({
        id: 'test-123',
        firstName: 'John',
        lastName: 'Smith',
        age: 56,
        email: 'john@example.com',
        createdAt: '2024-01-01'
      }),
      error: ref(null),
      pending: ref(false),
      refresh: vi.fn(),
      execute: vi.fn(),
      status: ref('success')
    } as any)

    const { updateProfile } = useCustomerProfile()
    const result = await updateProfile('test-123', {
      lastName: 'Smith',
      age: 56
    })

    expect(result).toBeDefined()
    expect(result.lastName).toBe('Smith')
    expect(result.age).toBe(56)
  })

  it('handles errors when getting profile', async () => {
    vi.mocked(useFetch).mockResolvedValue({
      data: ref(null),
      error: ref(new Error('Failed to fetch')),
      pending: ref(false),
      refresh: vi.fn(),
      execute: vi.fn(),
      status: ref('error')
    } as any)

    const { getProfile } = useCustomerProfile()

    await expect(getProfile('test-123')).rejects.toThrow('Failed to get profile')
  })

  it('gets customer consultations', async () => {
    vi.mocked(useFetch).mockResolvedValue({
      data: ref({
        items: [
          { id: '1', status: 'active' },
          { id: '2', status: 'completed' }
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

    const { getConsultations } = useCustomerProfile()
    const result = await getConsultations('test-123', {
      page: 1,
      limit: 10
    })

    expect(result).toBeDefined()
    expect(result.items).toHaveLength(2)
    expect(result.total).toBe(2)
  })
})

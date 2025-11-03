// @ts-nocheck - Complex type checking issues with $fetch mock
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { api } from '~/utils/api'

// Mock $fetch
global.$fetch = vi.fn() as any

describe('API Utility', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('consultations', () => {
    it('has consultations methods', () => {
      expect(api.consultations).toBeDefined()
      expect(api.consultations.list).toBeTypeOf('function')
      expect(api.consultations.get).toBeTypeOf('function')
      expect(api.consultations.create).toBeTypeOf('function')
      expect(api.consultations.update).toBeTypeOf('function')
    })

    it('lists consultations', async () => {
      const mockData = {
        items: [{ id: '1' }, { id: '2' }],
        total: 2
      }

      vi.mocked($fetch).mockResolvedValue(mockData)

      const result = await api.consultations.list({ page: 1, limit: 10 })

      expect($fetch).toHaveBeenCalledWith('/api/consultations', {
        params: { page: 1, limit: 10 }
      })
      expect(result).toEqual(mockData)
    })

    it('gets single consultation', async () => {
      const mockData = { id: '1', status: 'active' }
      vi.mocked($fetch).mockResolvedValue(mockData)

      const result = await api.consultations.get('1')

      expect($fetch).toHaveBeenCalledWith('/api/consultations/1')
      expect(result).toEqual(mockData)
    })

    it('creates consultation', async () => {
      const mockData = { id: 'new-1', status: 'active' }
      const createData = { customerId: 'c1', topic: 'retirement' }

      vi.mocked($fetch).mockResolvedValue(mockData)

      const result = await api.consultations.create(createData)

      expect($fetch).toHaveBeenCalledWith('/api/consultations', {
        method: 'POST',
        body: createData
      })
      expect(result).toEqual(mockData)
    })

    it('updates consultation', async () => {
      const mockData = { id: '1', status: 'completed' }
      const updateData = { status: 'completed' }

      vi.mocked($fetch).mockResolvedValue(mockData)

      const result = await api.consultations.update('1', updateData)

      expect($fetch).toHaveBeenCalledWith('/api/consultations/1', {
        method: 'PATCH',
        body: updateData
      })
      expect(result).toEqual(mockData)
    })
  })

  describe('customers', () => {
    it('has createProfile method', () => {
      expect(api.customers).toBeDefined()
      expect(api.customers.createProfile).toBeTypeOf('function')
    })

    it('creates customer profile', async () => {
      const mockData = { id: 'c1', firstName: 'John' }
      const profileData = { firstName: 'John', age: 55, topic: 'retirement' }

      vi.mocked($fetch).mockResolvedValue(mockData)

      const result = await api.customers.createProfile(profileData)

      expect($fetch).toHaveBeenCalledWith('/api/customers/profile', {
        method: 'POST',
        body: profileData
      })
      expect(result).toEqual(mockData)
    })
  })

  describe('admin', () => {
    it('has admin methods', () => {
      expect(api.admin).toBeDefined()
      expect(api.admin.consultations).toBeTypeOf('function')
      expect(api.admin.consultation).toBeTypeOf('function')
      expect(api.admin.metrics).toBeTypeOf('function')
      expect(api.admin.complianceData).toBeTypeOf('function')
    })

    it('fetches admin consultations', async () => {
      const mockData = { items: [], total: 0 }
      vi.mocked($fetch).mockResolvedValue(mockData)

      const result = await api.admin.consultations({ page: 1 })

      expect($fetch).toHaveBeenCalledWith('/api/admin/consultations', {
        params: { page: 1 }
      })
      expect(result).toEqual(mockData)
    })

    it('fetches single admin consultation', async () => {
      const mockData = { id: '1', customerId: 'c1' }
      vi.mocked($fetch).mockResolvedValue(mockData)

      const result = await api.admin.consultation('1')

      expect($fetch).toHaveBeenCalledWith('/api/admin/consultations/1')
      expect(result).toEqual(mockData)
    })

    it('fetches admin metrics', async () => {
      const mockData = { totalConsultations: 100, avgCompliance: 95 }
      vi.mocked($fetch).mockResolvedValue(mockData)

      const result = await api.admin.metrics()

      expect($fetch).toHaveBeenCalledWith('/api/admin/metrics')
      expect(result).toEqual(mockData)
    })

    it('fetches compliance data', async () => {
      const mockData = { compliantCount: 90, totalCount: 100 }
      vi.mocked($fetch).mockResolvedValue(mockData)

      const result = await api.admin.complianceData()

      expect($fetch).toHaveBeenCalledWith('/api/admin/metrics/compliance')
      expect(result).toEqual(mockData)
    })
  })
})

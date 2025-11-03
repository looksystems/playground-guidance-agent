export const api = {
  consultations: {
    list: (params?: any) => $fetch('/api/consultations', { params }),
    get: (id: string) => $fetch(`/api/consultations/${id}`),
    create: (data: any) => $fetch('/api/consultations', {
      method: 'POST',
      body: data
    }),
    update: (id: string, data: any) => $fetch(`/api/consultations/${id}`, {
      method: 'PATCH',
      body: data
    })
  },

  customers: {
    createProfile: (data: any) => $fetch('/api/customers/profile', {
      method: 'POST',
      body: data
    }),
    getProfile: (id: string) => $fetch(`/api/customers/${id}`),
    updateProfile: (id: string, data: any) => $fetch(`/api/customers/${id}`, {
      method: 'PUT',
      body: data
    }),
    getConsultations: (id: string, params?: any) => $fetch(`/api/customers/${id}/consultations`, {
      params
    })
  },

  admin: {
    consultations: (params?: any) => $fetch('/api/admin/consultations', { params }),
    consultation: (id: string) => $fetch(`/api/admin/consultations/${id}`),
    metrics: () => $fetch('/api/admin/metrics'),
    complianceData: () => $fetch('/api/admin/metrics/compliance')
  }
}

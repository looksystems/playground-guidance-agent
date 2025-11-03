import type { CustomerProfile, UpdateProfileData } from '~/app/types/api'

export interface CustomerConsultationsParams {
  page: number
  limit: number
  status?: 'active' | 'completed'
}

export interface CustomerConsultations {
  items: any[]
  total: number
  page: number
  limit: number
  pages: number
}

export const useCustomerProfile = () => {
  const getProfile = async (customerId: string): Promise<CustomerProfile> => {
    const { data, error } = await useFetch(`/api/customers/${customerId}`)

    if (error.value) {
      throw new Error('Failed to get profile')
    }

    return data.value as CustomerProfile
  }

  const updateProfile = async (
    customerId: string,
    updates: UpdateProfileData
  ): Promise<CustomerProfile> => {
    const { data, error } = await useFetch(`/api/customers/${customerId}`, {
      method: 'PUT',
      body: updates
    })

    if (error.value) {
      throw new Error('Failed to update profile')
    }

    return data.value as CustomerProfile
  }

  const getConsultations = async (
    customerId: string,
    params: CustomerConsultationsParams
  ): Promise<CustomerConsultations> => {
    const { data, error } = await useFetch(
      `/api/customers/${customerId}/consultations`,
      {
        query: params
      }
    )

    if (error.value) {
      throw new Error('Failed to get consultations')
    }

    return data.value as CustomerConsultations
  }

  return {
    getProfile,
    updateProfile,
    getConsultations
  }
}

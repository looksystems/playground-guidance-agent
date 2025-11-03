import type {
  CustomerProfile,
  ConsultationDetail,
  ConsultationMetrics,
  ListConsultationsParams,
  PaginatedConsultations,
  CreateConsultationResponse
} from '~/app/types/api'

export const useConsultation = () => {
  const listConsultations = async (
    params: ListConsultationsParams
  ): Promise<PaginatedConsultations> => {
    const { data, error } = await useFetch('/api/consultations', {
      query: params
    })

    if (error.value) {
      throw new Error('Failed to fetch consultations')
    }

    return data.value as PaginatedConsultations
  }

  const getConsultation = async (consultationId: string): Promise<ConsultationDetail> => {
    const { data, error } = await useFetch(
      `/api/consultations/${consultationId}`
    )

    if (error.value) {
      throw new Error('Failed to fetch consultation')
    }

    return data.value as ConsultationDetail
  }

  const createConsultation = async (
    customerProfile: CustomerProfile
  ): Promise<CreateConsultationResponse> => {
    const { data, error } = await useFetch('/api/consultations', {
      method: 'POST',
      body: { customer_profile: customerProfile }
    })

    if (error.value) {
      throw new Error('Failed to create consultation')
    }

    return data.value as CreateConsultationResponse
  }

  const endConsultation = async (
    consultationId: string,
    satisfactionScore?: number
  ): Promise<ConsultationDetail> => {
    const { data, error } = await useFetch(
      `/api/consultations/${consultationId}/end`,
      {
        method: 'POST',
        body: { satisfaction_score: satisfactionScore }
      }
    )

    if (error.value) {
      throw new Error('Failed to end consultation')
    }

    return data.value as ConsultationDetail
  }

  const getMetrics = async (consultationId: string): Promise<ConsultationMetrics> => {
    const { data, error } = await useFetch(
      `/api/consultations/${consultationId}/metrics`
    )

    if (error.value) {
      throw new Error('Failed to fetch metrics')
    }

    return data.value as ConsultationMetrics
  }

  return {
    listConsultations,
    getConsultation,
    createConsultation,
    endConsultation,
    getMetrics
  }
}

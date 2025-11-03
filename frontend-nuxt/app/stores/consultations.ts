import type { Consultation } from '~/app/types/api'

export const useConsultationsStore = defineStore('consultations', () => {
  const consultations = ref<Consultation[]>([])
  const activeConsultation = ref<Consultation | null>(null)

  const addConsultation = (consultation: Consultation) => {
    consultations.value.push(consultation)
  }

  const setActiveConsultation = (consultation: Consultation | null) => {
    activeConsultation.value = consultation
  }

  const updateConsultation = (id: string, updates: Partial<Consultation>) => {
    const index = consultations.value.findIndex(c => c.id === id)
    if (index !== -1) {
      consultations.value[index] = { ...consultations.value[index], ...updates }
    }
  }

  const removeConsultation = (id: string) => {
    const index = consultations.value.findIndex(c => c.id === id)
    if (index !== -1) {
      consultations.value.splice(index, 1)
    }
  }

  const clearConsultations = () => {
    consultations.value = []
    activeConsultation.value = null
  }

  return {
    consultations,
    activeConsultation,
    addConsultation,
    setActiveConsultation,
    updateConsultation,
    removeConsultation,
    clearConsultations
  }
})

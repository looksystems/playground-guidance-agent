export interface CustomerProfile {
  id: string
  firstName: string
  lastName: string
  age: number
  email?: string
  phone?: string
  topic?: string
  createdAt: string
  updatedAt?: string
}

export interface UpdateProfileData {
  firstName?: string
  lastName?: string
  age?: number
  email?: string
  phone?: string
}

export interface Consultation {
  id: string
  customerId: string
  customer: string
  topic: string
  status: 'active' | 'completed'
  messages: number
  compliance: number
  satisfaction: number
  satisfactionEmoji: string
  satisfactionText: string
  date: string
  advisor: string
  preview: string
}

export interface ConsultationDetail {
  id: string
  customerId: string
  customerName: string
  status: 'active' | 'completed'
  createdAt: string
  completedAt?: string
  messages: Message[]
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  complianceScore?: number
}

export interface ConsultationMetrics {
  complianceScore: number
  responseCount: number
  averageResponseTime: number
  topicsCovered: string[]
}

export interface ListConsultationsParams {
  page?: number
  limit?: number
  status?: 'active' | 'completed'
  search?: string
  customerId?: string
}

export interface PaginatedConsultations {
  items: Consultation[]
  total: number
  page: number
  limit: number
  pages: number
}

export interface CreateConsultationResponse {
  id: string
  customerId: string
  status: 'active' | 'completed'
  createdAt: string
}

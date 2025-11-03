"""Pydantic schemas for API request/response validation.

These schemas define the structure of data flowing through the API endpoints.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal
from uuid import UUID
from datetime import datetime


# --- Request Schemas ---


class CreateConsultationRequest(BaseModel):
    """Request to create a new consultation."""

    name: str = Field(..., min_length=1, max_length=100, description="Customer name")
    age: int = Field(..., ge=18, le=68, description="Customer age (18-68)")
    initial_query: str = Field(
        ..., min_length=10, max_length=1000, description="Initial question or concern"
    )

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: int) -> int:
        """Validate age is appropriate for pension guidance."""
        if v < 18:
            raise ValueError("Must be at least 18 years old")
        if v > 68:
            raise ValueError("Must be 68 years old or younger")
        return v


class SendMessageRequest(BaseModel):
    """Request to send a customer message."""

    content: str = Field(..., min_length=1, max_length=2000, description="Message content")


class EndConsultationRequest(BaseModel):
    """Request to end a consultation (optional satisfaction feedback)."""

    customer_satisfaction: Optional[float] = Field(
        None, ge=0, le=10, description="Customer satisfaction rating (0-10)"
    )
    feedback: Optional[str] = Field(None, max_length=500, description="Optional feedback")


# --- Response Schemas ---


class ConsultationResponse(BaseModel):
    """Response for a consultation."""

    id: UUID
    customer_id: UUID
    advisor_name: str
    status: Literal["active", "completed"]
    created_at: datetime
    ended_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Response for a message."""

    message_id: UUID
    status: Literal["received", "processing", "completed"]
    timestamp: datetime


class ConversationTurn(BaseModel):
    """A single turn in the conversation."""

    role: Literal["customer", "advisor", "system"]
    content: str
    timestamp: datetime
    compliance_score: Optional[float] = None
    compliance_confidence: Optional[float] = None
    compliance_reasoning: Optional[str] = None
    compliance_issues: Optional[List[dict]] = None
    compliance_passed: Optional[bool] = None
    requires_human_review: Optional[bool] = None


class ConsultationDetailResponse(BaseModel):
    """Detailed consultation response with conversation."""

    id: UUID
    customer_id: UUID
    advisor_name: str
    status: Literal["active", "completed"]
    conversation: List[ConversationTurn]
    outcome: Optional[dict] = None
    created_at: datetime
    ended_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConsultationMetrics(BaseModel):
    """Metrics for a consultation."""

    message_count: int
    avg_compliance_score: float
    customer_satisfaction: Optional[float] = None
    comprehension: Optional[float] = None
    duration_minutes: Optional[float] = None


class PaginatedConsultations(BaseModel):
    """Paginated list of consultations."""

    items: List[ConsultationResponse]
    total: int
    skip: int
    limit: int


# --- Customer Schemas ---


class CustomerProfileResponse(BaseModel):
    """Customer profile response."""

    customer_id: UUID
    name: str
    age: int
    consultation_count: int
    first_consultation: datetime
    last_consultation: Optional[datetime] = None


class CustomerConsultationListResponse(BaseModel):
    """List of consultations for a customer."""

    consultations: List[ConsultationResponse]


# --- Admin Schemas ---


class AdminConsultationReview(BaseModel):
    """Detailed consultation for admin review."""

    id: UUID
    customer_id: UUID
    customer_name: str
    customer_age: int
    advisor_name: str
    conversation: List[ConversationTurn]
    outcome: Optional[dict]
    metrics: ConsultationMetrics
    created_at: datetime
    ended_at: Optional[datetime]


class ComplianceMetrics(BaseModel):
    """Overall compliance metrics."""

    total_consultations: int
    avg_compliance_score: float
    compliant_percentage: float
    avg_satisfaction: float
    period_start: datetime
    period_end: datetime


class TimeSeriesDataPoint(BaseModel):
    """Single data point in time series."""

    date: str
    avg_compliance: float
    consultation_count: int


class TimeSeriesMetrics(BaseModel):
    """Time series metrics response."""

    data_points: List[TimeSeriesDataPoint]


class AdminConsultationListResponse(BaseModel):
    """Admin list of consultations with filters."""

    items: List[AdminConsultationReview]
    total: int
    skip: int
    limit: int


# --- SSE Event Schemas ---


class SSEChunkEvent(BaseModel):
    """SSE chunk event during streaming."""

    type: Literal["chunk"] = "chunk"
    content: str


class SSECompleteEvent(BaseModel):
    """SSE completion event."""

    type: Literal["complete"] = "complete"
    compliance_score: float
    compliance_confidence: float
    full_message: str


class SSEErrorEvent(BaseModel):
    """SSE error event."""

    type: Literal["error"] = "error"
    error: str


# --- Admin Settings ---


class AdminSettingsResponse(BaseModel):
    """Admin settings response."""

    systemName: str = Field(..., min_length=1, max_length=255)
    supportEmail: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    sessionTimeout: int = Field(..., ge=1, le=1440, description="Session timeout in minutes")
    fcaComplianceEnabled: bool
    riskAssessmentRequired: bool
    autoArchive: bool
    emailNotifications: bool
    complianceAlerts: bool
    dailyDigest: bool
    aiModel: str = Field(..., min_length=1, max_length=100)
    temperature: float = Field(..., ge=0.0, le=2.0)
    maxTokens: int = Field(..., ge=1, le=100000)

    @field_validator("supportEmail")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v


class UpdateAdminSettingsRequest(BaseModel):
    """Request to update admin settings."""

    systemName: str = Field(..., min_length=1, max_length=255)
    supportEmail: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    sessionTimeout: int = Field(..., ge=1, le=1440, description="Session timeout in minutes")
    fcaComplianceEnabled: bool
    riskAssessmentRequired: bool
    autoArchive: bool
    emailNotifications: bool
    complianceAlerts: bool
    dailyDigest: bool
    aiModel: str = Field(..., min_length=1, max_length=100)
    temperature: float = Field(..., ge=0.0, le=2.0)
    maxTokens: int = Field(..., ge=1, le=100000)

    @field_validator("supportEmail")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v


# --- Customer Management Schemas ---


class AdminCustomerResponse(BaseModel):
    """Admin customer response with aggregated data."""

    customer_id: UUID
    total_consultations: int
    first_consultation: datetime
    last_consultation: datetime
    avg_compliance_score: float
    avg_satisfaction: Optional[float]
    topics: List[str]
    customer_profile: dict
    recent_consultations: Optional[List[ConsultationResponse]] = None  # Only in detail view


class CustomerStats(BaseModel):
    """Customer statistics for list view."""

    total_customers: int
    active_customers_30d: int
    avg_consultations_per_customer: float


class PaginatedCustomers(BaseModel):
    """Paginated list of customers with stats."""

    items: List[AdminCustomerResponse]
    total: int
    page: int
    page_size: int
    pages: int
    stats: CustomerStats


# --- Knowledge Base Schemas ---


class FCAKnowledgeResponse(BaseModel):
    """FCA Knowledge response."""

    id: UUID
    content: str
    source: Optional[str] = None
    category: str
    has_embedding: bool
    meta: dict
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedFCAKnowledge(BaseModel):
    """Paginated list of FCA Knowledge."""

    items: List[FCAKnowledgeResponse]
    total: int
    page: int
    page_size: int
    pages: int


class PensionKnowledgeResponse(BaseModel):
    """Pension Knowledge response."""

    id: UUID
    content: str
    category: str
    subcategory: Optional[str] = None
    has_embedding: bool
    meta: dict
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedPensionKnowledge(BaseModel):
    """Paginated list of Pension Knowledge."""

    items: List[PensionKnowledgeResponse]
    total: int
    page: int
    page_size: int
    pages: int


# --- Learning System Schemas ---


class MemoryResponse(BaseModel):
    """Memory response schema."""

    id: UUID
    description: str
    timestamp: datetime
    last_accessed: datetime
    importance: float  # 0.0-1.0
    memory_type: Literal["observation", "reflection", "plan"]
    has_embedding: bool
    meta: dict
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedMemories(BaseModel):
    """Paginated memories response."""

    items: List[MemoryResponse]
    total: int
    page: int
    page_size: int
    pages: int
    type_counts: dict = Field(default_factory=dict, description="Count of each memory type")


class CaseResponse(BaseModel):
    """Case response schema."""

    id: UUID
    task_type: str
    customer_situation: str
    guidance_provided: str
    outcome: dict
    has_embedding: bool
    meta: dict
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedCases(BaseModel):
    """Paginated cases response."""

    items: List[CaseResponse]
    total: int
    page: int
    page_size: int
    pages: int
    task_types_count: int = Field(default=0, description="Count of distinct task types")
    with_outcomes_count: int = Field(default=0, description="Count of cases with outcomes")


class RuleResponse(BaseModel):
    """Rule response schema."""

    id: UUID
    principle: str
    domain: str
    confidence: float  # 0.0-1.0
    supporting_evidence: list
    evidence_count: int  # Length of supporting_evidence
    has_embedding: bool
    meta: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedRules(BaseModel):
    """Paginated rules response."""

    items: List[RuleResponse]
    total: int
    page: int
    page_size: int
    pages: int
    domains_count: int = Field(default=0, description="Count of distinct domains")
    high_confidence_count: int = Field(default=0, description="Count of rules with confidence >= 0.8")


# --- Health Check ---


class HealthCheckResponse(BaseModel):
    """Health check response."""

    status: Literal["healthy", "degraded", "unhealthy"]
    database: bool
    llm: bool
    timestamp: datetime

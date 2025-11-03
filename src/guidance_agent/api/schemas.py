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
    age: int = Field(..., ge=40, le=100, description="Customer age (must be 40+)")
    initial_query: str = Field(
        ..., min_length=10, max_length=1000, description="Initial question or concern"
    )

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: int) -> int:
        """Validate age is appropriate for pension guidance."""
        if v < 40:
            raise ValueError("Pension guidance is typically for ages 40+")
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


# --- Health Check ---


class HealthCheckResponse(BaseModel):
    """Health check response."""

    status: Literal["healthy", "degraded", "unhealthy"]
    database: bool
    llm: bool
    timestamp: datetime

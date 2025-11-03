"""Admin API endpoints.

Requires authentication. Handles:
- Reviewing consultations
- Compliance metrics and reporting
- Time-series analytics
- Exporting consultations
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, Literal
from collections import defaultdict

from guidance_agent.api import schemas
from guidance_agent.api.dependencies import (
    get_db,
    get_current_admin,
    get_pagination_params,
    PaginationParams,
    get_consultation_or_404,
)
from guidance_agent.core.database import Consultation

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(get_current_admin)])


@router.get("/consultations", response_model=schemas.AdminConsultationListResponse)
async def list_consultations_admin(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(get_pagination_params),
    status: Optional[Literal["active", "completed"]] = None,
    min_compliance: Optional[float] = Query(None, ge=0, le=1),
):
    """List consultations with admin filters.

    Args:
        db: Database session
        pagination: Pagination parameters
        status: Filter by status (active/completed)
        min_compliance: Filter by minimum compliance score

    Returns:
        Paginated list of consultations with detailed metrics
    """
    # Build query
    query = db.query(Consultation)

    # Apply filters
    if status == "active":
        query = query.filter(Consultation.end_time.is_(None))
    elif status == "completed":
        query = query.filter(Consultation.end_time.isnot(None))

    # Order by most recent first
    query = query.order_by(Consultation.start_time.desc())

    # Get total count
    total = query.count()

    # Apply pagination
    consultations = query.offset(pagination.skip).limit(pagination.limit).all()

    # Filter by compliance if specified
    if min_compliance is not None:
        filtered_consultations = []
        for c in consultations:
            scores = c.meta.get("compliance_scores", [])
            avg_score = sum(scores) / len(scores) if scores else 0
            if avg_score >= min_compliance:
                filtered_consultations.append(c)
        consultations = filtered_consultations
        total = len(filtered_consultations)

    # Convert to detailed response models
    items = []
    for c in consultations:
        # Calculate metrics
        message_count = len([m for m in c.conversation if m.get("role") != "system"])
        compliance_scores = c.meta.get("compliance_scores", [])
        avg_compliance = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0.0

        duration_minutes = None
        if c.end_time:
            duration = (c.end_time - c.start_time).total_seconds()
            duration_minutes = duration / 60

        metrics = schemas.ConsultationMetrics(
            message_count=message_count,
            avg_compliance_score=avg_compliance,
            customer_satisfaction=c.outcome.get("customer_satisfaction") if c.outcome else None,
            comprehension=c.outcome.get("comprehension") if c.outcome else None,
            duration_minutes=duration_minutes,
        )

        # Build conversation turns
        conversation_turns = [
            schemas.ConversationTurn(
                role=turn.get("role", "system"),
                content=turn.get("content", ""),
                timestamp=datetime.fromisoformat(
                    turn.get("timestamp", datetime.now().isoformat())
                ),
                compliance_score=turn.get("compliance_score"),
                compliance_confidence=turn.get("compliance_confidence"),
            )
            for turn in c.conversation
        ]

        items.append(
            schemas.AdminConsultationReview(
                id=c.id,
                customer_id=c.customer_id,
                customer_name=c.meta.get("customer_name", "Unknown"),
                customer_age=c.meta.get("customer_age", 0),
                advisor_name=c.meta.get("advisor_name", "Sarah"),
                conversation=conversation_turns,
                outcome=c.outcome,
                metrics=metrics,
                created_at=c.start_time,
                ended_at=c.end_time,
            )
        )

    return schemas.AdminConsultationListResponse(
        items=items,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get("/consultations/{consultation_id}", response_model=schemas.AdminConsultationReview)
async def get_consultation_review(
    consultation_id: str,
    db: Session = Depends(get_db),
):
    """Get detailed consultation for review.

    Args:
        consultation_id: UUID of consultation
        db: Database session

    Returns:
        Detailed consultation with metrics and analysis
    """
    consultation = get_consultation_or_404(consultation_id, db)

    # Calculate metrics
    message_count = len(
        [m for m in consultation.conversation if m.get("role") != "system"]
    )
    compliance_scores = consultation.meta.get("compliance_scores", [])
    avg_compliance = (
        sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0.0
    )

    duration_minutes = None
    if consultation.end_time:
        duration = (consultation.end_time - consultation.start_time).total_seconds()
        duration_minutes = duration / 60

    metrics = schemas.ConsultationMetrics(
        message_count=message_count,
        avg_compliance_score=avg_compliance,
        customer_satisfaction=consultation.outcome.get("customer_satisfaction")
        if consultation.outcome
        else None,
        comprehension=consultation.outcome.get("comprehension")
        if consultation.outcome
        else None,
        duration_minutes=duration_minutes,
    )

    # Build conversation turns
    conversation_turns = [
        schemas.ConversationTurn(
            role=turn.get("role", "system"),
            content=turn.get("content", ""),
            timestamp=datetime.fromisoformat(
                turn.get("timestamp", datetime.now().isoformat())
            ),
            compliance_score=turn.get("compliance_score"),
            compliance_confidence=turn.get("compliance_confidence"),
        )
        for turn in consultation.conversation
    ]

    return schemas.AdminConsultationReview(
        id=consultation.id,
        customer_id=consultation.customer_id,
        customer_name=consultation.meta.get("customer_name", "Unknown"),
        customer_age=consultation.meta.get("customer_age", 0),
        advisor_name=consultation.meta.get("advisor_name", "Sarah"),
        conversation=conversation_turns,
        outcome=consultation.outcome,
        metrics=metrics,
        created_at=consultation.start_time,
        ended_at=consultation.end_time,
    )


@router.get("/metrics/compliance", response_model=schemas.ComplianceMetrics)
async def get_compliance_metrics(
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
):
    """Get overall compliance metrics.

    Args:
        db: Database session
        days: Number of days to include in analysis

    Returns:
        Aggregated compliance metrics
    """
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # Query consultations in date range
    consultations = (
        db.query(Consultation)
        .filter(Consultation.start_time >= start_date)
        .filter(Consultation.start_time <= end_date)
        .all()
    )

    if not consultations:
        return schemas.ComplianceMetrics(
            total_consultations=0,
            avg_compliance_score=0.0,
            compliant_percentage=0.0,
            avg_satisfaction=0.0,
            period_start=start_date,
            period_end=end_date,
        )

    # Calculate metrics
    total_consultations = len(consultations)

    # Average compliance score
    all_scores = []
    for c in consultations:
        scores = c.meta.get("compliance_scores", [])
        all_scores.extend(scores)

    avg_compliance_score = sum(all_scores) / len(all_scores) if all_scores else 0.0

    # Compliant percentage (consultations with avg compliance >= 0.85)
    compliant_count = 0
    for c in consultations:
        if c.outcome and c.outcome.get("fca_compliant"):
            compliant_count += 1

    compliant_percentage = (compliant_count / total_consultations * 100) if total_consultations > 0 else 0.0

    # Average satisfaction
    satisfaction_scores = []
    for c in consultations:
        if c.outcome and "customer_satisfaction" in c.outcome:
            satisfaction_scores.append(c.outcome["customer_satisfaction"])

    avg_satisfaction = (
        sum(satisfaction_scores) / len(satisfaction_scores)
        if satisfaction_scores
        else 0.0
    )

    return schemas.ComplianceMetrics(
        total_consultations=total_consultations,
        avg_compliance_score=avg_compliance_score,
        compliant_percentage=compliant_percentage,
        avg_satisfaction=avg_satisfaction,
        period_start=start_date,
        period_end=end_date,
    )


@router.get("/metrics/time-series", response_model=schemas.TimeSeriesMetrics)
async def get_time_series_metrics(
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
):
    """Get compliance metrics over time.

    Args:
        db: Database session
        days: Number of days to include

    Returns:
        Time series data points
    """
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # Query consultations
    consultations = (
        db.query(Consultation)
        .filter(Consultation.start_time >= start_date)
        .filter(Consultation.start_time <= end_date)
        .all()
    )

    # Group by date
    daily_data = defaultdict(lambda: {"scores": [], "count": 0})

    for c in consultations:
        date_key = c.start_time.date().isoformat()
        scores = c.meta.get("compliance_scores", [])
        daily_data[date_key]["scores"].extend(scores)
        daily_data[date_key]["count"] += 1

    # Build data points
    data_points = []
    for date_str in sorted(daily_data.keys()):
        data = daily_data[date_str]
        avg_compliance = (
            sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0.0
        )

        data_points.append(
            schemas.TimeSeriesDataPoint(
                date=date_str,
                avg_compliance=avg_compliance,
                consultation_count=data["count"],
            )
        )

    return schemas.TimeSeriesMetrics(data_points=data_points)


@router.get("/consultations/{consultation_id}/export")
async def export_consultation(
    consultation_id: str,
    db: Session = Depends(get_db),
):
    """Export consultation as JSON.

    Args:
        consultation_id: UUID of consultation
        db: Database session

    Returns:
        Full consultation data as JSON
    """
    consultation = get_consultation_or_404(consultation_id, db)

    # Build export data
    export_data = {
        "id": str(consultation.id),
        "customer_id": str(consultation.customer_id),
        "advisor_id": str(consultation.advisor_id),
        "customer_name": consultation.meta.get("customer_name", "Unknown"),
        "customer_age": consultation.meta.get("customer_age", 0),
        "advisor_name": consultation.meta.get("advisor_name", "Sarah"),
        "conversation": consultation.conversation,
        "outcome": consultation.outcome,
        "start_time": consultation.start_time.isoformat(),
        "end_time": consultation.end_time.isoformat() if consultation.end_time else None,
        "duration_seconds": consultation.duration_seconds,
        "metadata": consultation.meta,
        "exported_at": datetime.now().isoformat(),
    }

    return export_data

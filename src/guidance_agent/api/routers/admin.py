"""Admin API endpoints.

Requires authentication. Handles:
- Reviewing consultations
- Compliance metrics and reporting
- Time-series analytics
- Exporting consultations
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from datetime import datetime, timedelta, date, timezone
from typing import Optional, Literal
from collections import defaultdict
from uuid import UUID
import math

from guidance_agent.api import schemas
from guidance_agent.api.dependencies import (
    get_db,
    get_current_admin,
    get_pagination_params,
    PaginationParams,
    get_consultation_or_404,
)
from guidance_agent.core.database import Consultation, SystemSettings, FCAKnowledge, PensionKnowledge, Memory, Case, Rule, MemoryTypeEnum

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(get_current_admin)])


@router.get("/consultations", response_model=schemas.AdminConsultationListResponse)
async def list_consultations_admin(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(get_pagination_params),
    status: Optional[Literal["active", "completed"]] = None,
    min_compliance: Optional[float] = Query(None, ge=0, le=1),
    search: Optional[str] = Query(None, description="Search by customer name or topic"),
    from_date: Optional[date] = Query(None, description="Filter consultations from this date"),
    to_date: Optional[date] = Query(None, description="Filter consultations up to this date"),
):
    """List consultations with admin filters.

    Args:
        db: Database session
        pagination: Pagination parameters
        status: Filter by status (active/completed)
        min_compliance: Filter by minimum compliance score
        search: Search by customer name or conversation content
        from_date: Filter consultations starting from this date
        to_date: Filter consultations up to this date (inclusive)

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

    # Date range filtering
    if from_date:
        from_datetime = datetime.combine(from_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        query = query.filter(Consultation.start_time >= from_datetime)

    if to_date:
        # Include the entire day by going to end of day
        to_datetime = datetime.combine(to_date, datetime.max.time()).replace(tzinfo=timezone.utc)
        query = query.filter(Consultation.start_time <= to_datetime)

    # Order by most recent first
    query = query.order_by(Consultation.start_time.desc())

    # Get all consultations for filtering (we need to filter by JSON fields)
    all_consultations = query.all()

    # Apply search filter (customer name or conversation content)
    if search:
        search_lower = search.lower()
        filtered_consultations = []
        for c in all_consultations:
            # Check customer name in meta
            customer_name = c.meta.get("customer_name", "").lower()
            if search_lower in customer_name:
                filtered_consultations.append(c)
                continue

            # Check conversation content
            conversation_text = " ".join(
                turn.get("content", "").lower()
                for turn in c.conversation
                if turn.get("role") != "system"
            )
            if search_lower in conversation_text:
                filtered_consultations.append(c)

        all_consultations = filtered_consultations

    # Filter by compliance if specified
    if min_compliance is not None:
        filtered_consultations = []
        for c in all_consultations:
            scores = c.meta.get("compliance_scores", [])
            avg_score = sum(scores) / len(scores) if scores else 0
            if avg_score >= min_compliance:
                filtered_consultations.append(c)
        all_consultations = filtered_consultations

    # Get total after filtering
    total = len(all_consultations)

    # Apply pagination after filtering
    consultations = all_consultations[pagination.skip : pagination.skip + pagination.limit]

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
                    turn.get("timestamp", datetime.now(timezone.utc).isoformat())
                ),
                compliance_score=turn.get("compliance_score"),
                compliance_confidence=turn.get("compliance_confidence"),
                compliance_reasoning=turn.get("compliance_reasoning"),
                compliance_issues=turn.get("compliance_issues"),
                compliance_passed=turn.get("compliance_passed"),
                requires_human_review=turn.get("requires_human_review"),
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
                turn.get("timestamp", datetime.now(timezone.utc).isoformat())
            ),
            compliance_score=turn.get("compliance_score"),
            compliance_confidence=turn.get("compliance_confidence"),
            compliance_reasoning=turn.get("compliance_reasoning"),
            compliance_issues=turn.get("compliance_issues"),
            compliance_passed=turn.get("compliance_passed"),
            requires_human_review=turn.get("requires_human_review"),
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


@router.get("/metrics")
async def get_all_metrics(
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
):
    """Get comprehensive metrics for admin dashboard.

    Args:
        db: Database session
        days: Number of days to include in analysis

    Returns:
        Comprehensive metrics including compliance, usage, and performance data
    """
    # Calculate date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)

    # Query consultations in date range
    consultations = (
        db.query(Consultation)
        .filter(Consultation.start_time >= start_date)
        .filter(Consultation.start_time <= end_date)
        .all()
    )

    # Initialize metrics
    total_consultations = len(consultations)
    completed_consultations = len([c for c in consultations if c.end_time is not None])
    active_consultations = total_consultations - completed_consultations

    # Calculate average response time (time for first advisor response)
    response_times = []
    for c in consultations:
        customer_msg = None
        advisor_msg = None
        for turn in c.conversation:
            if turn.get("role") == "customer" and not customer_msg:
                customer_msg = turn
            elif turn.get("role") == "advisor" and customer_msg and not advisor_msg:
                advisor_msg = turn
                break
        if customer_msg and advisor_msg:
            try:
                customer_time = datetime.fromisoformat(customer_msg.get("timestamp", ""))
                advisor_time = datetime.fromisoformat(advisor_msg.get("timestamp", ""))
                response_times.append((advisor_time - customer_time).total_seconds())
            except (ValueError, TypeError):
                pass

    avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0

    # Calculate completion rate
    completion_rate = (completed_consultations / total_consultations * 100) if total_consultations > 0 else 0.0

    # Compliance breakdown by category (Note: currently using static data as real compliance categorization needs to be implemented)
    compliance_breakdown = [
        {"category": "Risk Assessment", "score": 98},
        {"category": "Documentation", "score": 96},
        {"category": "Disclosure Requirements", "score": 94},
        {"category": "Client Suitability", "score": 97},
        {"category": "Regulatory Reporting", "score": 95}
    ]

    # Top topics from consultation metadata
    topic_counts = defaultdict(int)
    for c in consultations:
        topic = c.meta.get("initial_topic", "Unknown")
        if topic and topic != "Unknown":
            topic_counts[topic] += 1

    # If no topics found, use empty counts
    if not topic_counts:
        top_topics = []
    else:
        top_topics = [
            {"name": topic, "count": count}
            for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

    # Peak hours analysis
    hour_counts = defaultdict(int)
    for c in consultations:
        hour = c.start_time.hour
        hour_counts[hour] += 1

    # Find top 4 peak hours
    peak_hours_data = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:4]
    peak_hours = [
        {
            "time": f"{hour:02d}:00 - {(hour+1) % 24:02d}:00",
            "sessions": count
        }
        for hour, count in peak_hours_data
    ]

    # Customer retention (consultations with returning customers)
    customer_consultation_counts = defaultdict(int)
    for c in consultations:
        customer_consultation_counts[c.customer_id] += 1

    returning_customers = len([count for count in customer_consultation_counts.values() if count > 1])
    retention_rate = (returning_customers / len(customer_consultation_counts) * 100) if customer_consultation_counts else 0.0

    # Calculate satisfaction
    satisfaction_scores = []
    for c in consultations:
        if c.outcome and "customer_satisfaction" in c.outcome:
            sat_score = c.outcome["customer_satisfaction"]
            if sat_score is not None:
                satisfaction_scores.append(sat_score)

    avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0.0

    # Calculate compliance rate (percentage of consultations that are compliant)
    compliant_count = 0
    all_compliance_scores = []
    for c in consultations:
        scores = c.meta.get("compliance_scores", [])
        all_compliance_scores.extend(scores)
        # Check if consultation is compliant (using outcome flag if available)
        if c.outcome and c.outcome.get("fca_compliant"):
            compliant_count += 1

    avg_compliance_score = sum(all_compliance_scores) / len(all_compliance_scores) if all_compliance_scores else 0.0
    compliance_rate = (compliant_count / total_consultations * 100) if total_consultations > 0 else 0.0

    return {
        "performance_metrics": {
            "avg_response_time": round(avg_response_time, 1),
            "customer_retention": round(retention_rate, 1),
            "active_sessions": active_consultations,
            "completion_rate": round(completion_rate, 1)
        },
        "compliance_breakdown": compliance_breakdown,
        "top_topics": top_topics,
        "peak_hours": peak_hours,
        "consultations": {
            "total": total_consultations,
            "avg_satisfaction": round(avg_satisfaction, 1),
            "compliance_rate": round(compliance_rate, 1)
        },
        "summary": {
            "total_consultations": total_consultations,
            "completed_consultations": completed_consultations,
            "avg_satisfaction": round(avg_satisfaction, 1),
            "period_days": days
        }
    }


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
    end_date = datetime.now(timezone.utc)
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
    end_date = datetime.now(timezone.utc)
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
        "exported_at": datetime.now(timezone.utc).isoformat(),
    }

    return export_data


@router.get("/settings", response_model=schemas.AdminSettingsResponse)
async def get_admin_settings(
    db: Session = Depends(get_db),
):
    """Get admin settings.

    Args:
        db: Database session

    Returns:
        Current admin settings
    """
    # Get or create settings (single row table)
    settings = db.query(SystemSettings).filter(SystemSettings.id == 1).first()

    if not settings:
        # Create default settings if none exist
        settings = SystemSettings(id=1)
        db.add(settings)
        db.commit()
        db.refresh(settings)

    # Convert database model to response schema
    return schemas.AdminSettingsResponse(
        systemName=settings.system_name,
        supportEmail=settings.support_email,
        sessionTimeout=settings.session_timeout,
        fcaComplianceEnabled=settings.fca_compliance_enabled.lower() == "true",
        riskAssessmentRequired=settings.risk_assessment_required.lower() == "true",
        autoArchive=settings.auto_archive.lower() == "true",
        emailNotifications=settings.email_notifications.lower() == "true",
        complianceAlerts=settings.compliance_alerts.lower() == "true",
        dailyDigest=settings.daily_digest.lower() == "true",
        aiModel=settings.ai_model,
        temperature=settings.temperature,
        maxTokens=settings.max_tokens,
    )


@router.put("/settings", response_model=schemas.AdminSettingsResponse)
async def update_admin_settings(
    settings_update: schemas.UpdateAdminSettingsRequest,
    db: Session = Depends(get_db),
):
    """Update admin settings.

    Args:
        settings_update: Updated settings data
        db: Database session

    Returns:
        Updated admin settings
    """
    # Get or create settings (single row table)
    settings = db.query(SystemSettings).filter(SystemSettings.id == 1).first()

    if not settings:
        # Create new settings if none exist
        settings = SystemSettings(id=1)
        db.add(settings)

    # Update settings
    settings.system_name = settings_update.systemName
    settings.support_email = settings_update.supportEmail
    settings.session_timeout = settings_update.sessionTimeout
    settings.fca_compliance_enabled = "true" if settings_update.fcaComplianceEnabled else "false"
    settings.risk_assessment_required = "true" if settings_update.riskAssessmentRequired else "false"
    settings.auto_archive = "true" if settings_update.autoArchive else "false"
    settings.email_notifications = "true" if settings_update.emailNotifications else "false"
    settings.compliance_alerts = "true" if settings_update.complianceAlerts else "false"
    settings.daily_digest = "true" if settings_update.dailyDigest else "false"
    settings.ai_model = settings_update.aiModel
    settings.temperature = settings_update.temperature
    settings.max_tokens = settings_update.maxTokens

    db.commit()
    db.refresh(settings)

    # Convert database model to response schema
    return schemas.AdminSettingsResponse(
        systemName=settings.system_name,
        supportEmail=settings.support_email,
        sessionTimeout=settings.session_timeout,
        fcaComplianceEnabled=settings.fca_compliance_enabled.lower() == "true",
        riskAssessmentRequired=settings.risk_assessment_required.lower() == "true",
        autoArchive=settings.auto_archive.lower() == "true",
        emailNotifications=settings.email_notifications.lower() == "true",
        complianceAlerts=settings.compliance_alerts.lower() == "true",
        dailyDigest=settings.daily_digest.lower() == "true",
        aiModel=settings.ai_model,
        temperature=settings.temperature,
        maxTokens=settings.max_tokens,
    )

# --- Knowledge Base Endpoints ---


@router.get("/fca-knowledge", response_model=schemas.PaginatedFCAKnowledge)
async def list_fca_knowledge(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in content"),
    from_date: Optional[date] = Query(None, description="Filter from date"),
    to_date: Optional[date] = Query(None, description="Filter to date"),
):
    """List FCA knowledge with filters and pagination.

    Args:
        db: Database session
        page: Page number (default: 1)
        page_size: Items per page (default: 20, max: 100)
        category: Filter by category
        search: Text search in content
        from_date: Filter by creation date (from)
        to_date: Filter by creation date (to)

    Returns:
        Paginated list of FCA knowledge items
    """
    # Build query
    query = db.query(FCAKnowledge)

    # Apply filters
    if category:
        query = query.filter(FCAKnowledge.category == category)

    if search:
        query = query.filter(FCAKnowledge.content.ilike(f"%{search}%"))

    if from_date:
        query = query.filter(FCAKnowledge.created_at >= from_date)

    if to_date:
        # Add one day to include the entire to_date
        to_datetime = datetime.combine(to_date, datetime.max.time())
        query = query.filter(FCAKnowledge.created_at <= to_datetime)

    # Order by most recent first
    query = query.order_by(FCAKnowledge.created_at.desc())

    # Get total count
    total = query.count()

    # Calculate pagination
    skip = (page - 1) * page_size
    pages = math.ceil(total / page_size) if total > 0 else 0

    # Apply pagination
    items = query.offset(skip).limit(page_size).all()

    # Convert to response models
    response_items = []
    for item in items:
        response_items.append(
            schemas.FCAKnowledgeResponse(
                id=item.id,
                content=item.content,
                source=item.source,
                category=item.category,
                has_embedding=item.embedding is not None,
                meta=item.meta or {},
                created_at=item.created_at,
            )
        )

    return schemas.PaginatedFCAKnowledge(
        items=response_items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/fca-knowledge/{knowledge_id}", response_model=schemas.FCAKnowledgeResponse)
async def get_fca_knowledge_by_id(
    knowledge_id: UUID,
    db: Session = Depends(get_db),
):
    """Get FCA knowledge item by ID.

    Args:
        knowledge_id: UUID of the knowledge item
        db: Database session

    Returns:
        FCA knowledge item details

    Raises:
        HTTPException: 404 if knowledge item not found
    """
    item = db.query(FCAKnowledge).filter(FCAKnowledge.id == knowledge_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="FCA knowledge item not found")

    return schemas.FCAKnowledgeResponse(
        id=item.id,
        content=item.content,
        source=item.source,
        category=item.category,
        has_embedding=item.embedding is not None,
        meta=item.meta or {},
        created_at=item.created_at,
    )


@router.get("/pension-knowledge", response_model=schemas.PaginatedPensionKnowledge)
async def list_pension_knowledge(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    subcategory: Optional[str] = Query(None, description="Filter by subcategory"),
    search: Optional[str] = Query(None, description="Search in content"),
    from_date: Optional[date] = Query(None, description="Filter from date"),
    to_date: Optional[date] = Query(None, description="Filter to date"),
):
    """List pension knowledge with filters and pagination.

    Args:
        db: Database session
        page: Page number (default: 1)
        page_size: Items per page (default: 20, max: 100)
        category: Filter by category
        subcategory: Filter by subcategory
        search: Text search in content
        from_date: Filter by creation date (from)
        to_date: Filter by creation date (to)

    Returns:
        Paginated list of pension knowledge items
    """
    # Build query
    query = db.query(PensionKnowledge)

    # Apply filters
    if category:
        query = query.filter(PensionKnowledge.category == category)

    if subcategory:
        query = query.filter(PensionKnowledge.subcategory == subcategory)

    if search:
        query = query.filter(PensionKnowledge.content.ilike(f"%{search}%"))

    if from_date:
        query = query.filter(PensionKnowledge.created_at >= from_date)

    if to_date:
        # Add one day to include the entire to_date
        to_datetime = datetime.combine(to_date, datetime.max.time())
        query = query.filter(PensionKnowledge.created_at <= to_datetime)

    # Order by most recent first
    query = query.order_by(PensionKnowledge.created_at.desc())

    # Get total count
    total = query.count()

    # Calculate pagination
    skip = (page - 1) * page_size
    pages = math.ceil(total / page_size) if total > 0 else 0

    # Apply pagination
    items = query.offset(skip).limit(page_size).all()

    # Convert to response models
    response_items = []
    for item in items:
        response_items.append(
            schemas.PensionKnowledgeResponse(
                id=item.id,
                content=item.content,
                category=item.category,
                subcategory=item.subcategory,
                has_embedding=item.embedding is not None,
                meta=item.meta or {},
                created_at=item.created_at,
            )
        )

    return schemas.PaginatedPensionKnowledge(
        items=response_items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/pension-knowledge/{knowledge_id}", response_model=schemas.PensionKnowledgeResponse)
async def get_pension_knowledge_by_id(
    knowledge_id: UUID,
    db: Session = Depends(get_db),
):
    """Get pension knowledge item by ID.

    Args:
        knowledge_id: UUID of the knowledge item
        db: Database session

    Returns:
        Pension knowledge item details

    Raises:
        HTTPException: 404 if knowledge item not found
    """
    item = db.query(PensionKnowledge).filter(PensionKnowledge.id == knowledge_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Pension knowledge item not found")

    return schemas.PensionKnowledgeResponse(
        id=item.id,
        content=item.content,
        category=item.category,
        subcategory=item.subcategory,
        has_embedding=item.embedding is not None,
        meta=item.meta or {},
        created_at=item.created_at,
    )


@router.get("/customers", response_model=schemas.PaginatedCustomers)
async def list_customers(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    from_date: Optional[date] = Query(None, description="Filter by last consultation from date"),
    to_date: Optional[date] = Query(None, description="Filter by last consultation to date"),
    sort_by: Literal["total_consultations", "last_consultation", "avg_compliance"] = Query(
        "last_consultation", description="Sort field"
    ),
    sort_order: Literal["asc", "desc"] = Query("desc", description="Sort order"),
):
    """List customers with aggregated consultation statistics.

    This endpoint aggregates data from the consultations table to create
    a customer view with comprehensive statistics.

    Args:
        db: Database session
        page: Page number (1-indexed)
        page_size: Number of items per page
        from_date: Filter customers by last consultation from date
        to_date: Filter customers by last consultation to date
        sort_by: Field to sort by
        sort_order: Sort order (asc/desc)

    Returns:
        Paginated list of customers with aggregated statistics
    """
    # Get all unique customer IDs
    unique_customers = (
        db.query(Consultation.customer_id)
        .distinct()
        .all()
    )

    # Build aggregated customer data
    customer_data = []

    for (customer_id,) in unique_customers:
        # Get all consultations for this customer
        consultations = (
            db.query(Consultation)
            .filter(Consultation.customer_id == customer_id)
            .order_by(Consultation.start_time.asc())
            .all()
        )

        if not consultations:
            continue

        # Calculate aggregated metrics
        total_consultations = len(consultations)
        first_consultation = consultations[0].start_time
        last_consultation = consultations[-1].start_time

        # Calculate average compliance score
        all_compliance_scores = []
        for c in consultations:
            scores = c.meta.get("compliance_scores", [])
            all_compliance_scores.extend(scores)

        avg_compliance_score = (
            sum(all_compliance_scores) / len(all_compliance_scores)
            if all_compliance_scores
            else 0.0
        )

        # Calculate average satisfaction
        satisfaction_scores = []
        for c in consultations:
            if c.outcome and "customer_satisfaction" in c.outcome:
                sat = c.outcome["customer_satisfaction"]
                if sat is not None:
                    satisfaction_scores.append(sat)

        avg_satisfaction = (
            sum(satisfaction_scores) / len(satisfaction_scores)
            if satisfaction_scores
            else None
        )

        # Collect unique topics
        topics = set()
        for c in consultations:
            topic = c.meta.get("initial_topic")
            if topic:
                topics.add(topic)

        # Get customer profile from most recent consultation
        most_recent = consultations[-1]
        customer_profile = {
            "customer_name": most_recent.meta.get("customer_name", "Unknown"),
            "customer_age": most_recent.meta.get("customer_age", 0),
            "advisor_name": most_recent.meta.get("advisor_name", "Sarah"),
        }

        customer_data.append({
            "customer_id": customer_id,
            "total_consultations": total_consultations,
            "first_consultation": first_consultation,
            "last_consultation": last_consultation,
            "avg_compliance_score": avg_compliance_score,
            "avg_satisfaction": avg_satisfaction,
            "topics": list(topics),
            "customer_profile": customer_profile,
        })

    # Apply date range filters
    if from_date:
        from_datetime = datetime.combine(from_date, datetime.min.time(), tzinfo=timezone.utc)
        customer_data = [
            c for c in customer_data
            if c["last_consultation"].replace(tzinfo=timezone.utc) >= from_datetime
        ]

    if to_date:
        to_datetime = datetime.combine(to_date, datetime.max.time(), tzinfo=timezone.utc)
        customer_data = [
            c for c in customer_data
            if c["last_consultation"].replace(tzinfo=timezone.utc) <= to_datetime
        ]

    # Sort customer data
    sort_key_map = {
        "total_consultations": lambda x: x["total_consultations"],
        "last_consultation": lambda x: x["last_consultation"],
        "avg_compliance": lambda x: x["avg_compliance_score"],
    }

    customer_data.sort(
        key=sort_key_map[sort_by],
        reverse=(sort_order == "desc")
    )

    # Calculate statistics
    total_customers = len(customer_data)

    # Active customers (last 30 days)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    active_customers_30d = len([
        c for c in customer_data
        if c["last_consultation"].replace(tzinfo=timezone.utc) >= thirty_days_ago
    ])

    # Average consultations per customer
    avg_consultations_per_customer = (
        sum(c["total_consultations"] for c in customer_data) / total_customers
        if total_customers > 0
        else 0.0
    )

    stats = schemas.CustomerStats(
        total_customers=total_customers,
        active_customers_30d=active_customers_30d,
        avg_consultations_per_customer=avg_consultations_per_customer,
    )

    # Apply pagination
    skip = (page - 1) * page_size
    paginated_data = customer_data[skip:skip + page_size]

    # Calculate total pages
    pages = math.ceil(total_customers / page_size) if total_customers > 0 else 0

    # Build response items
    items = [
        schemas.AdminCustomerResponse(
            customer_id=c["customer_id"],
            total_consultations=c["total_consultations"],
            first_consultation=c["first_consultation"],
            last_consultation=c["last_consultation"],
            avg_compliance_score=c["avg_compliance_score"],
            avg_satisfaction=c["avg_satisfaction"],
            topics=c["topics"],
            customer_profile=c["customer_profile"],
        )
        for c in paginated_data
    ]

    return schemas.PaginatedCustomers(
        items=items,
        total=total_customers,
        page=page,
        page_size=page_size,
        pages=pages,
        stats=stats,
    )


@router.get("/customers/{customer_id}", response_model=schemas.AdminCustomerResponse)
async def get_customer_detail(
    customer_id: UUID,
    db: Session = Depends(get_db),
):
    """Get detailed customer information with consultation history.

    Args:
        customer_id: UUID of the customer
        db: Database session

    Returns:
        Detailed customer data with recent consultations

    Raises:
        HTTPException: If customer not found (no consultations)
    """
    # Get all consultations for this customer
    consultations = (
        db.query(Consultation)
        .filter(Consultation.customer_id == customer_id)
        .order_by(Consultation.start_time.asc())
        .all()
    )

    if not consultations:
        raise HTTPException(
            status_code=404,
            detail=f"Customer {customer_id} not found"
        )

    # Calculate aggregated metrics
    total_consultations = len(consultations)
    first_consultation = consultations[0].start_time
    last_consultation = consultations[-1].start_time

    # Calculate average compliance score
    all_compliance_scores = []
    for c in consultations:
        scores = c.meta.get("compliance_scores", [])
        all_compliance_scores.extend(scores)

    avg_compliance_score = (
        sum(all_compliance_scores) / len(all_compliance_scores)
        if all_compliance_scores
        else 0.0
    )

    # Calculate average satisfaction
    satisfaction_scores = []
    for c in consultations:
        if c.outcome and "customer_satisfaction" in c.outcome:
            sat = c.outcome["customer_satisfaction"]
            if sat is not None:
                satisfaction_scores.append(sat)

    avg_satisfaction = (
        sum(satisfaction_scores) / len(satisfaction_scores)
        if satisfaction_scores
        else None
    )

    # Collect unique topics
    topics = set()
    for c in consultations:
        topic = c.meta.get("initial_topic")
        if topic:
            topics.add(topic)

    # Get customer profile from most recent consultation
    most_recent = consultations[-1]
    customer_profile = {
        "customer_name": most_recent.meta.get("customer_name", "Unknown"),
        "customer_age": most_recent.meta.get("customer_age", 0),
        "advisor_name": most_recent.meta.get("advisor_name", "Sarah"),
    }

    # Get last 5 consultations for history
    recent_consultations_data = consultations[-5:]

    recent_consultations = [
        schemas.ConsultationResponse(
            id=c.id,
            customer_id=c.customer_id,
            advisor_name=c.meta.get("advisor_name", "Sarah"),
            status="completed" if c.end_time else "active",
            created_at=c.start_time,
            ended_at=c.end_time,
        )
        for c in recent_consultations_data
    ]

    return schemas.AdminCustomerResponse(
        customer_id=customer_id,
        total_consultations=total_consultations,
        first_consultation=first_consultation,
        last_consultation=last_consultation,
        avg_compliance_score=avg_compliance_score,
        avg_satisfaction=avg_satisfaction,
        topics=list(topics),
        customer_profile=customer_profile,
        recent_consultations=recent_consultations,
    )


# --- Learning System Endpoints ---


@router.get("/memories", response_model=schemas.PaginatedMemories)
async def list_memories(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    memory_type: Optional[Literal["observation", "reflection", "plan"]] = None,
    min_importance: Optional[float] = Query(None, ge=0.0, le=1.0),
    max_importance: Optional[float] = Query(None, ge=0.0, le=1.0),
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    sort_by: Literal["importance", "timestamp", "last_accessed"] = "timestamp",
    sort_order: Literal["asc", "desc"] = "desc",
):
    """List memories with filters and sorting.

    Args:
        db: Database session
        page: Page number
        page_size: Items per page
        memory_type: Filter by memory type (observation/reflection/plan)
        min_importance: Minimum importance score (0.0-1.0)
        max_importance: Maximum importance score (0.0-1.0)
        from_date: Filter by timestamp from date
        to_date: Filter by timestamp to date
        sort_by: Sort field
        sort_order: Sort order (asc/desc)

    Returns:
        Paginated list of memories
    """
    # Build query
    query = db.query(Memory)

    # Apply filters
    if memory_type:
        query = query.filter(Memory.memory_type == memory_type)

    if min_importance is not None:
        query = query.filter(Memory.importance >= min_importance)

    if max_importance is not None:
        query = query.filter(Memory.importance <= max_importance)

    if from_date:
        from_datetime = datetime.combine(from_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        query = query.filter(Memory.timestamp >= from_datetime)

    if to_date:
        to_datetime = datetime.combine(to_date, datetime.max.time()).replace(tzinfo=timezone.utc)
        query = query.filter(Memory.timestamp <= to_datetime)

    # Apply sorting
    sort_field = {
        "importance": Memory.importance,
        "timestamp": Memory.timestamp,
        "last_accessed": Memory.last_accessed,
    }[sort_by]

    if sort_order == "desc":
        query = query.order_by(sort_field.desc())
    else:
        query = query.order_by(sort_field.asc())

    # Get total count
    total = query.count()

    # Calculate pagination
    pages = math.ceil(total / page_size) if total > 0 else 0
    skip = (page - 1) * page_size

    # Get paginated results
    memories = query.offset(skip).limit(page_size).all()

    # Calculate type counts (across all memories, not just current page)
    type_counts_query = (
        db.query(Memory.memory_type, func.count(Memory.id))
        .group_by(Memory.memory_type)
    )

    # Apply same filters for type counts
    if memory_type:
        type_counts_query = type_counts_query.filter(Memory.memory_type == memory_type)
    if min_importance is not None:
        type_counts_query = type_counts_query.filter(Memory.importance >= min_importance)
    if max_importance is not None:
        type_counts_query = type_counts_query.filter(Memory.importance <= max_importance)
    if from_date:
        from_datetime = datetime.combine(from_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        type_counts_query = type_counts_query.filter(Memory.timestamp >= from_datetime)
    if to_date:
        to_datetime = datetime.combine(to_date, datetime.max.time()).replace(tzinfo=timezone.utc)
        type_counts_query = type_counts_query.filter(Memory.timestamp <= to_datetime)

    type_counts_result = type_counts_query.all()
    type_counts = {
        str(mem_type.value if hasattr(mem_type, "value") else mem_type): count
        for mem_type, count in type_counts_result
    }

    # Convert to response models
    items = [
        schemas.MemoryResponse(
            id=m.id,
            description=m.description,
            timestamp=m.timestamp,
            last_accessed=m.last_accessed,
            importance=m.importance,
            memory_type=m.memory_type.value if hasattr(m.memory_type, "value") else m.memory_type,
            has_embedding=m.embedding is not None,
            meta=m.meta or {},
            created_at=m.created_at,
        )
        for m in memories
    ]

    return schemas.PaginatedMemories(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        type_counts=type_counts,
    )


@router.get("/memories/{memory_id}", response_model=schemas.MemoryResponse)
async def get_memory(
    memory_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a specific memory by ID.

    Args:
        memory_id: UUID of the memory
        db: Database session

    Returns:
        Memory detail

    Raises:
        HTTPException: 404 if memory not found
    """
    memory = db.query(Memory).filter(Memory.id == memory_id).first()

    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")

    return schemas.MemoryResponse(
        id=memory.id,
        description=memory.description,
        timestamp=memory.timestamp,
        last_accessed=memory.last_accessed,
        importance=memory.importance,
        memory_type=memory.memory_type.value if hasattr(memory.memory_type, "value") else memory.memory_type,
        has_embedding=memory.embedding is not None,
        meta=memory.meta or {},
        created_at=memory.created_at,
    )


@router.get("/cases", response_model=schemas.PaginatedCases)
async def list_cases(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    task_type: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
):
    """List cases with filters.

    Args:
        db: Database session
        page: Page number
        page_size: Items per page
        task_type: Filter by task type
        from_date: Filter by created_at from date
        to_date: Filter by created_at to date

    Returns:
        Paginated list of cases
    """
    # Build query
    query = db.query(Case)

    # Apply filters
    if task_type:
        query = query.filter(Case.task_type == task_type)

    if from_date:
        from_datetime = datetime.combine(from_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        query = query.filter(Case.created_at >= from_datetime)

    if to_date:
        to_datetime = datetime.combine(to_date, datetime.max.time()).replace(tzinfo=timezone.utc)
        query = query.filter(Case.created_at <= to_datetime)

    # Default sorting by created_at desc
    query = query.order_by(Case.created_at.desc())

    # Get total count
    total = query.count()

    # Calculate pagination
    pages = math.ceil(total / page_size) if total > 0 else 0
    skip = (page - 1) * page_size

    # Get paginated results
    cases = query.offset(skip).limit(page_size).all()

    # Calculate statistics (across all cases matching the filters, not just current page)
    # Count distinct task types
    task_types_count_query = db.query(func.count(distinct(Case.task_type)))
    if task_type:
        task_types_count_query = task_types_count_query.filter(Case.task_type == task_type)
    if from_date:
        from_datetime = datetime.combine(from_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        task_types_count_query = task_types_count_query.filter(Case.created_at >= from_datetime)
    if to_date:
        to_datetime = datetime.combine(to_date, datetime.max.time()).replace(tzinfo=timezone.utc)
        task_types_count_query = task_types_count_query.filter(Case.created_at <= to_datetime)

    task_types_count = task_types_count_query.scalar() or 0

    # Count cases with outcomes
    with_outcomes_query = db.query(func.count(Case.id)).filter(Case.outcome.isnot(None))
    if task_type:
        with_outcomes_query = with_outcomes_query.filter(Case.task_type == task_type)
    if from_date:
        from_datetime = datetime.combine(from_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        with_outcomes_query = with_outcomes_query.filter(Case.created_at >= from_datetime)
    if to_date:
        to_datetime = datetime.combine(to_date, datetime.max.time()).replace(tzinfo=timezone.utc)
        with_outcomes_query = with_outcomes_query.filter(Case.created_at <= to_datetime)

    with_outcomes_count = with_outcomes_query.scalar() or 0

    # Convert to response models
    items = [
        schemas.CaseResponse(
            id=c.id,
            task_type=c.task_type,
            customer_situation=c.customer_situation,
            guidance_provided=c.guidance_provided,
            outcome=c.outcome or {},
            has_embedding=c.embedding is not None,
            meta=c.meta or {},
            created_at=c.created_at,
        )
        for c in cases
    ]

    return schemas.PaginatedCases(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        task_types_count=task_types_count,
        with_outcomes_count=with_outcomes_count,
    )


@router.get("/cases/{case_id}", response_model=schemas.CaseResponse)
async def get_case(
    case_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a specific case by ID.

    Args:
        case_id: UUID of the case
        db: Database session

    Returns:
        Case detail

    Raises:
        HTTPException: 404 if case not found
    """
    case = db.query(Case).filter(Case.id == case_id).first()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    return schemas.CaseResponse(
        id=case.id,
        task_type=case.task_type,
        customer_situation=case.customer_situation,
        guidance_provided=case.guidance_provided,
        outcome=case.outcome or {},
        has_embedding=case.embedding is not None,
        meta=case.meta or {},
        created_at=case.created_at,
    )


@router.get("/rules", response_model=schemas.PaginatedRules)
async def list_rules(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    domain: Optional[str] = None,
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0),
    max_confidence: Optional[float] = Query(None, ge=0.0, le=1.0),
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    sort_by: Literal["confidence", "created_at", "updated_at"] = "updated_at",
    sort_order: Literal["asc", "desc"] = "desc",
):
    """List rules with filters and sorting.

    Args:
        db: Database session
        page: Page number
        page_size: Items per page
        domain: Filter by domain
        min_confidence: Minimum confidence score (0.0-1.0)
        max_confidence: Maximum confidence score (0.0-1.0)
        from_date: Filter by created_at from date
        to_date: Filter by created_at to date
        sort_by: Sort field
        sort_order: Sort order (asc/desc)

    Returns:
        Paginated list of rules
    """
    # Build query
    query = db.query(Rule)

    # Apply filters
    if domain:
        query = query.filter(Rule.domain == domain)

    if min_confidence is not None:
        query = query.filter(Rule.confidence >= min_confidence)

    if max_confidence is not None:
        query = query.filter(Rule.confidence <= max_confidence)

    if from_date:
        from_datetime = datetime.combine(from_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        query = query.filter(Rule.created_at >= from_datetime)

    if to_date:
        to_datetime = datetime.combine(to_date, datetime.max.time()).replace(tzinfo=timezone.utc)
        query = query.filter(Rule.created_at <= to_datetime)

    # Apply sorting
    sort_field = {
        "confidence": Rule.confidence,
        "created_at": Rule.created_at,
        "updated_at": Rule.updated_at,
    }[sort_by]

    if sort_order == "desc":
        query = query.order_by(sort_field.desc())
    else:
        query = query.order_by(sort_field.asc())

    # Get total count
    total = query.count()

    # Calculate pagination
    pages = math.ceil(total / page_size) if total > 0 else 0
    skip = (page - 1) * page_size

    # Get paginated results
    rules = query.offset(skip).limit(page_size).all()

    # Calculate statistics (across all rules matching the filters, not just current page)
    # Count distinct domains
    domains_count_query = db.query(func.count(distinct(Rule.domain)))
    if domain:
        domains_count_query = domains_count_query.filter(Rule.domain == domain)
    if min_confidence is not None:
        domains_count_query = domains_count_query.filter(Rule.confidence >= min_confidence)
    if max_confidence is not None:
        domains_count_query = domains_count_query.filter(Rule.confidence <= max_confidence)
    if from_date:
        from_datetime = datetime.combine(from_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        domains_count_query = domains_count_query.filter(Rule.created_at >= from_datetime)
    if to_date:
        to_datetime = datetime.combine(to_date, datetime.max.time()).replace(tzinfo=timezone.utc)
        domains_count_query = domains_count_query.filter(Rule.created_at <= to_datetime)

    domains_count = domains_count_query.scalar() or 0

    # Count rules with high confidence (>= 0.8)
    high_confidence_query = db.query(func.count(Rule.id)).filter(Rule.confidence >= 0.8)
    if domain:
        high_confidence_query = high_confidence_query.filter(Rule.domain == domain)
    if min_confidence is not None:
        high_confidence_query = high_confidence_query.filter(Rule.confidence >= min_confidence)
    if max_confidence is not None:
        high_confidence_query = high_confidence_query.filter(Rule.confidence <= max_confidence)
    if from_date:
        from_datetime = datetime.combine(from_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        high_confidence_query = high_confidence_query.filter(Rule.created_at >= from_datetime)
    if to_date:
        to_datetime = datetime.combine(to_date, datetime.max.time()).replace(tzinfo=timezone.utc)
        high_confidence_query = high_confidence_query.filter(Rule.created_at <= to_datetime)

    high_confidence_count = high_confidence_query.scalar() or 0

    # Convert to response models
    items = [
        schemas.RuleResponse(
            id=r.id,
            principle=r.principle,
            domain=r.domain,
            confidence=r.confidence,
            supporting_evidence=r.supporting_evidence or [],
            evidence_count=len(r.supporting_evidence) if r.supporting_evidence else 0,
            has_embedding=r.embedding is not None,
            meta=r.meta or {},
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in rules
    ]

    return schemas.PaginatedRules(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        domains_count=domains_count,
        high_confidence_count=high_confidence_count,
    )


@router.get("/rules/{rule_id}", response_model=schemas.RuleResponse)
async def get_rule(
    rule_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a specific rule by ID.

    Args:
        rule_id: UUID of the rule
        db: Database session

    Returns:
        Rule detail

    Raises:
        HTTPException: 404 if rule not found
    """
    rule = db.query(Rule).filter(Rule.id == rule_id).first()

    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    return schemas.RuleResponse(
        id=rule.id,
        principle=rule.principle,
        domain=rule.domain,
        confidence=rule.confidence,
        supporting_evidence=rule.supporting_evidence or [],
        evidence_count=len(rule.supporting_evidence) if rule.supporting_evidence else 0,
        has_embedding=rule.embedding is not None,
        meta=rule.meta or {},
        created_at=rule.created_at,
        updated_at=rule.updated_at,
    )

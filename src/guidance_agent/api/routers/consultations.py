"""Consultation API endpoints.

Handles:
- Creating new consultations
- Sending messages
- SSE streaming for real-time guidance
- Ending consultations
- Retrieving consultation details
"""

import json
import logging
from uuid import uuid4
from datetime import datetime, timezone
from typing import List, AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from sse_starlette.sse import EventSourceResponse

from guidance_agent.api import schemas
from guidance_agent.api.dependencies import (
    get_db,
    get_advisor_agent,
    get_pagination_params,
    PaginationParams,
    get_consultation_or_404,
    verify_consultation_active,
)
from guidance_agent.advisor.agent import AdvisorAgent
from guidance_agent.core.database import Consultation
from guidance_agent.core.types import CustomerProfile, CustomerDemographics, MemoryType
from guidance_agent.core.memory import MemoryNode, rate_importance
from guidance_agent.retrieval.embeddings import embed

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/consultations", tags=["consultations"])


@router.post("", response_model=schemas.ConsultationResponse, status_code=status.HTTP_201_CREATED)
async def create_consultation(
    request: schemas.CreateConsultationRequest,
    db: Session = Depends(get_db),
    advisor: AdvisorAgent = Depends(get_advisor_agent),
):
    """Create a new consultation session.

    Args:
        request: Customer profile and initial query
        db: Database session
        advisor: Advisor agent instance

    Returns:
        Created consultation details
    """
    # Generate IDs
    consultation_id = uuid4()
    customer_id = uuid4()

    # Create customer profile
    customer = CustomerProfile(
        customer_id=customer_id,
        demographics=CustomerDemographics(
            age=request.age,
            gender="unknown",
            location="unknown",
            employment_status="unknown",
            financial_literacy="medium",
        ),
        presenting_question=request.initial_query,
    )

    # Initial system message
    system_message = {
        "role": "system",
        "content": f"Consultation started with {request.name}, age {request.age}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Create consultation record
    consultation = Consultation(
        id=consultation_id,
        customer_id=customer_id,
        advisor_id=uuid4(),  # In production, use actual advisor ID
        conversation=[system_message],
        start_time=datetime.now(timezone.utc),
        meta={
            "customer_name": request.name,
            "customer_age": request.age,
            "advisor_name": advisor.profile.name,
            "initial_query": request.initial_query,
            "compliance_scores": [],
        },
    )

    db.add(consultation)
    db.commit()
    db.refresh(consultation)

    return schemas.ConsultationResponse(
        id=consultation.id,
        customer_id=consultation.customer_id,
        advisor_name=advisor.profile.name,
        status="active",
        created_at=consultation.start_time,
    )


@router.get("/{consultation_id}", response_model=schemas.ConsultationDetailResponse)
async def get_consultation(
    consultation_id: str,
    db: Session = Depends(get_db),
):
    """Get consultation details by ID.

    Args:
        consultation_id: UUID of consultation
        db: Database session

    Returns:
        Detailed consultation information
    """
    consultation = get_consultation_or_404(consultation_id, db)

    # Build conversation turns
    conversation_turns = [
        schemas.ConversationTurn(
            role=turn.get("role", "system"),
            content=turn.get("content", ""),
            timestamp=datetime.fromisoformat(turn.get("timestamp", datetime.now(timezone.utc).isoformat())),
            compliance_score=turn.get("compliance_score"),
            compliance_confidence=turn.get("compliance_confidence"),
            compliance_reasoning=turn.get("compliance_reasoning"),
            compliance_issues=turn.get("compliance_issues"),
            compliance_passed=turn.get("compliance_passed"),
            requires_human_review=turn.get("requires_human_review"),
        )
        for turn in consultation.conversation
    ]

    return schemas.ConsultationDetailResponse(
        id=consultation.id,
        customer_id=consultation.customer_id,
        advisor_name=consultation.meta.get("advisor_name", "Sarah"),
        status="completed" if consultation.end_time else "active",
        conversation=conversation_turns,
        outcome=consultation.outcome,
        created_at=consultation.start_time,
        ended_at=consultation.end_time,
    )


@router.get("", response_model=schemas.PaginatedConsultations)
async def list_consultations(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(get_pagination_params),
):
    """List all consultations with pagination.

    Args:
        db: Database session
        pagination: Pagination parameters

    Returns:
        Paginated list of consultations
    """
    # Query consultations
    query = db.query(Consultation).order_by(Consultation.start_time.desc())

    total = query.count()
    consultations = query.offset(pagination.skip).limit(pagination.limit).all()

    # Convert to response models
    items = [
        schemas.ConsultationResponse(
            id=c.id,
            customer_id=c.customer_id,
            advisor_name=c.meta.get("advisor_name", "Sarah"),
            status="completed" if c.end_time else "active",
            created_at=c.start_time,
            ended_at=c.end_time,
        )
        for c in consultations
    ]

    return schemas.PaginatedConsultations(
        items=items,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.post("/{consultation_id}/messages", response_model=schemas.MessageResponse)
async def send_message(
    consultation_id: str,
    request: schemas.SendMessageRequest,
    db: Session = Depends(get_db),
    advisor: AdvisorAgent = Depends(get_advisor_agent),
):
    """Send a customer message (returns acknowledgment).

    The actual advisor response is streamed via the /stream endpoint.

    Args:
        consultation_id: UUID of consultation
        request: Message content
        db: Database session
        advisor: Advisor agent instance

    Returns:
        Message acknowledgment
    """
    consultation = get_consultation_or_404(consultation_id, db)
    verify_consultation_active(consultation)

    # Add customer message to conversation
    message_id = uuid4()
    customer_message = {
        "role": "customer",
        "content": request.content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message_id": str(message_id),
    }

    consultation.conversation.append(customer_message)
    flag_modified(consultation, "conversation")
    db.commit()

    # Extract and record customer observation as memory
    if advisor.memory_stream.session:
        try:
            # Rate the importance of this customer statement
            importance = rate_importance(request.content)

            # Only create memory if importance is above threshold
            if importance > 0.3:
                memory = MemoryNode(
                    description=f"Customer inquiry: {request.content}",
                    importance=importance,
                    memory_type=MemoryType.OBSERVATION,
                    embedding=embed(request.content),
                    timestamp=datetime.fromisoformat(customer_message["timestamp"]),
                )
                advisor.memory_stream.add(memory)
                logger.info(f"Created customer observation memory (importance: {importance:.2f})")
        except Exception as e:
            logger.error(f"Failed to create customer memory: {e}")
            # Don't fail the request if memory creation fails

    return schemas.MessageResponse(
        message_id=message_id,
        status="received",
        timestamp=datetime.now(timezone.utc),
    )


@router.get("/{consultation_id}/stream")
async def stream_guidance(
    consultation_id: str,
    db: Session = Depends(get_db),
    advisor: AdvisorAgent = Depends(get_advisor_agent),
):
    """Stream advisor guidance using Server-Sent Events (SSE).

    This endpoint provides real-time streaming of advisor responses,
    reducing time-to-first-token from 6-8s to 1-2s.

    Args:
        consultation_id: UUID of consultation
        db: Database session
        advisor: Advisor agent instance

    Returns:
        SSE event stream

    SSE Event Format:
        - type: "chunk" - Text chunk during streaming
        - type: "complete" - Streaming completed with compliance score
        - type: "error" - Error occurred
    """
    consultation = get_consultation_or_404(consultation_id, db)
    verify_consultation_active(consultation)

    async def event_generator() -> AsyncIterator[dict]:
        """Generate SSE events from advisor guidance stream."""
        try:
            # Extract the most recent customer message as presenting_question
            latest_customer_message = ""
            for turn in reversed(consultation.conversation):
                if turn.get("role") == "customer":
                    latest_customer_message = turn.get("content", "")
                    break

            # Build customer profile from consultation
            customer = CustomerProfile(
                customer_id=consultation.customer_id,
                demographics=CustomerDemographics(
                    age=consultation.meta.get("customer_age", 50),
                    gender="unknown",
                    location="unknown",
                    employment_status="unknown",
                    financial_literacy="medium",
                ),
                presenting_question=latest_customer_message,
            )

            # Get conversation history (exclude system messages)
            conversation_history = [
                {"role": turn["role"], "content": turn["content"]}
                for turn in consultation.conversation
                if turn.get("role") != "system"
            ]

            # Stream guidance
            guidance_buffer = []

            async for chunk in advisor.provide_guidance_stream(
                customer=customer,
                conversation_history=conversation_history,
            ):
                guidance_buffer.append(chunk)

                # Yield chunk event
                yield {
                    "event": "message",
                    "data": json.dumps(
                        schemas.SSEChunkEvent(content=chunk).model_dump()
                    ),
                }

            # Full guidance text
            full_guidance = "".join(guidance_buffer)

            # Validate compliance (non-blocking, use cached result)
            validation = await advisor._validate_and_record_async(
                guidance=full_guidance,
                customer=customer,
                context=advisor._retrieve_context(customer, conversation_history),
            )

            # Store advisor message in conversation
            advisor_message = {
                "role": "advisor",
                "content": full_guidance,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "compliance_score": validation.confidence,
                "compliance_confidence": validation.confidence,
                "compliance_reasoning": validation.reasoning,
                "compliance_issues": [
                    {
                        "category": issue.issue_type.value,
                        "severity": issue.severity.value,
                        "description": issue.description,
                    }
                    for issue in validation.issues
                ],
                "compliance_passed": validation.passed,
                "requires_human_review": validation.requires_human_review,
            }

            consultation.conversation.append(advisor_message)
            flag_modified(consultation, "conversation")

            # Update compliance scores tracking
            if "compliance_scores" not in consultation.meta:
                consultation.meta["compliance_scores"] = []
            consultation.meta["compliance_scores"].append(validation.confidence)
            flag_modified(consultation, "meta")

            db.commit()

            # Extract and record key insights from advisor response
            if advisor.memory_stream.session and full_guidance:
                try:
                    # Rate importance of the advisor's response
                    importance = rate_importance(full_guidance)

                    # Higher threshold for advisor insights
                    if importance > 0.5:
                        # Truncate long responses for description
                        description = full_guidance[:200]
                        if len(full_guidance) > 200:
                            description += "..."

                        memory = MemoryNode(
                            description=f"Advisor insight: {description}",
                            importance=importance,
                            memory_type=MemoryType.REFLECTION,
                            embedding=embed(full_guidance),
                            timestamp=datetime.fromisoformat(advisor_message["timestamp"]),
                        )
                        advisor.memory_stream.add(memory)
                        logger.info(f"Created advisor insight memory (importance: {importance:.2f})")
                except Exception as e:
                    logger.error(f"Failed to create advisor memory: {e}")
                    # Don't fail the request if memory creation fails

            # Yield completion event
            yield {
                "event": "message",
                "data": json.dumps(
                    schemas.SSECompleteEvent(
                        compliance_score=validation.confidence,
                        compliance_confidence=validation.confidence,
                        full_message=full_guidance,
                    ).model_dump()
                ),
            }

        except Exception as e:
            # Yield error event
            yield {
                "event": "message",
                "data": json.dumps(
                    schemas.SSEErrorEvent(error=str(e)).model_dump()
                ),
            }

    return EventSourceResponse(event_generator())


@router.post("/{consultation_id}/end", response_model=schemas.ConsultationDetailResponse)
async def end_consultation(
    consultation_id: str,
    request: schemas.EndConsultationRequest = None,
    db: Session = Depends(get_db),
    advisor: AdvisorAgent = Depends(get_advisor_agent),
):
    """End an active consultation.

    Args:
        consultation_id: UUID of consultation
        request: Optional satisfaction feedback
        db: Database session
        advisor: Advisor agent instance

    Returns:
        Completed consultation details with outcome
    """
    consultation = get_consultation_or_404(consultation_id, db)
    verify_consultation_active(consultation)

    # Mark as ended
    consultation.end_time = datetime.now(timezone.utc)

    # Calculate duration
    duration = (consultation.end_time - consultation.start_time).total_seconds()
    consultation.duration_seconds = int(duration)

    # Generate outcome (simplified - in production, use outcome evaluator)
    compliance_scores = consultation.meta.get("compliance_scores", [])
    avg_compliance = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0.95

    outcome = {
        "customer_satisfaction": request.customer_satisfaction if request else 8.0,
        "comprehension": 8.5,
        "fca_compliant": avg_compliance >= 0.85,
        "avg_compliance_score": avg_compliance,
        "successful": True,
    }

    consultation.outcome = outcome

    # Calculate conversational quality (Phase 2)
    conversation_history = [
        {"role": turn["role"], "content": turn["content"], "customer_name": consultation.meta.get("customer_name", "")}
        for turn in consultation.conversation
        if turn.get("role") != "system"
    ]

    conversational_quality = await advisor._calculate_conversational_quality(
        conversation_history=conversation_history,
        db=None  # Not needed for current implementation
    )
    consultation.conversational_quality = conversational_quality

    # Calculate and store dialogue patterns
    # Extract advisor messages for pattern analysis
    advisor_messages = [msg["content"] for msg in conversation_history if msg.get("role") == "advisor"]

    if advisor_messages:
        # Count signposting phrases
        signpost_phrases = [
            "let me break this down", "let me explain", "let me help",
            "here's what this means", "here's what", "building on",
            "before we", "first,", "let's explore", "let's look",
            "here's how", "one option", "one approach",
            "some people find", "it's worth", "it depends"
        ]
        signpost_count = sum(
            1 for msg in advisor_messages
            if any(phrase in msg.lower() for phrase in signpost_phrases)
        )

        # Calculate personalization score (name usage)
        customer_name = consultation.meta.get("customer_name", "")
        personalization_score = 0.0
        if customer_name:
            name_usage = sum(1 for msg in advisor_messages if customer_name.lower() in msg.lower())
            expected_usage_rate = len(advisor_messages) / 2
            personalization_score = min(name_usage / expected_usage_rate, 1.0) if expected_usage_rate > 0 else 0.0

        # Calculate engagement score (question usage)
        question_count = sum(msg.count("?") for msg in advisor_messages)
        engagement_score = min(question_count / len(advisor_messages), 1.0) if len(advisor_messages) > 0 else 0.0

        # Store dialogue patterns
        consultation.dialogue_patterns = {
            "signposting_used": signpost_count > 0,
            "personalization_level": "high" if personalization_score > 0.7 else "medium" if personalization_score > 0.4 else "low",
            "engagement_level": "high" if engagement_score > 0.7 else "medium" if engagement_score > 0.4 else "low",
            "signpost_count": signpost_count,
            "personalization_score": personalization_score,
            "engagement_score": engagement_score,
        }

    db.commit()

    # Build response
    conversation_turns = [
        schemas.ConversationTurn(
            role=turn.get("role", "system"),
            content=turn.get("content", ""),
            timestamp=datetime.fromisoformat(turn.get("timestamp", datetime.now(timezone.utc).isoformat())),
            compliance_score=turn.get("compliance_score"),
            compliance_confidence=turn.get("compliance_confidence"),
            compliance_reasoning=turn.get("compliance_reasoning"),
            compliance_issues=turn.get("compliance_issues"),
            compliance_passed=turn.get("compliance_passed"),
            requires_human_review=turn.get("requires_human_review"),
        )
        for turn in consultation.conversation
    ]

    return schemas.ConsultationDetailResponse(
        id=consultation.id,
        customer_id=consultation.customer_id,
        advisor_name=consultation.meta.get("advisor_name", "Sarah"),
        status="completed",
        conversation=conversation_turns,
        outcome=outcome,
        created_at=consultation.start_time,
        ended_at=consultation.end_time,
    )


@router.get("/{consultation_id}/metrics", response_model=schemas.ConsultationMetrics)
async def get_consultation_metrics(
    consultation_id: str,
    db: Session = Depends(get_db),
):
    """Get metrics for a consultation.

    Args:
        consultation_id: UUID of consultation
        db: Database session

    Returns:
        Consultation metrics
    """
    consultation = get_consultation_or_404(consultation_id, db)

    # Calculate metrics
    message_count = len([m for m in consultation.conversation if m.get("role") != "system"])

    compliance_scores = consultation.meta.get("compliance_scores", [])
    avg_compliance = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0.0

    # Duration
    duration_minutes = None
    if consultation.end_time:
        duration = (consultation.end_time - consultation.start_time).total_seconds()
        duration_minutes = duration / 60

    # Outcome metrics
    customer_satisfaction = None
    comprehension = None
    if consultation.outcome:
        customer_satisfaction = consultation.outcome.get("customer_satisfaction")
        comprehension = consultation.outcome.get("comprehension")

    return schemas.ConsultationMetrics(
        message_count=message_count,
        avg_compliance_score=avg_compliance,
        customer_satisfaction=customer_satisfaction,
        comprehension=comprehension,
        duration_minutes=duration_minutes,
    )


@router.get("/{consultation_id}/memories")
async def get_consultation_memories(
    consultation_id: str,
    db: Session = Depends(get_db),
):
    """Get all memories associated with a consultation.

    Debug endpoint to verify memories are being recorded and persisted.
    Returns recent memories from the system to help with troubleshooting.

    Args:
        consultation_id: UUID of consultation
        db: Database session

    Returns:
        List of memory dictionaries with id, description, importance,
        memory_type, timestamp, and access_count

    Raises:
        HTTPException: If consultation not found (404)
    """
    from guidance_agent.core.database import Memory

    # Verify consultation exists
    consultation = get_consultation_or_404(consultation_id, db)

    # Get all memories (for now; later could filter by consultation)
    # Order by most recent first, limit to 50 for debugging
    memories = db.query(Memory).order_by(Memory.timestamp.desc()).limit(50).all()

    return [
        {
            "id": str(m.id),
            "description": m.description,
            "importance": m.importance,
            "memory_type": m.memory_type.value,
            "timestamp": m.timestamp.isoformat(),
            "access_count": 0,  # Access count tracking not yet implemented
        }
        for m in memories
    ]

"""Customer profile API endpoints.

Handles:
- Retrieving customer profiles
- Listing customer consultations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from guidance_agent.api import schemas
from guidance_agent.api.dependencies import get_db
from guidance_agent.core.database import Consultation

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/{customer_id}", response_model=schemas.CustomerProfileResponse)
async def get_customer_profile(
    customer_id: str,
    db: Session = Depends(get_db),
):
    """Get customer profile by ID.

    Aggregates information from all consultations for this customer.

    Args:
        customer_id: UUID of customer
        db: Database session

    Returns:
        Customer profile with consultation history summary

    Raises:
        HTTPException: If customer not found
    """
    # Find all consultations for this customer
    consultations = (
        db.query(Consultation)
        .filter(Consultation.customer_id == customer_id)
        .order_by(Consultation.start_time.asc())
        .all()
    )

    if not consultations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer {customer_id} not found",
        )

    # Extract customer info from first consultation
    first_consultation = consultations[0]
    customer_name = first_consultation.meta.get("customer_name", "Unknown")
    customer_age = first_consultation.meta.get("customer_age", 0)

    # Get consultation times
    first_consultation_time = first_consultation.start_time
    last_consultation_time = consultations[-1].start_time if consultations else None

    return schemas.CustomerProfileResponse(
        customer_id=customer_id,
        name=customer_name,
        age=customer_age,
        consultation_count=len(consultations),
        first_consultation=first_consultation_time,
        last_consultation=last_consultation_time,
    )


@router.get(
    "/{customer_id}/consultations",
    response_model=schemas.CustomerConsultationListResponse,
)
async def list_customer_consultations(
    customer_id: str,
    db: Session = Depends(get_db),
):
    """List all consultations for a customer.

    Args:
        customer_id: UUID of customer
        db: Database session

    Returns:
        List of consultations for this customer

    Raises:
        HTTPException: If customer not found
    """
    # Find all consultations
    consultations = (
        db.query(Consultation)
        .filter(Consultation.customer_id == customer_id)
        .order_by(Consultation.start_time.desc())
        .all()
    )

    if not consultations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No consultations found for customer {customer_id}",
        )

    # Convert to response models
    consultation_list = [
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

    return schemas.CustomerConsultationListResponse(
        consultations=consultation_list,
    )

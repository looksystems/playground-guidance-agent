"""FastAPI dependencies for dependency injection.

Provides reusable dependencies for:
- Database sessions
- Authentication
- Advisor agent instances
- Pagination helpers
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from guidance_agent.core.database import SessionLocal
from guidance_agent.advisor.agent import AdvisorAgent
from guidance_agent.core.types import AdvisorProfile


# --- Database Dependencies ---


def get_db() -> Generator[Session, None, None]:
    """Get database session dependency.

    Yields:
        SQLAlchemy session

    Example:
        @app.get("/consultations")
        def list_consultations(db: Session = Depends(get_db)):
            return db.query(Consultation).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Authentication Dependencies ---


def verify_admin_token(authorization: Optional[str] = Header(None)) -> bool:
    """Verify admin authentication token.

    Args:
        authorization: Authorization header value

    Returns:
        True if authenticated

    Raises:
        HTTPException: If authentication fails

    Note:
        In production, this should validate JWT tokens or API keys.
        For now, we use a simple token check.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid scheme")
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # In production, validate token against database or JWT secret
    # For now, accept a simple admin token
    valid_tokens = ["admin-token", "test-admin-token"]

    if token not in valid_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return True


def get_current_admin(authenticated: bool = Depends(verify_admin_token)) -> bool:
    """Get current admin user (requires authentication).

    Args:
        authenticated: Authentication status from verify_admin_token

    Returns:
        True if authenticated as admin
    """
    return authenticated


# --- Advisor Agent Dependencies ---


def get_advisor_profile() -> AdvisorProfile:
    """Get the default advisor profile.

    Returns:
        AdvisorProfile for Sarah, the pension guidance specialist
    """
    return AdvisorProfile(
        name="Sarah",
        description="Pension guidance specialist with expertise in FCA compliance",
        specialization="pension_consolidation",
        experience_level="senior",
    )


def get_advisor_agent(
    profile: AdvisorProfile = Depends(get_advisor_profile),
    db: Session = Depends(get_db),
) -> AdvisorAgent:
    """Get advisor agent instance.

    Args:
        profile: Advisor profile configuration
        db: Database session for memory persistence

    Returns:
        Configured advisor agent instance with database-backed memory

    Note:
        Creates a new agent instance per request. Memory persistence
        is now enabled via the database session.
    """
    return AdvisorAgent(
        profile=profile,
        session=db,
        use_chain_of_thought=True,
        enable_prompt_caching=True,
    )


# --- Pagination Dependencies ---


class PaginationParams:
    """Pagination parameters for list endpoints."""

    def __init__(
        self,
        skip: int = 0,
        limit: int = 20,
    ):
        """Initialize pagination params.

        Args:
            skip: Number of items to skip (default: 0)
            limit: Maximum number of items to return (default: 20, max: 100)
        """
        self.skip = max(0, skip)
        self.limit = min(100, max(1, limit))


def get_pagination_params(
    skip: int = 0,
    limit: int = 20,
) -> PaginationParams:
    """Get pagination parameters.

    Args:
        skip: Number of items to skip
        limit: Maximum items to return

    Returns:
        PaginationParams object

    Example:
        @app.get("/items")
        def list_items(pagination: PaginationParams = Depends(get_pagination_params)):
            return db.query(Item).offset(pagination.skip).limit(pagination.limit).all()
    """
    return PaginationParams(skip=skip, limit=limit)


# --- Helper Functions ---


def get_consultation_or_404(
    consultation_id: str,
    db: Session,
):
    """Get consultation by ID or raise 404.

    Args:
        consultation_id: UUID of consultation
        db: Database session

    Returns:
        Consultation object

    Raises:
        HTTPException: If consultation not found
    """
    from guidance_agent.core.database import Consultation

    consultation = (
        db.query(Consultation)
        .filter(Consultation.id == consultation_id)
        .first()
    )

    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consultation {consultation_id} not found",
        )

    return consultation


def verify_consultation_active(consultation) -> None:
    """Verify consultation is active (not ended).

    Args:
        consultation: Consultation object

    Raises:
        HTTPException: If consultation is completed
    """
    if consultation.end_time is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consultation has already been completed",
        )

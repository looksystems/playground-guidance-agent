"""Tests for Phase 2 conversational quality fields in Consultation model.

Following TDD approach - these tests define the expected behavior
before implementation. These tests will FAIL until the model is updated.

Phase 2 Requirements:
- Consultation model should have conversational_quality field (Float, nullable, 0-1)
- Consultation model should have dialogue_patterns field (JSONB, nullable)
"""

import pytest
from sqlalchemy.exc import IntegrityError
from uuid import uuid4
from datetime import datetime, timezone

from guidance_agent.core.database import Consultation


@pytest.mark.asyncio
async def test_consultation_has_conversational_quality_field(transactional_db_session):
    """Test that Consultation model has conversational_quality field.

    Field Requirements:
    - Type: Float
    - Nullable: True
    - Range: 0.0 to 1.0
    """
    db = transactional_db_session

    # Create consultation with conversational_quality
    consultation = Consultation(
        id=uuid4(),
        customer_id=uuid4(),
        advisor_id=uuid4(),
        conversation=[
            {
                "role": "customer",
                "content": "Test message",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        ],
        start_time=datetime.now(timezone.utc),
        conversational_quality=0.85  # NEW FIELD
    )

    db.add(consultation)
    db.commit()
    db.refresh(consultation)

    # Verify field exists and has correct value
    assert hasattr(consultation, 'conversational_quality')
    assert consultation.conversational_quality == 0.85


@pytest.mark.asyncio
async def test_consultation_conversational_quality_accepts_float_range(transactional_db_session):
    """Test that conversational_quality accepts values from 0.0 to 1.0."""
    db = transactional_db_session

    test_values = [0.0, 0.25, 0.5, 0.75, 1.0]

    for value in test_values:
        consultation = Consultation(
            id=uuid4(),
            customer_id=uuid4(),
            advisor_id=uuid4(),
            conversation=[{"role": "customer", "content": "Test"}],
            start_time=datetime.now(timezone.utc),
            conversational_quality=value
        )

        db.add(consultation)
        db.commit()
        db.refresh(consultation)

        assert consultation.conversational_quality == value

        # Clean up for next iteration
        db.delete(consultation)
        db.commit()


@pytest.mark.asyncio
async def test_consultation_conversational_quality_is_nullable(transactional_db_session):
    """Test that conversational_quality can be None (nullable)."""
    db = transactional_db_session

    # Create consultation without conversational_quality
    consultation = Consultation(
        id=uuid4(),
        customer_id=uuid4(),
        advisor_id=uuid4(),
        conversation=[{"role": "customer", "content": "Test"}],
        start_time=datetime.now(timezone.utc)
        # No conversational_quality specified
    )

    db.add(consultation)
    db.commit()
    db.refresh(consultation)

    # Should be None by default
    assert consultation.conversational_quality is None


@pytest.mark.asyncio
async def test_consultation_conversational_quality_can_be_set_to_none(transactional_db_session):
    """Test that conversational_quality can be explicitly set to None."""
    db = transactional_db_session

    consultation = Consultation(
        id=uuid4(),
        customer_id=uuid4(),
        advisor_id=uuid4(),
        conversation=[{"role": "customer", "content": "Test"}],
        start_time=datetime.now(timezone.utc),
        conversational_quality=None  # Explicitly None
    )

    db.add(consultation)
    db.commit()
    db.refresh(consultation)

    assert consultation.conversational_quality is None


@pytest.mark.asyncio
async def test_consultation_conversational_quality_can_be_updated(transactional_db_session):
    """Test that conversational_quality can be updated after creation."""
    db = transactional_db_session

    consultation = Consultation(
        id=uuid4(),
        customer_id=uuid4(),
        advisor_id=uuid4(),
        conversation=[{"role": "customer", "content": "Test"}],
        start_time=datetime.now(timezone.utc),
        conversational_quality=0.5
    )

    db.add(consultation)
    db.commit()
    db.refresh(consultation)

    # Update the value
    consultation.conversational_quality = 0.85
    db.commit()
    db.refresh(consultation)

    assert consultation.conversational_quality == 0.85


@pytest.mark.asyncio
async def test_consultation_has_dialogue_patterns_field(transactional_db_session):
    """Test that Consultation model has dialogue_patterns field.

    Field Requirements:
    - Type: JSONB
    - Nullable: True
    """
    db = transactional_db_session

    dialogue_patterns = {
        "signposting_used": True,
        "personalization_level": "high",
        "engagement_level": "medium",
        "effective_phrases": [
            "Let me break this down for you",
            "Here's what this means"
        ]
    }

    consultation = Consultation(
        id=uuid4(),
        customer_id=uuid4(),
        advisor_id=uuid4(),
        conversation=[{"role": "customer", "content": "Test"}],
        start_time=datetime.now(timezone.utc),
        dialogue_patterns=dialogue_patterns  # NEW FIELD
    )

    db.add(consultation)
    db.commit()
    db.refresh(consultation)

    # Verify field exists and has correct value
    assert hasattr(consultation, 'dialogue_patterns')
    assert consultation.dialogue_patterns == dialogue_patterns


@pytest.mark.asyncio
async def test_consultation_dialogue_patterns_is_nullable(transactional_db_session):
    """Test that dialogue_patterns can be None (nullable)."""
    db = transactional_db_session

    consultation = Consultation(
        id=uuid4(),
        customer_id=uuid4(),
        advisor_id=uuid4(),
        conversation=[{"role": "customer", "content": "Test"}],
        start_time=datetime.now(timezone.utc)
        # No dialogue_patterns specified
    )

    db.add(consultation)
    db.commit()
    db.refresh(consultation)

    # Should be None by default
    assert consultation.dialogue_patterns is None


@pytest.mark.asyncio
async def test_consultation_dialogue_patterns_stores_complex_json(transactional_db_session):
    """Test that dialogue_patterns can store complex JSON structures."""
    db = transactional_db_session

    complex_patterns = {
        "signposting_used": True,
        "personalization_level": "high",
        "engagement_level": "medium",
        "effective_phrases": [
            "Let me break this down",
            "Building on what you mentioned"
        ],
        "conversation_phase": "middle",
        "tone_adjustments": {
            "empathy_level": "high",
            "formality": "professional"
        },
        "question_types": ["open-ended", "confirmatory"],
        "transition_count": 5,
        "name_usage_count": 3
    }

    consultation = Consultation(
        id=uuid4(),
        customer_id=uuid4(),
        advisor_id=uuid4(),
        conversation=[{"role": "customer", "content": "Test"}],
        start_time=datetime.now(timezone.utc),
        dialogue_patterns=complex_patterns
    )

    db.add(consultation)
    db.commit()
    db.refresh(consultation)

    # Verify entire complex structure is preserved
    assert consultation.dialogue_patterns == complex_patterns
    assert consultation.dialogue_patterns["signposting_used"] is True
    assert consultation.dialogue_patterns["personalization_level"] == "high"
    assert len(consultation.dialogue_patterns["effective_phrases"]) == 2
    assert consultation.dialogue_patterns["tone_adjustments"]["empathy_level"] == "high"


@pytest.mark.asyncio
async def test_consultation_dialogue_patterns_can_be_updated(transactional_db_session):
    """Test that dialogue_patterns can be updated after creation."""
    db = transactional_db_session

    initial_patterns = {
        "signposting_used": False,
        "engagement_level": "low"
    }

    consultation = Consultation(
        id=uuid4(),
        customer_id=uuid4(),
        advisor_id=uuid4(),
        conversation=[{"role": "customer", "content": "Test"}],
        start_time=datetime.now(timezone.utc),
        dialogue_patterns=initial_patterns
    )

    db.add(consultation)
    db.commit()
    db.refresh(consultation)

    # Update the patterns
    updated_patterns = {
        "signposting_used": True,
        "engagement_level": "high",
        "personalization_level": "medium"
    }

    consultation.dialogue_patterns = updated_patterns
    db.commit()
    db.refresh(consultation)

    assert consultation.dialogue_patterns == updated_patterns


@pytest.mark.asyncio
async def test_consultation_dialogue_patterns_empty_dict(transactional_db_session):
    """Test that dialogue_patterns can be an empty dictionary."""
    db = transactional_db_session

    consultation = Consultation(
        id=uuid4(),
        customer_id=uuid4(),
        advisor_id=uuid4(),
        conversation=[{"role": "customer", "content": "Test"}],
        start_time=datetime.now(timezone.utc),
        dialogue_patterns={}  # Empty dict
    )

    db.add(consultation)
    db.commit()
    db.refresh(consultation)

    assert consultation.dialogue_patterns == {}


@pytest.mark.asyncio
async def test_consultation_both_new_fields_together(transactional_db_session):
    """Test that both conversational_quality and dialogue_patterns work together."""
    db = transactional_db_session

    consultation = Consultation(
        id=uuid4(),
        customer_id=uuid4(),
        advisor_id=uuid4(),
        conversation=[
            {
                "role": "customer",
                "content": "How much should I be saving?",
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            {
                "role": "advisor",
                "content": "Great question! Let me break this down for you...",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        ],
        start_time=datetime.now(timezone.utc),
        conversational_quality=0.85,
        dialogue_patterns={
            "signposting_used": True,
            "personalization_level": "high",
            "engagement_level": "high"
        }
    )

    db.add(consultation)
    db.commit()
    db.refresh(consultation)

    # Verify both fields are stored correctly
    assert consultation.conversational_quality == 0.85
    assert consultation.dialogue_patterns["signposting_used"] is True
    assert consultation.dialogue_patterns["personalization_level"] == "high"


@pytest.mark.asyncio
async def test_consultation_query_by_conversational_quality(transactional_db_session):
    """Test that we can query consultations by conversational_quality."""
    db = transactional_db_session

    # Create consultations with different quality scores
    high_quality = Consultation(
        id=uuid4(),
        customer_id=uuid4(),
        advisor_id=uuid4(),
        conversation=[{"role": "customer", "content": "Test"}],
        start_time=datetime.now(timezone.utc),
        conversational_quality=0.9
    )

    low_quality = Consultation(
        id=uuid4(),
        customer_id=uuid4(),
        advisor_id=uuid4(),
        conversation=[{"role": "customer", "content": "Test"}],
        start_time=datetime.now(timezone.utc),
        conversational_quality=0.3
    )

    no_quality = Consultation(
        id=uuid4(),
        customer_id=uuid4(),
        advisor_id=uuid4(),
        conversation=[{"role": "customer", "content": "Test"}],
        start_time=datetime.now(timezone.utc),
        conversational_quality=None
    )

    db.add_all([high_quality, low_quality, no_quality])
    db.commit()

    # Query for high quality consultations (>0.7)
    high_quality_results = db.query(Consultation).filter(
        Consultation.conversational_quality > 0.7
    ).all()

    assert len(high_quality_results) == 1
    assert high_quality_results[0].id == high_quality.id

    # Query for low quality consultations (<0.5)
    low_quality_results = db.query(Consultation).filter(
        Consultation.conversational_quality < 0.5
    ).all()

    assert len(low_quality_results) == 1
    assert low_quality_results[0].id == low_quality.id


@pytest.mark.asyncio
async def test_consultation_conversational_quality_type_validation(transactional_db_session):
    """Test that conversational_quality validates as a float type."""
    db = transactional_db_session

    # Valid: int should be converted to float
    consultation = Consultation(
        id=uuid4(),
        customer_id=uuid4(),
        advisor_id=uuid4(),
        conversation=[{"role": "customer", "content": "Test"}],
        start_time=datetime.now(timezone.utc),
        conversational_quality=1  # Integer should be acceptable
    )

    db.add(consultation)
    db.commit()
    db.refresh(consultation)

    # Should be converted to float
    assert isinstance(consultation.conversational_quality, (float, int))
    assert consultation.conversational_quality == 1.0

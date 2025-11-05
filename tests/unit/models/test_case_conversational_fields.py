"""Tests for Phase 2 conversational quality fields in Case model.

Following TDD approach - these tests define the expected behavior
before implementation. These tests will FAIL until the model is updated.

Phase 2 Requirements:
- Case model should have dialogue_techniques field (JSONB, nullable)
"""

import pytest
from uuid import uuid4
from datetime import datetime, timezone

from guidance_agent.core.database import Case


@pytest.mark.asyncio
async def test_case_has_dialogue_techniques_field(transactional_db_session):
    """Test that Case model has dialogue_techniques field.

    Field Requirements:
    - Type: JSONB
    - Nullable: True
    """
    db = transactional_db_session

    dialogue_techniques = {
        "successful_patterns": [
            "Used signposting effectively",
            "Natural transitions between topics"
        ],
        "effective_phrases": [
            "Let me break this down for you",
            "Building on what you mentioned"
        ],
        "engagement_approach": "high",
        "personalization_style": "high"
    }

    case = Case(
        id=uuid4(),
        task_type="pension_consolidation",
        customer_situation="Customer has 3 pensions from previous employers",
        guidance_provided="Explained consolidation benefits and process",
        outcome={"customer_satisfaction": 9.0},
        dialogue_techniques=dialogue_techniques  # NEW FIELD
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    # Verify field exists and has correct value
    assert hasattr(case, 'dialogue_techniques')
    assert case.dialogue_techniques == dialogue_techniques


@pytest.mark.asyncio
async def test_case_dialogue_techniques_is_nullable(transactional_db_session):
    """Test that dialogue_techniques can be None (nullable)."""
    db = transactional_db_session

    case = Case(
        id=uuid4(),
        task_type="pension_consolidation",
        customer_situation="Customer has 3 pensions",
        guidance_provided="Explained benefits",
        outcome={"customer_satisfaction": 8.5}
        # No dialogue_techniques specified
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    # Should be None by default
    assert case.dialogue_techniques is None


@pytest.mark.asyncio
async def test_case_dialogue_techniques_stores_complex_json(transactional_db_session):
    """Test that dialogue_techniques can store complex JSON structures."""
    db = transactional_db_session

    complex_techniques = {
        "successful_patterns": [
            "Acknowledged customer anxiety early",
            "Used name 3 times naturally",
            "Provided clear signposting for complex topics",
            "Asked confirmatory questions to check understanding"
        ],
        "effective_phrases": [
            "Let me break this down for you, Sarah",
            "Great question - here's what this means for your situation",
            "Building on what you mentioned about retirement goals",
            "Before we move on, let's make sure this makes sense"
        ],
        "engagement_approach": "high",
        "personalization_style": "high",
        "conversation_phases": ["opening", "middle", "closing"],
        "tone_adjustments": {
            "empathy_level": "high",
            "formality": "professional-friendly",
            "pacing": "moderate"
        },
        "metrics": {
            "signpost_count": 5,
            "name_usage_count": 3,
            "question_count": 7,
            "transition_phrases": 4
        }
    }

    case = Case(
        id=uuid4(),
        task_type="pension_drawdown",
        customer_situation="Customer aged 58 considering early retirement",
        guidance_provided="Discussed drawdown strategies and tax implications",
        outcome={
            "customer_satisfaction": 9.5,
            "comprehension": 9.0
        },
        dialogue_techniques=complex_techniques
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    # Verify entire complex structure is preserved
    assert case.dialogue_techniques == complex_techniques
    assert len(case.dialogue_techniques["successful_patterns"]) == 4
    assert len(case.dialogue_techniques["effective_phrases"]) == 4
    assert case.dialogue_techniques["engagement_approach"] == "high"
    assert case.dialogue_techniques["tone_adjustments"]["empathy_level"] == "high"
    assert case.dialogue_techniques["metrics"]["signpost_count"] == 5


@pytest.mark.asyncio
async def test_case_dialogue_techniques_can_be_updated(transactional_db_session):
    """Test that dialogue_techniques can be updated after creation."""
    db = transactional_db_session

    initial_techniques = {
        "successful_patterns": ["Pattern 1"],
        "engagement_approach": "medium"
    }

    case = Case(
        id=uuid4(),
        task_type="pension_consolidation",
        customer_situation="Customer has multiple pensions",
        guidance_provided="Basic consolidation guidance",
        outcome={"customer_satisfaction": 7.0},
        dialogue_techniques=initial_techniques
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    # Update the techniques
    updated_techniques = {
        "successful_patterns": ["Pattern 1", "Pattern 2", "Pattern 3"],
        "engagement_approach": "high",
        "personalization_style": "high",
        "effective_phrases": [
            "Let me explain this",
            "Here's what this means"
        ]
    }

    case.dialogue_techniques = updated_techniques
    db.commit()
    db.refresh(case)

    assert case.dialogue_techniques == updated_techniques
    assert len(case.dialogue_techniques["successful_patterns"]) == 3


@pytest.mark.asyncio
async def test_case_dialogue_techniques_empty_dict(transactional_db_session):
    """Test that dialogue_techniques can be an empty dictionary."""
    db = transactional_db_session

    case = Case(
        id=uuid4(),
        task_type="pension_transfer",
        customer_situation="Customer considering DB to DC transfer",
        guidance_provided="Explained risks and requirements",
        outcome={"customer_satisfaction": 8.0},
        dialogue_techniques={}  # Empty dict
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    assert case.dialogue_techniques == {}


@pytest.mark.asyncio
async def test_case_dialogue_techniques_with_existing_fields(transactional_db_session):
    """Test that dialogue_techniques works alongside existing Case fields."""
    db = transactional_db_session

    case = Case(
        id=uuid4(),
        task_type="pension_consolidation",
        customer_situation="Customer has 4 pensions from old jobs, wants simplification",
        guidance_provided="Explained consolidation process, benefits, and potential fees",
        outcome={
            "customer_satisfaction": 9.0,
            "comprehension": 8.5,
            "decision_made": True,
            "follow_up_required": False
        },
        embedding=[0.1] * 1536,  # Mock embedding vector
        meta={
            "consultation_id": str(uuid4()),
            "duration_minutes": 35,
            "customer_age": 52
        },
        dialogue_techniques={
            "successful_patterns": [
                "Clear signposting throughout",
                "Used customer name naturally"
            ],
            "effective_phrases": [
                "Let me break this down for you, John",
                "Here's what this means for your situation"
            ],
            "engagement_approach": "high",
            "personalization_style": "high"
        }
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    # Verify all fields are stored correctly
    assert case.task_type == "pension_consolidation"
    assert case.outcome["customer_satisfaction"] == 9.0
    assert case.meta["duration_minutes"] == 35
    assert case.dialogue_techniques["engagement_approach"] == "high"
    assert len(case.dialogue_techniques["successful_patterns"]) == 2


@pytest.mark.asyncio
async def test_case_query_by_dialogue_techniques_presence(transactional_db_session):
    """Test that we can query cases based on dialogue_techniques presence."""
    db = transactional_db_session

    # Create case with dialogue techniques
    case_with_techniques = Case(
        id=uuid4(),
        task_type="pension_consolidation",
        customer_situation="Test situation",
        guidance_provided="Test guidance",
        outcome={"customer_satisfaction": 9.0},
        dialogue_techniques={
            "successful_patterns": ["Pattern 1"],
            "engagement_approach": "high"
        }
    )

    # Create case without dialogue techniques
    case_without_techniques = Case(
        id=uuid4(),
        task_type="pension_drawdown",
        customer_situation="Test situation",
        guidance_provided="Test guidance",
        outcome={"customer_satisfaction": 8.0},
        dialogue_techniques=None
    )

    db.add_all([case_with_techniques, case_without_techniques])
    db.commit()

    # Query for cases with dialogue techniques
    cases_with_techniques = db.query(Case).filter(
        Case.dialogue_techniques.isnot(None)
    ).all()

    assert len(cases_with_techniques) == 1
    assert cases_with_techniques[0].id == case_with_techniques.id

    # Query for cases without dialogue techniques
    cases_without_techniques = db.query(Case).filter(
        Case.dialogue_techniques.is_(None)
    ).all()

    assert len(cases_without_techniques) == 1
    assert cases_without_techniques[0].id == case_without_techniques.id


@pytest.mark.asyncio
async def test_case_dialogue_techniques_json_querying(transactional_db_session):
    """Test that we can query JSON fields within dialogue_techniques.

    This tests JSONB querying capabilities - filtering by nested JSON values.
    """
    db = transactional_db_session

    # Create cases with different engagement approaches
    high_engagement = Case(
        id=uuid4(),
        task_type="pension_consolidation",
        customer_situation="Test",
        guidance_provided="Test",
        outcome={"customer_satisfaction": 9.0},
        dialogue_techniques={"engagement_approach": "high"}
    )

    medium_engagement = Case(
        id=uuid4(),
        task_type="pension_drawdown",
        customer_situation="Test",
        guidance_provided="Test",
        outcome={"customer_satisfaction": 8.0},
        dialogue_techniques={"engagement_approach": "medium"}
    )

    db.add_all([high_engagement, medium_engagement])
    db.commit()

    # Query for high engagement cases using JSONB operator
    high_engagement_cases = db.query(Case).filter(
        Case.dialogue_techniques['engagement_approach'].astext == 'high'
    ).all()

    assert len(high_engagement_cases) == 1
    assert high_engagement_cases[0].id == high_engagement.id


@pytest.mark.asyncio
async def test_case_dialogue_techniques_with_array_fields(transactional_db_session):
    """Test that dialogue_techniques can store and retrieve array fields."""
    db = transactional_db_session

    techniques_with_arrays = {
        "successful_patterns": [
            "Pattern 1",
            "Pattern 2",
            "Pattern 3"
        ],
        "effective_phrases": [
            "Phrase 1",
            "Phrase 2"
        ],
        "conversation_phases": ["opening", "middle", "closing"]
    }

    case = Case(
        id=uuid4(),
        task_type="pension_consolidation",
        customer_situation="Test",
        guidance_provided="Test",
        outcome={"customer_satisfaction": 9.0},
        dialogue_techniques=techniques_with_arrays
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    # Verify arrays are preserved
    assert len(case.dialogue_techniques["successful_patterns"]) == 3
    assert case.dialogue_techniques["successful_patterns"][0] == "Pattern 1"
    assert len(case.dialogue_techniques["effective_phrases"]) == 2
    assert case.dialogue_techniques["conversation_phases"] == ["opening", "middle", "closing"]


@pytest.mark.asyncio
async def test_case_dialogue_techniques_supports_nested_dicts(transactional_db_session):
    """Test that dialogue_techniques supports nested dictionary structures."""
    db = transactional_db_session

    nested_techniques = {
        "tone_adjustments": {
            "empathy_level": "high",
            "formality": "professional",
            "pacing": "moderate"
        },
        "metrics": {
            "signpost_count": 5,
            "name_usage_count": 3,
            "question_count": 7
        }
    }

    case = Case(
        id=uuid4(),
        task_type="pension_drawdown",
        customer_situation="Test",
        guidance_provided="Test",
        outcome={"customer_satisfaction": 9.0},
        dialogue_techniques=nested_techniques
    )

    db.add(case)
    db.commit()
    db.refresh(case)

    # Verify nested structure is preserved
    assert case.dialogue_techniques["tone_adjustments"]["empathy_level"] == "high"
    assert case.dialogue_techniques["metrics"]["signpost_count"] == 5
    assert isinstance(case.dialogue_techniques["tone_adjustments"], dict)
    assert isinstance(case.dialogue_techniques["metrics"], dict)


@pytest.mark.asyncio
async def test_case_retrieve_multiple_cases_with_dialogue_techniques(transactional_db_session):
    """Test retrieving multiple cases with different dialogue techniques."""
    db = transactional_db_session

    # Create multiple cases with different techniques
    cases_data = [
        {
            "task_type": "pension_consolidation",
            "dialogue_techniques": {
                "engagement_approach": "high",
                "personalization_style": "high"
            }
        },
        {
            "task_type": "pension_drawdown",
            "dialogue_techniques": {
                "engagement_approach": "medium",
                "personalization_style": "high"
            }
        },
        {
            "task_type": "pension_transfer",
            "dialogue_techniques": None
        }
    ]

    cases = []
    for data in cases_data:
        case = Case(
            id=uuid4(),
            task_type=data["task_type"],
            customer_situation="Test",
            guidance_provided="Test",
            outcome={"customer_satisfaction": 8.0},
            dialogue_techniques=data["dialogue_techniques"]
        )
        cases.append(case)
        db.add(case)

    db.commit()

    # Retrieve all cases
    retrieved_cases = db.query(Case).all()
    assert len(retrieved_cases) == 3

    # Verify each case has correct dialogue_techniques
    consolidation_case = next(c for c in retrieved_cases if c.task_type == "pension_consolidation")
    assert consolidation_case.dialogue_techniques["engagement_approach"] == "high"

    drawdown_case = next(c for c in retrieved_cases if c.task_type == "pension_drawdown")
    assert drawdown_case.dialogue_techniques["engagement_approach"] == "medium"

    transfer_case = next(c for c in retrieved_cases if c.task_type == "pension_transfer")
    assert transfer_case.dialogue_techniques is None

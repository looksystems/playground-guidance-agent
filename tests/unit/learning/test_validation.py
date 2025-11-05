"""Unit tests for rule validation and confidence adjustment."""

import pytest
from uuid import uuid4
from datetime import datetime

from tests.fixtures.embeddings import EMBEDDING_DIMENSION as EMBEDDING_DIM

from guidance_agent.learning.validation import (
    update_rule_confidence,
    track_rule_performance,
    adjust_confidence_on_success,
    adjust_confidence_on_failure,
    get_rule_performance_metrics,
)
from guidance_agent.core.types import OutcomeResult, OutcomeStatus
from guidance_agent.retrieval.retriever import RulesBase
from guidance_agent.core.database import Rule, get_session


@pytest.fixture
def db_session(transactional_db_session):
    """Get a test database session with automatic rollback.

    Uses the transactional_db_session fixture from conftest.py
    which automatically rolls back all changes after each test.
    """
    return transactional_db_session


@pytest.fixture
def rules_base(db_session):
    """Create a rules base for testing."""
    return RulesBase(session=db_session)


@pytest.fixture
def sample_rule(rules_base, db_session):
    """Create a sample rule for testing."""
    rule_id = uuid4()
    rules_base.add(
        id=rule_id,
        embedding=[0.1] * EMBEDDING_DIM,
        metadata={
            "principle": "Always explain pension transfer risks before benefits",
            "domain": "risk_disclosure",
            "confidence": 0.70,
            "supporting_evidence": [],
        },
    )

    # Retrieve the rule
    rule = db_session.query(Rule).filter(Rule.id == rule_id).first()
    return rule


@pytest.fixture
def successful_outcome():
    """Create a successful outcome."""
    return OutcomeResult(
        status=OutcomeStatus.SUCCESS,
        successful=True,
        customer_satisfaction=9.0,
        comprehension=8.5,
        goal_alignment=9.0,
    )


@pytest.fixture
def failed_outcome():
    """Create a failed outcome."""
    return OutcomeResult(
        status=OutcomeStatus.FAILURE,
        successful=False,
        customer_satisfaction=3.0,
        comprehension=4.0,
        goal_alignment=2.0,
    )


class TestUpdateRuleConfidence:
    """Tests for update_rule_confidence function."""

    def test_update_confidence_basic(self, sample_rule, db_session):
        """Test basic confidence update."""
        original_confidence = sample_rule.confidence

        new_confidence = update_rule_confidence(
            rule=sample_rule, new_confidence=0.85, session=db_session
        )

        assert new_confidence == 0.85
        assert sample_rule.confidence == 0.85
        assert new_confidence != original_confidence

    def test_update_confidence_enforces_bounds(self, sample_rule, db_session):
        """Test that confidence is bounded between 0 and 1."""
        # Test upper bound
        new_confidence = update_rule_confidence(
            rule=sample_rule, new_confidence=1.5, session=db_session
        )
        assert new_confidence == 1.0

        # Test lower bound
        new_confidence = update_rule_confidence(
            rule=sample_rule, new_confidence=-0.5, session=db_session
        )
        assert new_confidence == 0.0

    def test_update_confidence_persists(self, sample_rule, db_session):
        """Test that confidence update persists to database."""
        rule_id = sample_rule.id

        update_rule_confidence(rule=sample_rule, new_confidence=0.92, session=db_session)

        # Refresh from database
        db_session.expire(sample_rule)
        updated_rule = db_session.query(Rule).filter(Rule.id == rule_id).first()

        assert updated_rule.confidence == 0.92


class TestAdjustConfidenceOnSuccess:
    """Tests for adjust_confidence_on_success function."""

    def test_adjust_on_success_increases_confidence(self, sample_rule, successful_outcome, db_session):
        """Test that successful outcome increases confidence."""
        original_confidence = sample_rule.confidence

        new_confidence = adjust_confidence_on_success(
            rule=sample_rule, outcome=successful_outcome, session=db_session
        )

        assert new_confidence > original_confidence

    def test_adjust_on_success_caps_at_one(self, sample_rule, successful_outcome, db_session):
        """Test that confidence doesn't exceed 1.0."""
        # Set high initial confidence
        sample_rule.confidence = 0.98

        new_confidence = adjust_confidence_on_success(
            rule=sample_rule, outcome=successful_outcome, session=db_session
        )

        assert new_confidence <= 1.0

    def test_adjust_on_success_considers_outcome_quality(self, sample_rule, db_session):
        """Test that adjustment magnitude depends on outcome quality."""
        # High quality outcome
        high_quality_outcome = OutcomeResult(
            successful=True,
            customer_satisfaction=10.0,
            comprehension=10.0,
            goal_alignment=10.0,
        )

        original_confidence = sample_rule.confidence
        new_confidence_high = adjust_confidence_on_success(
            rule=sample_rule, outcome=high_quality_outcome, session=db_session
        )

        # Reset
        sample_rule.confidence = original_confidence

        # Lower quality outcome
        low_quality_outcome = OutcomeResult(
            successful=True,
            customer_satisfaction=6.0,
            comprehension=6.0,
            goal_alignment=6.0,
        )

        new_confidence_low = adjust_confidence_on_success(
            rule=sample_rule, outcome=low_quality_outcome, session=db_session
        )

        # High quality should increase confidence more
        assert (new_confidence_high - original_confidence) > (new_confidence_low - original_confidence)


class TestAdjustConfidenceOnFailure:
    """Tests for adjust_confidence_on_failure function."""

    def test_adjust_on_failure_decreases_confidence(self, sample_rule, failed_outcome, db_session):
        """Test that failed outcome decreases confidence."""
        original_confidence = sample_rule.confidence

        new_confidence = adjust_confidence_on_failure(
            rule=sample_rule, outcome=failed_outcome, session=db_session
        )

        assert new_confidence < original_confidence

    def test_adjust_on_failure_floors_at_zero(self, sample_rule, failed_outcome, db_session):
        """Test that confidence doesn't go below 0.0."""
        # Set low initial confidence
        sample_rule.confidence = 0.05

        new_confidence = adjust_confidence_on_failure(
            rule=sample_rule, outcome=failed_outcome, session=db_session
        )

        assert new_confidence >= 0.0


class TestTrackRulePerformance:
    """Tests for track_rule_performance function."""

    def test_track_performance_basic(self, sample_rule, successful_outcome, db_session):
        """Test basic performance tracking."""
        rule_ids = [str(sample_rule.id)]

        track_rule_performance(
            rule_ids=rule_ids,
            outcome=successful_outcome,
            session=db_session,
        )

        # Check that metadata was updated
        db_session.expire(sample_rule)
        updated_rule = db_session.query(Rule).filter(Rule.id == sample_rule.id).first()

        assert "performance" in updated_rule.meta
        assert updated_rule.meta["performance"]["uses"] == 1
        assert updated_rule.meta["performance"]["successes"] == 1

    def test_track_performance_accumulates(self, sample_rule, successful_outcome, failed_outcome, db_session):
        """Test that performance tracking accumulates over multiple consultations."""
        rule_ids = [str(sample_rule.id)]

        # Track success
        track_rule_performance(rule_ids, successful_outcome, db_session)

        # Track another success
        track_rule_performance(rule_ids, successful_outcome, db_session)

        # Track failure
        track_rule_performance(rule_ids, failed_outcome, db_session)

        # Check accumulated stats
        db_session.expire(sample_rule)
        updated_rule = db_session.query(Rule).filter(Rule.id == sample_rule.id).first()

        assert updated_rule.meta["performance"]["uses"] == 3
        assert updated_rule.meta["performance"]["successes"] == 2
        assert updated_rule.meta["performance"]["failures"] == 1

    def test_track_performance_multiple_rules(self, rules_base, successful_outcome, db_session):
        """Test tracking performance for multiple rules."""
        # Create two rules
        rule_id1 = uuid4()
        rule_id2 = uuid4()

        rules_base.add(
            id=rule_id1,
            embedding=[0.1] * EMBEDDING_DIM,
            metadata={
                "principle": "Rule 1",
                "domain": "test",
                "confidence": 0.7,
                "supporting_evidence": [],
            },
        )

        rules_base.add(
            id=rule_id2,
            embedding=[0.2] * EMBEDDING_DIM,
            metadata={
                "principle": "Rule 2",
                "domain": "test",
                "confidence": 0.7,
                "supporting_evidence": [],
            },
        )

        # Track performance for both
        rule_ids = [str(rule_id1), str(rule_id2)]
        track_rule_performance(rule_ids, successful_outcome, db_session)

        # Check both were updated
        rule1 = db_session.query(Rule).filter(Rule.id == rule_id1).first()
        rule2 = db_session.query(Rule).filter(Rule.id == rule_id2).first()

        assert rule1.meta["performance"]["uses"] == 1
        assert rule2.meta["performance"]["uses"] == 1


class TestGetRulePerformanceMetrics:
    """Tests for get_rule_performance_metrics function."""

    def test_get_metrics_basic(self, sample_rule, successful_outcome, db_session):
        """Test getting performance metrics."""
        rule_ids = [str(sample_rule.id)]

        # Add some performance data
        track_rule_performance(rule_ids, successful_outcome, db_session)
        track_rule_performance(rule_ids, successful_outcome, db_session)

        # Get metrics
        metrics = get_rule_performance_metrics(sample_rule)

        assert "uses" in metrics
        assert "successes" in metrics
        assert "failures" in metrics
        assert "success_rate" in metrics
        assert metrics["uses"] == 2
        assert metrics["successes"] == 2
        assert metrics["success_rate"] == 1.0

    def test_get_metrics_calculates_success_rate(self, sample_rule, successful_outcome, failed_outcome, db_session):
        """Test that success rate is calculated correctly."""
        rule_ids = [str(sample_rule.id)]

        # 3 successes, 1 failure = 75% success rate
        track_rule_performance(rule_ids, successful_outcome, db_session)
        track_rule_performance(rule_ids, successful_outcome, db_session)
        track_rule_performance(rule_ids, successful_outcome, db_session)
        track_rule_performance(rule_ids, failed_outcome, db_session)

        metrics = get_rule_performance_metrics(sample_rule)

        assert metrics["uses"] == 4
        assert metrics["successes"] == 3
        assert metrics["failures"] == 1
        assert metrics["success_rate"] == 0.75

    def test_get_metrics_no_data(self, sample_rule):
        """Test getting metrics for rule with no performance data."""
        metrics = get_rule_performance_metrics(sample_rule)

        assert metrics["uses"] == 0
        assert metrics["successes"] == 0
        assert metrics["failures"] == 0
        assert metrics["success_rate"] == 0.0

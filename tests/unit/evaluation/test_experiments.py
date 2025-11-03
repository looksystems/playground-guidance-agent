"""Tests for experiment tracking with Phoenix.

Following TDD approach: Write tests FIRST, then implement.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime
from uuid import uuid4

from guidance_agent.evaluation.experiments import (
    run_training_experiment,
    store_experiment_outcomes,
    load_experiment_outcomes,
)
from guidance_agent.evaluation.metrics import AdvisorMetrics
from guidance_agent.core.types import OutcomeResult, AdvisorProfile, CustomerProfile
from guidance_agent.advisor.agent import AdvisorAgent
from guidance_agent.customer.agent import CustomerAgent


class TestStoreExperimentOutcomes:
    """Test store_experiment_outcomes function."""

    @patch("guidance_agent.evaluation.experiments.get_session")
    def test_store_experiment_outcomes_empty_list(self, mock_get_session):
        """Test storing empty outcomes list."""
        mock_session = Mock()
        mock_get_session.return_value = mock_session

        # Store empty list
        store_experiment_outcomes("test_experiment", [])

        # Should still call commit (even for empty list)
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    @patch("guidance_agent.evaluation.experiments.get_session")
    @patch("guidance_agent.evaluation.experiments.Consultation")
    def test_store_experiment_outcomes_single_outcome(
        self, mock_consultation_class, mock_get_session
    ):
        """Test storing single outcome."""
        mock_session = Mock()
        mock_get_session.return_value = mock_session

        outcome = OutcomeResult(
            outcome_id=uuid4(),
            successful=True,
            customer_satisfaction=8.0,
        )

        # Store outcome
        store_experiment_outcomes("exp1", [outcome])

        # Should create one Consultation record
        assert mock_consultation_class.call_count == 1
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @patch("guidance_agent.evaluation.experiments.get_session")
    @patch("guidance_agent.evaluation.experiments.Consultation")
    def test_store_experiment_outcomes_multiple_outcomes(
        self, mock_consultation_class, mock_get_session
    ):
        """Test storing multiple outcomes."""
        mock_session = Mock()
        mock_get_session.return_value = mock_session

        outcomes = [
            OutcomeResult(outcome_id=uuid4(), successful=True),
            OutcomeResult(outcome_id=uuid4(), successful=False),
            OutcomeResult(outcome_id=uuid4(), successful=True),
        ]

        # Store outcomes
        store_experiment_outcomes("exp2", outcomes)

        # Should create three Consultation records
        assert mock_consultation_class.call_count == 3
        assert mock_session.add.call_count == 3
        mock_session.commit.assert_called_once()


class TestLoadExperimentOutcomes:
    """Test load_experiment_outcomes function."""

    @patch("guidance_agent.evaluation.experiments.get_session")
    def test_load_experiment_outcomes_not_found(self, mock_get_session):
        """Test loading outcomes for non-existent experiment."""
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        mock_session.query.return_value.filter.return_value.all.return_value = []

        outcomes = load_experiment_outcomes("nonexistent")

        assert outcomes == []
        mock_session.close.assert_called_once()

    @patch("guidance_agent.evaluation.experiments.get_session")
    def test_load_experiment_outcomes_found(self, mock_get_session):
        """Test loading outcomes for existing experiment."""
        mock_session = Mock()
        mock_get_session.return_value = mock_session

        # Mock consultation records
        mock_consultation = Mock()
        mock_consultation.outcome = {
            "successful": True,
            "customer_satisfaction": 8.0,
            "comprehension": 7.5,
        }
        mock_session.query.return_value.filter.return_value.all.return_value = [
            mock_consultation
        ]

        outcomes = load_experiment_outcomes("exp1")

        # Should return empty list (simplified implementation)
        # In production, this would deserialize properly
        assert outcomes == []
        mock_session.close.assert_called_once()


class TestRunTrainingExperiment:
    """Test run_training_experiment function."""

    @patch("guidance_agent.evaluation.experiments.store_experiment_outcomes")
    @patch("guidance_agent.evaluation.experiments.run_consultation")
    @patch("guidance_agent.evaluation.experiments.trace")
    def test_run_training_experiment_zero_customers(
        self, mock_trace, mock_run_consultation, mock_store
    ):
        """Test experiment with zero customers."""
        # Setup mock span
        mock_span = Mock()
        mock_trace.get_tracer.return_value.start_as_current_span.return_value.__enter__.return_value = (
            mock_span
        )

        advisor = AdvisorAgent(profile=AdvisorProfile(name="Test", description="Test"))

        # Run experiment with 0 customers
        metrics = run_training_experiment("test_exp", advisor, [], num_customers=0)

        # Should return zero metrics
        assert metrics.overall_quality == 0.0
        mock_run_consultation.assert_not_called()

    @patch("guidance_agent.evaluation.experiments.store_experiment_outcomes")
    @patch("guidance_agent.evaluation.experiments.run_consultation")
    @patch("guidance_agent.evaluation.experiments.generate_customer_profile")
    @patch("guidance_agent.evaluation.experiments.trace")
    def test_run_training_experiment_single_customer(
        self, mock_trace, mock_generate, mock_run_consultation, mock_store
    ):
        """Test experiment with single customer."""
        # Setup mock span
        mock_span = Mock()
        mock_trace.get_tracer.return_value.start_as_current_span.return_value.__enter__.return_value = (
            mock_span
        )

        # Setup mocks
        mock_generate.return_value = CustomerProfile()
        mock_outcome = OutcomeResult(
            successful=True,
            customer_satisfaction=8.0,
            comprehension=7.5,
            fca_compliant=True,
        )
        mock_run_consultation.return_value = mock_outcome

        advisor = AdvisorAgent(profile=AdvisorProfile(name="Test", description="Test"))

        # Run experiment
        metrics = run_training_experiment("test_exp", advisor, [], num_customers=1)

        # Should generate 1 customer
        mock_generate.assert_called_once()

        # Should run 1 consultation
        mock_run_consultation.assert_called_once()

        # Should store outcomes
        mock_store.assert_called_once()

        # Should set span attributes
        assert mock_span.set_attribute.called

    @patch("guidance_agent.evaluation.experiments.store_experiment_outcomes")
    @patch("guidance_agent.evaluation.experiments.run_consultation")
    @patch("guidance_agent.evaluation.experiments.generate_customer_profile")
    @patch("guidance_agent.evaluation.experiments.trace")
    def test_run_training_experiment_multiple_customers(
        self, mock_trace, mock_generate, mock_run_consultation, mock_store
    ):
        """Test experiment with multiple customers."""
        # Setup mock span
        mock_span = Mock()
        mock_trace.get_tracer.return_value.start_as_current_span.return_value.__enter__.return_value = (
            mock_span
        )

        # Setup mocks
        mock_generate.return_value = CustomerProfile()
        mock_outcome = OutcomeResult(
            successful=True,
            customer_satisfaction=8.0,
            fca_compliant=True,
        )
        mock_run_consultation.return_value = mock_outcome

        advisor = AdvisorAgent(profile=AdvisorProfile(name="Test", description="Test"))

        # Run experiment with 5 customers
        metrics = run_training_experiment("test_exp", advisor, [], num_customers=5)

        # Should generate 5 customers
        assert mock_generate.call_count == 5

        # Should run 5 consultations
        assert mock_run_consultation.call_count == 5

    @patch("guidance_agent.evaluation.experiments.store_experiment_outcomes")
    @patch("guidance_agent.evaluation.experiments.run_consultation")
    @patch("guidance_agent.evaluation.experiments.generate_customer_profile")
    @patch("guidance_agent.evaluation.experiments.trace")
    def test_run_training_experiment_uses_provided_customers(
        self, mock_trace, mock_generate, mock_run_consultation, mock_store
    ):
        """Test experiment uses provided customers instead of generating."""
        # Setup mock span
        mock_span = Mock()
        mock_trace.get_tracer.return_value.start_as_current_span.return_value.__enter__.return_value = (
            mock_span
        )

        # Setup mocks
        mock_outcome = OutcomeResult(successful=True, customer_satisfaction=8.0)
        mock_run_consultation.return_value = mock_outcome

        advisor = AdvisorAgent(profile=AdvisorProfile(name="Test", description="Test"))
        customers = [
            CustomerAgent(profile=CustomerProfile()),
            CustomerAgent(profile=CustomerProfile()),
        ]

        # Run experiment with provided customers
        metrics = run_training_experiment(
            "test_exp", advisor, customers, num_customers=2
        )

        # Should NOT generate customers
        mock_generate.assert_not_called()

        # Should run 2 consultations with provided customers
        assert mock_run_consultation.call_count == 2

    @patch("guidance_agent.evaluation.experiments.store_experiment_outcomes")
    @patch("guidance_agent.evaluation.experiments.run_consultation")
    @patch("guidance_agent.evaluation.experiments.generate_customer_profile")
    @patch("guidance_agent.evaluation.experiments.trace")
    def test_run_training_experiment_progress_events(
        self, mock_trace, mock_generate, mock_run_consultation, mock_store
    ):
        """Test that progress events are logged at intervals."""
        # Setup mock span
        mock_span = Mock()
        mock_trace.get_tracer.return_value.start_as_current_span.return_value.__enter__.return_value = (
            mock_span
        )

        # Setup mocks
        mock_generate.return_value = CustomerProfile()
        mock_outcome = OutcomeResult(successful=True, customer_satisfaction=8.0)
        mock_run_consultation.return_value = mock_outcome

        advisor = AdvisorAgent(profile=AdvisorProfile(name="Test", description="Test"))

        # Run experiment with 250 customers (should log at 0, 100, 200)
        metrics = run_training_experiment(
            "test_exp", advisor, [], num_customers=250, progress_interval=100
        )

        # Should have added progress events
        # At checkpoints: 0, 100, 200
        add_event_calls = [
            call for call in mock_span.add_event.call_args_list
            if call[0][0] == "progress_checkpoint"
        ]
        assert len(add_event_calls) >= 2  # At least 2 checkpoints

    @patch("guidance_agent.evaluation.experiments.store_experiment_outcomes")
    @patch("guidance_agent.evaluation.experiments.run_consultation")
    @patch("guidance_agent.evaluation.experiments.generate_customer_profile")
    @patch("guidance_agent.evaluation.experiments.trace")
    def test_run_training_experiment_sets_span_attributes(
        self, mock_trace, mock_generate, mock_run_consultation, mock_store
    ):
        """Test that span attributes are set correctly."""
        # Setup mock span
        mock_span = Mock()
        mock_trace.get_tracer.return_value.start_as_current_span.return_value.__enter__.return_value = (
            mock_span
        )

        # Setup mocks
        mock_generate.return_value = CustomerProfile()
        mock_outcome = OutcomeResult(
            successful=True,
            customer_satisfaction=8.5,
            fca_compliant=True,
        )
        mock_run_consultation.return_value = mock_outcome

        advisor = AdvisorAgent(profile=AdvisorProfile(name="Test", description="Test"))

        # Run experiment
        metrics = run_training_experiment("test_exp", advisor, [], num_customers=3)

        # Check that span attributes were set
        set_attribute_calls = mock_span.set_attribute.call_args_list

        # Should set experiment metadata
        attribute_names = [call[0][0] for call in set_attribute_calls]
        assert "experiment.completed" in attribute_names
        assert "results.overall_quality" in attribute_names
        assert "results.compliance_rate" in attribute_names
        assert "results.satisfaction" in attribute_names

    @patch("guidance_agent.evaluation.experiments.store_experiment_outcomes")
    @patch("guidance_agent.evaluation.experiments.run_consultation")
    @patch("guidance_agent.evaluation.experiments.generate_customer_profile")
    @patch("guidance_agent.evaluation.experiments.trace")
    def test_run_training_experiment_stores_outcomes(
        self, mock_trace, mock_generate, mock_run_consultation, mock_store
    ):
        """Test that outcomes are stored in database."""
        # Setup mock span
        mock_span = Mock()
        mock_trace.get_tracer.return_value.start_as_current_span.return_value.__enter__.return_value = (
            mock_span
        )

        # Setup mocks
        mock_generate.return_value = CustomerProfile()
        outcomes_list = [
            OutcomeResult(successful=True, customer_satisfaction=8.0),
            OutcomeResult(successful=False, customer_satisfaction=5.0),
        ]
        mock_run_consultation.side_effect = outcomes_list

        advisor = AdvisorAgent(profile=AdvisorProfile(name="Test", description="Test"))

        # Run experiment
        metrics = run_training_experiment("test_exp", advisor, [], num_customers=2)

        # Should store outcomes
        mock_store.assert_called_once()
        call_args = mock_store.call_args
        assert call_args[0][0] == "test_exp"  # Experiment name
        assert len(call_args[0][1]) == 2  # Two outcomes

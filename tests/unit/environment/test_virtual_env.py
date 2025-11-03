"""Unit tests for VirtualEnvironment."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from guidance_agent.environment.virtual_env import VirtualEnvironment, TrainingMetrics
from guidance_agent.environment.time_manager import VirtualTimeManager
from guidance_agent.environment.orchestrator import EventOrchestrator, ConsultationResult
from guidance_agent.advisor.agent import AdvisorAgent
from guidance_agent.customer.generator import generate_customer_profile
from guidance_agent.compliance.validator import ValidationResult
from guidance_agent.core.types import (
    AdvisorProfile,
    CustomerProfile,
    OutcomeResult,
    OutcomeStatus,
)


class TestVirtualEnvironment:
    """Test virtual training environment."""

    @pytest.fixture
    def advisor_profile(self):
        """Create an advisor profile."""
        return AdvisorProfile(
            name="Sarah",
            description="Pension guidance specialist",
        )

    def test_environment_initialization(self, advisor_profile):
        """Test environment initializes correctly."""
        env = VirtualEnvironment(
            advisor_profile=advisor_profile,
            acceleration_factor=60,
        )

        assert env.advisor is not None
        assert env.time_manager is not None
        assert env.orchestrator is not None
        assert env.metrics is not None

    def test_environment_with_custom_parameters(self, advisor_profile):
        """Test environment with custom parameters."""
        env = VirtualEnvironment(
            advisor_profile=advisor_profile,
            acceleration_factor=100,
            max_turns_per_consultation=15,
        )

        assert env.time_manager.acceleration_factor == 100
        assert env.orchestrator.max_turns == 15

    def test_get_metrics(self, advisor_profile):
        """Test getting training metrics."""
        env = VirtualEnvironment(advisor_profile=advisor_profile)

        metrics = env.get_metrics()

        assert isinstance(metrics, TrainingMetrics)
        assert metrics.total_consultations == 0
        assert metrics.successful_consultations == 0

    def test_run_single_consultation(self, advisor_profile):
        """Test running a single consultation."""
        with patch("guidance_agent.customer.generator.completion") as mock_gen, \
             patch("guidance_agent.advisor.agent.completion") as mock_advisor, \
             patch("guidance_agent.customer.agent.completion") as mock_customer, \
             patch("guidance_agent.customer.simulator.completion") as mock_outcome, \
             patch("guidance_agent.environment.virtual_env.learn_from_successful_consultation") as mock_learn:

            env = VirtualEnvironment(advisor_profile=advisor_profile)

            # Mock customer generation
            mock_gen.side_effect = [
                Mock(choices=[Mock(message=Mock(content='{"gender": "F", "location": "London", "employment_status": "employed", "occupation": "teacher", "financial_literacy": "medium"}'))]),
                Mock(choices=[Mock(message=Mock(content='{"annual_income": 35000, "total_assets": 45000, "total_debt": 5000, "dependents": 0, "risk_tolerance": "medium"}'))]),
                Mock(choices=[Mock(message=Mock(content='{"pot_id": "pot1", "provider": "NEST", "pot_type": "defined_contribution", "current_value": 15000, "projected_value": 25000, "age_accessible": 55, "is_db_scheme": false, "db_guaranteed_amount": null}'))]),
                Mock(choices=[Mock(message=Mock(content='{"goals": "Understand my pension", "presenting_question": "How much should I save?"}'))]),
            ]

            # Mock advisor
            mock_advisor.return_value = Mock(choices=[Mock(message=Mock(content="Good question!"))])

            # Mock customer
            mock_customer.side_effect = [
                Mock(choices=[Mock(message=Mock(content='{"understanding_level": "fully_understood", "confusion_points": [], "customer_feeling": "satisfied"}'))]),
                Mock(choices=[Mock(message=Mock(content="Thank you!"))]),
            ]

            # Mock outcome (successful)
            mock_outcome.return_value = Mock(
                choices=[Mock(message=Mock(content='{"customer_satisfaction": 8.5, "comprehension": 9.0, "goal_alignment": 8.5, "risks_identified": true, "guidance_appropriate": true, "fca_compliant": true, "understanding_checked": true, "signposted_when_needed": false, "has_db_pension": false, "db_warning_given": false, "reasoning": "Success"}'))]
            )

            with patch.object(env.advisor.compliance_validator, "validate") as mock_validate:
                mock_validate.return_value = ValidationResult(passed=True, confidence=0.95, requires_human_review=False, issues=[], reasoning="OK")

                result = env.run_single_consultation()

                assert result is not None
                assert isinstance(result, ConsultationResult)
                assert result.outcome.successful is True
                assert mock_learn.called  # Verify learning was triggered

    def test_run_training_session(self, advisor_profile):
        """Test running a training session with multiple consultations."""
        with patch("guidance_agent.customer.generator.completion") as mock_gen, \
             patch("guidance_agent.advisor.agent.completion") as mock_advisor, \
             patch("guidance_agent.customer.agent.completion") as mock_customer, \
             patch("guidance_agent.customer.simulator.completion") as mock_outcome, \
             patch("guidance_agent.environment.virtual_env.learn_from_successful_consultation") as mock_learn:

            env = VirtualEnvironment(advisor_profile=advisor_profile)

            # Mock customer generation (will be called 3 times)
            mock_gen.side_effect = [
                # Customer 1
                Mock(choices=[Mock(message=Mock(content='{"gender": "F", "location": "London", "employment_status": "employed", "occupation": "teacher", "financial_literacy": "medium"}'))]),
                Mock(choices=[Mock(message=Mock(content='{"annual_income": 35000, "total_assets": 45000, "total_debt": 5000, "dependents": 0, "risk_tolerance": "medium"}'))]),
                Mock(choices=[Mock(message=Mock(content='{"pot_id": "pot1", "provider": "NEST", "pot_type": "defined_contribution", "current_value": 15000, "projected_value": 25000, "age_accessible": 55, "is_db_scheme": false, "db_guaranteed_amount": null}'))]),
                Mock(choices=[Mock(message=Mock(content='{"goals": "Goal 1", "presenting_question": "Question 1"}'))]),
                # Customer 2
                Mock(choices=[Mock(message=Mock(content='{"gender": "M", "location": "Manchester", "employment_status": "employed", "occupation": "engineer", "financial_literacy": "high"}'))]),
                Mock(choices=[Mock(message=Mock(content='{"annual_income": 45000, "total_assets": 60000, "total_debt": 8000, "dependents": 1, "risk_tolerance": "high"}'))]),
                Mock(choices=[Mock(message=Mock(content='{"pot_id": "pot2", "provider": "Aviva", "pot_type": "defined_contribution", "current_value": 25000, "projected_value": 35000, "age_accessible": 55, "is_db_scheme": false, "db_guaranteed_amount": null}'))]),
                Mock(choices=[Mock(message=Mock(content='{"goals": "Goal 2", "presenting_question": "Question 2"}'))]),
                # Customer 3
                Mock(choices=[Mock(message=Mock(content='{"gender": "F", "location": "Edinburgh", "employment_status": "self-employed", "occupation": "consultant", "financial_literacy": "low"}'))]),
                Mock(choices=[Mock(message=Mock(content='{"annual_income": 30000, "total_assets": 35000, "total_debt": 3000, "dependents": 0, "risk_tolerance": "low"}'))]),
                Mock(choices=[Mock(message=Mock(content='{"pot_id": "pot3", "provider": "Scottish Widows", "pot_type": "defined_contribution", "current_value": 10000, "projected_value": 15000, "age_accessible": 55, "is_db_scheme": false, "db_guaranteed_amount": null}'))]),
                Mock(choices=[Mock(message=Mock(content='{"goals": "Goal 3", "presenting_question": "Question 3"}'))]),
            ]

            # Mock advisor (will be called 3 times)
            mock_advisor.return_value = Mock(choices=[Mock(message=Mock(content="Response"))])

            # Mock customer (will be called 6 times - 2 per consultation)
            mock_customer.side_effect = [
                Mock(choices=[Mock(message=Mock(content='{"understanding_level": "fully_understood", "confusion_points": [], "customer_feeling": "satisfied"}'))]),
                Mock(choices=[Mock(message=Mock(content="Thanks!"))]),
            ] * 3

            # Mock outcomes (3 consultations)
            mock_outcome.side_effect = [
                Mock(choices=[Mock(message=Mock(content='{"customer_satisfaction": 8.5, "comprehension": 9.0, "goal_alignment": 8.5, "risks_identified": true, "guidance_appropriate": true, "fca_compliant": true, "understanding_checked": true, "signposted_when_needed": false, "has_db_pension": false, "db_warning_given": false, "reasoning": "Success"}'))]),
                Mock(choices=[Mock(message=Mock(content='{"customer_satisfaction": 8.0, "comprehension": 8.0, "goal_alignment": 8.0, "risks_identified": true, "guidance_appropriate": true, "fca_compliant": true, "understanding_checked": true, "signposted_when_needed": false, "has_db_pension": false, "db_warning_given": false, "reasoning": "Success"}'))]),
                Mock(choices=[Mock(message=Mock(content='{"customer_satisfaction": 7.5, "comprehension": 7.5, "goal_alignment": 7.5, "risks_identified": true, "guidance_appropriate": true, "fca_compliant": true, "understanding_checked": true, "signposted_when_needed": false, "has_db_pension": false, "db_warning_given": false, "reasoning": "Success"}'))]),
            ]

            with patch.object(env.advisor.compliance_validator, "validate") as mock_validate:
                mock_validate.return_value = ValidationResult(passed=True, confidence=0.95, requires_human_review=False, issues=[], reasoning="OK")

                env.run_training_session(num_consultations=3)

                metrics = env.get_metrics()
                assert metrics.total_consultations == 3
                assert metrics.successful_consultations == 3
                assert metrics.success_rate == 1.0

    def test_metrics_tracking(self, advisor_profile):
        """Test that metrics are tracked correctly."""
        env = VirtualEnvironment(advisor_profile=advisor_profile)

        # Manually update metrics
        env.metrics.total_consultations = 10
        env.metrics.successful_consultations = 8
        env.metrics.total_satisfaction = 85.0
        env.metrics.total_comprehension = 82.5
        env.metrics.compliance_violations = 0

        metrics = env.get_metrics()
        assert metrics.total_consultations == 10
        assert metrics.successful_consultations == 8
        assert metrics.success_rate == 0.8
        assert metrics.avg_satisfaction == 8.5
        assert metrics.avg_comprehension == 8.25
        assert metrics.compliance_rate == 1.0

    def test_learning_integration_on_success(self, advisor_profile):
        """Test that successful consultations trigger learning."""
        env = VirtualEnvironment(advisor_profile=advisor_profile)

        # Create mock successful outcome
        mock_outcome = OutcomeResult(
            status=OutcomeStatus.SUCCESS,
            successful=True,
            customer_satisfaction=9.0,
            comprehension=9.0,
            goal_alignment=9.0,
            risks_identified=True,
            guidance_appropriate=True,
            fca_compliant=True,
            understanding_checked=True,
            signposted_when_needed=False,
            has_db_pension=False,
            db_warning_given=False,
            reasoning="Excellent consultation",
        )

        # Mock profile and conversation history
        mock_profile = MagicMock()
        mock_profile.presenting_question = "Test question"
        mock_profile.pensions = []

        mock_conversation = [
            {"role": "customer", "content": "Test question"},
            {"role": "advisor", "content": "Test guidance"},
        ]

        # Should call learn_from_successful_consultation
        with patch("guidance_agent.environment.virtual_env.learn_from_successful_consultation") as mock_learn_success:
            env._process_outcome(mock_profile, mock_conversation, mock_outcome)
            assert mock_learn_success.called

    def test_time_advancement(self, advisor_profile):
        """Test that virtual time advances during training."""
        env = VirtualEnvironment(advisor_profile=advisor_profile, acceleration_factor=60)

        start_time = env.time_manager.get_virtual_time()

        # Advance time (simulate consultation duration)
        env.time_manager.advance(hours=0.5)  # 30 minutes real time

        end_time = env.time_manager.get_virtual_time()

        # Should have advanced by 30 virtual hours
        delta_hours = (end_time - start_time).total_seconds() / 3600
        assert delta_hours == pytest.approx(30.0, rel=0.01)

    def test_progress_display(self, advisor_profile, capsys):
        """Test progress display during training."""
        env = VirtualEnvironment(advisor_profile=advisor_profile)

        env._display_progress(
            current=50,
            total=100,
            success_rate=0.85,
            avg_satisfaction=8.5,
            compliance_rate=1.0,
        )

        captured = capsys.readouterr()
        assert "50/100" in captured.out or "50" in captured.out
        assert "85" in captured.out  # Success rate

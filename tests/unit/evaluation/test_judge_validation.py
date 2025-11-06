"""Tests for LLM-as-judge validation.

Following TDD approach: Write tests FIRST, then implement.
"""

import pytest
from unittest.mock import Mock, patch
from dataclasses import dataclass

from guidance_agent.evaluation.judge_validation import (
    ValidationReport,
    validate_llm_judges,
    calculate_cohens_kappa,
    calculate_fn_rate,
    calculate_fp_rate,
    analyse_confidence_calibration,
)


@dataclass
class ExpertLabeledConsultation:
    """Mock expert-labeled consultation for testing."""

    consultation_id: str
    transcript: str
    expert_label: bool
    expert_confidence: float
    expert_reasoning: str


class TestValidationReport:
    """Test ValidationReport dataclass."""

    def test_validation_report_creation(self):
        """Test creating ValidationReport instance."""
        report = ValidationReport(
            total_consultations=100,
            agreement_rate=0.85,
            cohens_kappa=0.82,
            false_negative_rate=0.02,
            false_positive_rate=0.08,
            confidence_calibration={"mean_error": 0.05},
        )

        assert report.total_consultations == 100
        assert report.agreement_rate == 0.85
        assert report.cohens_kappa == 0.82
        assert report.false_negative_rate == 0.02
        assert report.false_positive_rate == 0.08
        assert report.confidence_calibration == {"mean_error": 0.05}


class TestCalculateCohensKappa:
    """Test calculate_cohens_kappa function."""

    def test_calculate_cohens_kappa_perfect_agreement(self):
        """Test kappa with perfect agreement."""
        results = [
            {"expert_label": True, "judge_consensus": True, "agreement": True},
            {"expert_label": False, "judge_consensus": False, "agreement": True},
            {"expert_label": True, "judge_consensus": True, "agreement": True},
        ]

        kappa = calculate_cohens_kappa(results)

        # Perfect agreement should give kappa = 1.0
        assert kappa == pytest.approx(1.0)

    def test_calculate_cohens_kappa_no_agreement(self):
        """Test kappa with no agreement (random)."""
        results = [
            {"expert_label": True, "judge_consensus": False, "agreement": False},
            {"expert_label": False, "judge_consensus": True, "agreement": False},
            {"expert_label": True, "judge_consensus": False, "agreement": False},
            {"expert_label": False, "judge_consensus": True, "agreement": False},
        ]

        kappa = calculate_cohens_kappa(results)

        # No agreement should give kappa close to 0 or negative
        assert kappa <= 0.1

    def test_calculate_cohens_kappa_partial_agreement(self):
        """Test kappa with partial agreement."""
        results = [
            {"expert_label": True, "judge_consensus": True, "agreement": True},
            {"expert_label": True, "judge_consensus": False, "agreement": False},
            {"expert_label": False, "judge_consensus": False, "agreement": True},
            {"expert_label": False, "judge_consensus": False, "agreement": True},
        ]

        kappa = calculate_cohens_kappa(results)

        # Partial agreement should give kappa between 0 and 1
        assert 0.0 < kappa < 1.0


class TestCalculateFnRate:
    """Test calculate_fn_rate (false negative rate) function."""

    def test_calculate_fn_rate_no_false_negatives(self):
        """Test FN rate with no false negatives."""
        results = [
            {"expert_label": True, "judge_consensus": True},  # True positive
            {"expert_label": True, "judge_consensus": True},  # True positive
            {"expert_label": False, "judge_consensus": False},  # True negative
        ]

        fn_rate = calculate_fn_rate(results)

        # No false negatives
        assert fn_rate == 0.0

    def test_calculate_fn_rate_with_false_negatives(self):
        """Test FN rate with some false negatives."""
        results = [
            {"expert_label": True, "judge_consensus": True},  # True positive
            {"expert_label": True, "judge_consensus": False},  # FALSE NEGATIVE
            {"expert_label": True, "judge_consensus": True},  # True positive
            {"expert_label": True, "judge_consensus": False},  # FALSE NEGATIVE
        ]

        fn_rate = calculate_fn_rate(results)

        # 2 false negatives out of 4 positive cases
        assert fn_rate == 0.5

    def test_calculate_fn_rate_no_positives(self):
        """Test FN rate when there are no positive cases."""
        results = [
            {"expert_label": False, "judge_consensus": False},
            {"expert_label": False, "judge_consensus": False},
        ]

        fn_rate = calculate_fn_rate(results)

        # No positive cases, so FN rate is 0
        assert fn_rate == 0.0


class TestCalculateFpRate:
    """Test calculate_fp_rate (false positive rate) function."""

    def test_calculate_fp_rate_no_false_positives(self):
        """Test FP rate with no false positives."""
        results = [
            {"expert_label": False, "judge_consensus": False},  # True negative
            {"expert_label": False, "judge_consensus": False},  # True negative
            {"expert_label": True, "judge_consensus": True},  # True positive
        ]

        fp_rate = calculate_fp_rate(results)

        # No false positives
        assert fp_rate == 0.0

    def test_calculate_fp_rate_with_false_positives(self):
        """Test FP rate with some false positives."""
        results = [
            {"expert_label": False, "judge_consensus": False},  # True negative
            {"expert_label": False, "judge_consensus": True},  # FALSE POSITIVE
            {"expert_label": False, "judge_consensus": False},  # True negative
            {"expert_label": False, "judge_consensus": True},  # FALSE POSITIVE
        ]

        fp_rate = calculate_fp_rate(results)

        # 2 false positives out of 4 negative cases
        assert fp_rate == 0.5

    def test_calculate_fp_rate_no_negatives(self):
        """Test FP rate when there are no negative cases."""
        results = [
            {"expert_label": True, "judge_consensus": True},
            {"expert_label": True, "judge_consensus": True},
        ]

        fp_rate = calculate_fp_rate(results)

        # No negative cases, so FP rate is 0
        assert fp_rate == 0.0


class TestAnalyseConfidenceCalibration:
    """Test analyse_confidence_calibration function."""

    def test_analyse_confidence_calibration_perfect(self):
        """Test calibration with perfect confidence alignment."""
        results = [
            {
                "expert_confidence": 0.9,
                "judge_confidence": 0.9,
                "agreement": True,
            },
            {
                "expert_confidence": 0.8,
                "judge_confidence": 0.8,
                "agreement": True,
            },
        ]

        calibration = analyse_confidence_calibration(results)

        # Perfect calibration
        assert calibration["mean_error"] == pytest.approx(0.0)

    def test_analyse_confidence_calibration_with_errors(self):
        """Test calibration with some errors."""
        results = [
            {
                "expert_confidence": 0.9,
                "judge_confidence": 0.7,  # 0.2 error
                "agreement": True,
            },
            {
                "expert_confidence": 0.6,
                "judge_confidence": 0.8,  # 0.2 error
                "agreement": True,
            },
        ]

        calibration = analyse_confidence_calibration(results)

        # Mean absolute error should be 0.2
        assert calibration["mean_error"] == pytest.approx(0.2)

    def test_analyse_confidence_calibration_includes_rmse(self):
        """Test that calibration includes RMSE metric."""
        results = [
            {"expert_confidence": 0.9, "judge_confidence": 0.7, "agreement": True},
            {"expert_confidence": 0.6, "judge_confidence": 0.8, "agreement": True},
        ]

        calibration = analyse_confidence_calibration(results)

        # Should include RMSE
        assert "rmse" in calibration
        assert calibration["rmse"] > 0


class TestValidateLLMJudges:
    """Test validate_llm_judges function."""

    @patch("guidance_agent.evaluation.judge_validation.LLMJudge")
    def test_validate_llm_judges_empty_list(self, mock_judge_class):
        """Test validation with empty consultation list."""
        report = validate_llm_judges([])

        # Should return report with zeros
        assert report.total_consultations == 0
        assert report.agreement_rate == 0.0

    @patch("guidance_agent.evaluation.judge_validation.LLMJudge")
    def test_validate_llm_judges_single_consultation(self, mock_judge_class):
        """Test validation with single consultation."""
        # Setup mock judge
        mock_judge = Mock()
        mock_judge.evaluate.return_value = {
            "passed": True,
            "confidence": 0.9,
            "reasoning": "Test",
        }
        mock_judge_class.return_value = mock_judge

        # Expert labeled consultation
        consultation = ExpertLabeledConsultation(
            consultation_id="test1",
            transcript="Customer asked about pensions...",
            expert_label=True,
            expert_confidence=0.9,
            expert_reasoning="Compliant guidance provided",
        )

        report = validate_llm_judges([consultation])

        # Should have 1 consultation
        assert report.total_consultations == 1

        # Should have perfect agreement (both True)
        assert report.agreement_rate == 1.0

    @patch("guidance_agent.evaluation.judge_validation.LLMJudge")
    def test_validate_llm_judges_uses_multiple_judges(self, mock_judge_class):
        """Test that validation uses multiple judge models."""
        # Setup mock judge
        mock_judge = Mock()
        mock_judge.evaluate.return_value = {
            "passed": True,
            "confidence": 0.9,
            "reasoning": "Test",
        }
        mock_judge_class.return_value = mock_judge

        consultation = ExpertLabeledConsultation(
            consultation_id="test1",
            transcript="Test",
            expert_label=True,
            expert_confidence=0.9,
            expert_reasoning="Test",
        )

        report = validate_llm_judges([consultation])

        # Should create 3 judges (gpt-4, claude, gpt-4-v2)
        assert mock_judge_class.call_count == 3

    @patch("guidance_agent.evaluation.judge_validation.LLMJudge")
    def test_validate_llm_judges_computes_consensus(self, mock_judge_class):
        """Test that validation computes consensus across judges."""
        # Setup mock judges with different results
        mock_judge = Mock()
        mock_judge.evaluate.side_effect = [
            {"passed": True, "confidence": 0.9, "reasoning": "Test1"},
            {"passed": True, "confidence": 0.8, "reasoning": "Test2"},
            {"passed": False, "confidence": 0.6, "reasoning": "Test3"},
        ]
        mock_judge_class.return_value = mock_judge

        consultation = ExpertLabeledConsultation(
            consultation_id="test1",
            transcript="Test",
            expert_label=True,
            expert_confidence=0.9,
            expert_reasoning="Test",
        )

        report = validate_llm_judges([consultation])

        # Consensus should be computed (2/3 say True, so consensus is True)
        # Agreement should be True (consensus matches expert)
        assert report.total_consultations == 1

    @patch("guidance_agent.evaluation.judge_validation.LLMJudge")
    def test_validate_llm_judges_realistic_scenario(self, mock_judge_class):
        """Test validation with realistic mixed results."""
        # Setup mock judge with varying results
        mock_judge = Mock()

        # For each consultation, return 3 judge results (one per judge model)
        # Consultation 1: all agree True (expert: True) - agreement
        # Consultation 2: all agree False (expert: False) - agreement
        # Consultation 3: majority True (expert: False) - disagreement (FP)
        # Consultation 4: majority False (expert: True) - disagreement (FN)
        mock_judge.evaluate.side_effect = [
            # Consultation 1
            {"passed": True, "confidence": 0.9, "reasoning": "T1"},
            {"passed": True, "confidence": 0.85, "reasoning": "T2"},
            {"passed": True, "confidence": 0.88, "reasoning": "T3"},
            # Consultation 2
            {"passed": False, "confidence": 0.7, "reasoning": "T4"},
            {"passed": False, "confidence": 0.75, "reasoning": "T5"},
            {"passed": False, "confidence": 0.72, "reasoning": "T6"},
            # Consultation 3 (FP)
            {"passed": True, "confidence": 0.6, "reasoning": "T7"},
            {"passed": True, "confidence": 0.65, "reasoning": "T8"},
            {"passed": False, "confidence": 0.5, "reasoning": "T9"},
            # Consultation 4 (FN)
            {"passed": False, "confidence": 0.55, "reasoning": "T10"},
            {"passed": False, "confidence": 0.6, "reasoning": "T11"},
            {"passed": True, "confidence": 0.5, "reasoning": "T12"},
        ]
        mock_judge_class.return_value = mock_judge

        consultations = [
            ExpertLabeledConsultation(
                consultation_id="c1",
                transcript="Good",
                expert_label=True,
                expert_confidence=0.9,
                expert_reasoning="Good",
            ),
            ExpertLabeledConsultation(
                consultation_id="c2",
                transcript="Bad",
                expert_label=False,
                expert_confidence=0.8,
                expert_reasoning="Bad",
            ),
            ExpertLabeledConsultation(
                consultation_id="c3",
                transcript="Bad but judges say good",
                expert_label=False,
                expert_confidence=0.7,
                expert_reasoning="Violation",
            ),
            ExpertLabeledConsultation(
                consultation_id="c4",
                transcript="Good but judges say bad",
                expert_label=True,
                expert_confidence=0.85,
                expert_reasoning="Compliant",
            ),
        ]

        report = validate_llm_judges(consultations)

        # 4 consultations
        assert report.total_consultations == 4

        # Agreement on 2/4 = 50%
        assert report.agreement_rate == 0.5

        # Should have computed kappa, FN, FP rates
        assert report.cohens_kappa >= 0
        assert 0 <= report.false_negative_rate <= 1
        assert 0 <= report.false_positive_rate <= 1

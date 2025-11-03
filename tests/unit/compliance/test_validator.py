"""Tests for compliance validator."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from guidance_agent.core.types import (
    CustomerProfile,
    CustomerDemographics,
    FinancialSituation,
    PensionPot,
)
from guidance_agent.compliance.validator import (
    ComplianceValidator,
    ValidationResult,
    ValidationIssue,
    IssueType,
    IssueSeverity,
)


class TestValidationIssue:
    """Tests for ValidationIssue dataclass."""

    def test_create_validation_issue(self):
        """Test creating a validation issue."""
        issue = ValidationIssue(
            issue_type=IssueType.ADVICE_BOUNDARY,
            severity=IssueSeverity.HIGH,
            description="Guidance crossed into advice territory",
            suggestion="Rephrase to maintain guidance boundary",
        )

        assert issue.issue_type == IssueType.ADVICE_BOUNDARY
        assert issue.severity == IssueSeverity.HIGH
        assert "advice territory" in issue.description
        assert issue.suggestion is not None

    def test_validation_issue_defaults(self):
        """Test validation issue with defaults."""
        issue = ValidationIssue(
            issue_type=IssueType.RISK_DISCLOSURE,
            severity=IssueSeverity.MEDIUM,
            description="Missing risk disclosure",
        )

        assert issue.issue_type == IssueType.RISK_DISCLOSURE
        assert issue.severity == IssueSeverity.MEDIUM
        assert issue.suggestion is None


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_create_passing_validation_result(self):
        """Test creating a passing validation result."""
        result = ValidationResult(
            passed=True,
            confidence=0.95,
            issues=[],
            requires_human_review=False,
            reasoning="All FCA requirements met",
        )

        assert result.passed is True
        assert result.confidence == 0.95
        assert len(result.issues) == 0
        assert result.requires_human_review is False

    def test_create_failing_validation_result(self):
        """Test creating a failing validation result."""
        issues = [
            ValidationIssue(
                issue_type=IssueType.ADVICE_BOUNDARY,
                severity=IssueSeverity.HIGH,
                description="Crossed into advice",
            )
        ]

        result = ValidationResult(
            passed=False,
            confidence=0.30,
            issues=issues,
            requires_human_review=True,
            reasoning="Guidance crossed advice boundary",
        )

        assert result.passed is False
        assert result.confidence == 0.30
        assert len(result.issues) == 1
        assert result.requires_human_review is True

    def test_validation_result_borderline_case(self):
        """Test validation result for borderline case (medium confidence)."""
        result = ValidationResult(
            passed=True,
            confidence=0.65,
            issues=[],
            requires_human_review=True,
            reasoning="Borderline case - confidence not high enough",
        )

        assert result.passed is True
        assert result.confidence == 0.65
        assert result.requires_human_review is True  # Due to medium confidence


class TestComplianceValidator:
    """Tests for ComplianceValidator class."""

    @pytest.fixture
    def validator(self):
        """Create a validator instance."""
        return ComplianceValidator()

    @pytest.fixture
    def simple_customer(self):
        """Create a simple customer profile."""
        return CustomerProfile(
            demographics=CustomerDemographics(
                age=55,
                gender="M",
                location="London",
                employment_status="employed",
                financial_literacy="medium",
            ),
            financial=FinancialSituation(
                annual_income=50000,
                total_assets=200000,
                total_debt=10000,
                dependents=0,
                risk_tolerance="medium",
            ),
            pensions=[
                PensionPot(
                    pot_id="pot1",
                    provider="Provider A",
                    pot_type="defined_contribution",
                    current_value=100000,
                    projected_value=120000,
                    age_accessible=55,
                )
            ],
            goals="Understanding my pension withdrawal options",
        )

    def test_create_validator(self, validator):
        """Test creating a ComplianceValidator."""
        assert validator is not None
        assert hasattr(validator, "validate")

    def test_validate_compliant_guidance(self, validator, simple_customer):
        """Test validation of compliant guidance."""
        guidance = """
        I can help you understand your pension withdrawal options.

        With your defined contribution pension, you have several options available
        from age 55. These include taking a tax-free lump sum (typically 25%),
        purchasing an annuity, or entering drawdown.

        Each option has different implications for your income, tax, and flexibility.
        Have you considered which of these options might align with your goals?
        """

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            # Mock LLM response indicating compliance
            mock_completion.return_value = MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content="""
                            ANALYSIS:
                            1. Guidance vs Advice boundary: PASS - Stays within guidance, no specific recommendations
                            2. Risk disclosure: PASS - Mentions different implications
                            3. Clear and not misleading: PASS - Uses plain language
                            4. Understanding verification: PASS - Asks question to check understanding
                            5. Signposting: N/A - Not needed for this query

                            OVERALL: PASS
                            CONFIDENCE: 0.92
                            ISSUES: None
                            """
                        )
                    )
                ]
            )

            result = validator.validate(
                guidance=guidance,
                customer=simple_customer,
                reasoning="Customer asking about withdrawal options",
            )

        assert result.passed is True
        assert result.confidence >= 0.85
        assert len(result.issues) == 0
        assert result.requires_human_review is False

    def test_validate_advice_boundary_violation(self, validator, simple_customer):
        """Test detection of advice boundary violation."""
        guidance = """
        You should definitely take the 25% lump sum and invest it in stocks.
        This is the best option for someone in your situation.
        """

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            # Mock LLM response indicating advice boundary violation
            mock_completion.return_value = MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content="""
                            ANALYSIS:
                            1. Guidance vs Advice boundary: FAIL - Uses "should" and makes specific recommendation
                            2. Risk disclosure: FAIL - No risks mentioned
                            3. Clear and not misleading: PASS
                            4. Understanding verification: FAIL - No check
                            5. Signposting: FAIL - Should signpost to regulated advisor

                            OVERALL: FAIL
                            CONFIDENCE: 0.95
                            ISSUES: Advice boundary violation, Missing risk disclosure
                            """
                        )
                    )
                ]
            )

            result = validator.validate(
                guidance=guidance,
                customer=simple_customer,
                reasoning="Customer asking about withdrawal options",
            )

        assert result.passed is False
        assert result.confidence >= 0.85
        assert len(result.issues) >= 1
        # Check for advice boundary issue
        advice_issues = [
            i for i in result.issues if i.issue_type == IssueType.ADVICE_BOUNDARY
        ]
        assert len(advice_issues) >= 1
        assert advice_issues[0].severity == IssueSeverity.HIGH

    def test_validate_missing_risk_disclosure(self, validator, simple_customer):
        """Test detection of missing risk disclosure."""
        guidance = """
        Taking your pension as a lump sum is straightforward. You just need to
        contact your provider and they'll arrange it.
        """

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            # Mock LLM response indicating missing risk disclosure
            mock_completion.return_value = MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content="""
                            ANALYSIS:
                            1. Guidance vs Advice boundary: PASS
                            2. Risk disclosure: FAIL - No mention of tax implications or other risks
                            3. Clear and not misleading: PASS
                            4. Understanding verification: FAIL
                            5. Signposting: PASS

                            OVERALL: FAIL
                            CONFIDENCE: 0.88
                            ISSUES: Missing risk disclosure about tax implications
                            """
                        )
                    )
                ]
            )

            result = validator.validate(
                guidance=guidance,
                customer=simple_customer,
                reasoning="Customer asking about lump sum withdrawal",
            )

        assert result.passed is False
        # Check for risk disclosure issue
        risk_issues = [
            i for i in result.issues if i.issue_type == IssueType.RISK_DISCLOSURE
        ]
        assert len(risk_issues) >= 1

    def test_validate_low_confidence_requires_review(self, validator, simple_customer):
        """Test that low confidence triggers human review even if passed."""
        guidance = """
        Your pension options depend on the specific terms of your scheme.
        You might want to consider the different withdrawal methods available.
        """

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            # Mock LLM response with low confidence
            mock_completion.return_value = MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content="""
                            ANALYSIS:
                            1. Guidance vs Advice boundary: UNCERTAIN - Vague language
                            2. Risk disclosure: PASS
                            3. Clear and not misleading: UNCERTAIN - Could be clearer
                            4. Understanding verification: FAIL
                            5. Signposting: PASS

                            OVERALL: UNCERTAIN
                            CONFIDENCE: 0.55
                            ISSUES: Vague guidance, could be more specific
                            """
                        )
                    )
                ]
            )

            result = validator.validate(
                guidance=guidance,
                customer=simple_customer,
                reasoning="Customer asking about pension options",
            )

        # Low confidence should trigger human review
        assert result.confidence < 0.70
        assert result.requires_human_review is True

    def test_validate_db_pension_requires_warning(self, validator):
        """Test that DB pension transfer requires specific warning."""
        db_customer = CustomerProfile(
            demographics=CustomerDemographics(
                age=55,
                gender="M",
                location="London",
                employment_status="employed",
                financial_literacy="medium",
            ),
            financial=FinancialSituation(
                annual_income=50000,
                total_assets=200000,
                total_debt=10000,
                dependents=0,
                risk_tolerance="medium",
            ),
            pensions=[
                PensionPot(
                    pot_id="pot1",
                    provider="Company Pension",
                    pot_type="defined_benefit",
                    current_value=500000,
                    projected_value=500000,
                    age_accessible=65,
                    is_db_scheme=True,
                    db_guaranteed_amount=20000,
                )
            ],
            goals="Considering transferring my DB pension",
        )

        guidance = """
        You can transfer your defined benefit pension if you choose to.
        """

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            # Mock LLM response - missing DB warning
            mock_completion.return_value = MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content="""
                            ANALYSIS:
                            1. Guidance vs Advice boundary: PASS
                            2. Risk disclosure: FAIL - Missing DB transfer warning
                            3. Clear and not misleading: PASS
                            4. Understanding verification: FAIL
                            5. Signposting: FAIL - Must signpost to FCA-regulated advisor

                            OVERALL: FAIL
                            CONFIDENCE: 0.90
                            ISSUES: Missing DB transfer warning and advisor signposting
                            """
                        )
                    )
                ]
            )

            result = validator.validate(
                guidance=guidance,
                customer=db_customer,
                reasoning="Customer considering DB transfer",
            )

        assert result.passed is False
        # Should have signposting or DB-specific issue
        assert len(result.issues) >= 1

    def test_validate_uses_correct_model(self, validator, simple_customer):
        """Test that validator uses the correct LLM model."""
        guidance = "Test guidance"

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content="""
                            ANALYSIS:
                            1. Guidance vs Advice boundary: PASS
                            2. Risk disclosure: PASS
                            3. Clear and not misleading: PASS
                            4. Understanding verification: PASS
                            5. Signposting: PASS

                            OVERALL: PASS
                            CONFIDENCE: 0.90
                            ISSUES: None
                            """
                        )
                    )
                ]
            )

            validator.validate(
                guidance=guidance,
                customer=simple_customer,
                reasoning="Test",
            )

            # Verify completion was called
            assert mock_completion.called
            call_args = mock_completion.call_args
            # Should use advisor model (GPT-4 or equivalent) for validation
            assert "model" in call_args.kwargs
            # Temperature should be 0 for deterministic compliance checking
            assert call_args.kwargs.get("temperature") == 0

    def test_validate_constructs_proper_prompt(self, validator, simple_customer):
        """Test that validator constructs a proper compliance check prompt."""
        guidance = "Test guidance about pensions"

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content="""
                            ANALYSIS:
                            1. Guidance vs Advice boundary: PASS
                            2. Risk disclosure: PASS
                            3. Clear and not misleading: PASS
                            4. Understanding verification: PASS
                            5. Signposting: PASS

                            OVERALL: PASS
                            CONFIDENCE: 0.90
                            ISSUES: None
                            """
                        )
                    )
                ]
            )

            validator.validate(
                guidance=guidance,
                customer=simple_customer,
                reasoning="Test reasoning",
            )

            # Check prompt was constructed with key elements
            assert mock_completion.called
            call_args = mock_completion.call_args
            messages = call_args.kwargs["messages"]
            prompt = messages[0]["content"]

            # Prompt should include guidance text
            assert "Test guidance about pensions" in prompt
            # Prompt should mention FCA compliance
            assert "FCA" in prompt or "compliance" in prompt.lower()
            # Prompt should mention key checks
            assert "advice" in prompt.lower() or "guidance" in prompt.lower()

    def test_validate_high_confidence_no_review(self, validator, simple_customer):
        """Test that high confidence passing validation doesn't require review."""
        guidance = """
        I can explain the different pension withdrawal options available to you.

        There are typically three main options: taking a tax-free lump sum,
        purchasing an annuity for guaranteed income, or flexible drawdown.
        Each has different tax implications and levels of flexibility.

        Would you like me to explain each option in more detail?
        """

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            mock_completion.return_value = MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content="""
                            ANALYSIS:
                            1. Guidance vs Advice boundary: PASS - Clear guidance, no recommendations
                            2. Risk disclosure: PASS - Mentions different implications
                            3. Clear and not misleading: PASS - Plain language
                            4. Understanding verification: PASS - Asks follow-up question
                            5. Signposting: N/A

                            OVERALL: PASS
                            CONFIDENCE: 0.95
                            ISSUES: None
                            """
                        )
                    )
                ]
            )

            result = validator.validate(
                guidance=guidance,
                customer=simple_customer,
                reasoning="Customer asking about withdrawal options",
            )

        assert result.passed is True
        assert result.confidence >= 0.85
        assert result.requires_human_review is False

    def test_validate_handles_llm_error(self, validator, simple_customer):
        """Test that validator handles LLM errors gracefully."""
        guidance = "Test guidance"

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            # Simulate LLM error
            mock_completion.side_effect = Exception("API Error")

            with pytest.raises(Exception):
                validator.validate(
                    guidance=guidance,
                    customer=simple_customer,
                    reasoning="Test",
                )

    def test_validate_parses_llm_response_correctly(self, validator, simple_customer):
        """Test that validator correctly parses LLM response."""
        guidance = "Test guidance"

        with patch("guidance_agent.compliance.validator.completion") as mock_completion:
            # Mock response with specific format
            mock_completion.return_value = MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content="""
                            ANALYSIS:
                            1. Guidance vs Advice boundary: FAIL - Contains recommendation
                            2. Risk disclosure: PASS
                            3. Clear and not misleading: PASS
                            4. Understanding verification: FAIL - No check
                            5. Signposting: PASS

                            OVERALL: FAIL
                            CONFIDENCE: 0.85
                            ISSUES: Advice boundary violation, No understanding check
                            """
                        )
                    )
                ]
            )

            result = validator.validate(
                guidance=guidance,
                customer=simple_customer,
                reasoning="Test",
            )

        # Verify parsing worked
        assert result.passed is False
        assert result.confidence == pytest.approx(0.85, abs=0.05)
        assert len(result.issues) >= 1

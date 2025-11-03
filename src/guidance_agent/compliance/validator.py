"""Compliance validation for pension guidance.

This module provides FCA compliance validation with confidence scoring
for pension guidance responses. It uses LLM-as-judge to validate that
guidance stays within regulatory boundaries.
"""

import os
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from litellm import completion

from guidance_agent.core.types import CustomerProfile
from guidance_agent.core.provider_config import (
    detect_provider,
    get_provider_info,
)
from guidance_agent.core.template_engine import render_template


class IssueType(str, Enum):
    """Types of compliance issues."""

    ADVICE_BOUNDARY = "advice_boundary"  # Crossed into regulated advice
    RISK_DISCLOSURE = "risk_disclosure"  # Missing or inadequate risk disclosure
    CLARITY = "clarity"  # Unclear or misleading
    UNDERSTANDING_CHECK = "understanding_check"  # No verification of comprehension
    SIGNPOSTING = "signposting"  # Missing signpost to regulated advisor
    DB_WARNING = "db_warning"  # Missing DB transfer warning


class IssueSeverity(str, Enum):
    """Severity levels for compliance issues."""

    HIGH = "high"  # Critical compliance violation
    MEDIUM = "medium"  # Significant concern but not critical
    LOW = "low"  # Minor issue or suggestion


@dataclass
class ValidationIssue:
    """A specific compliance issue found in guidance."""

    issue_type: IssueType
    severity: IssueSeverity
    description: str
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of compliance validation."""

    passed: bool
    confidence: float  # 0-1, confidence in the validation result
    issues: list[ValidationIssue] = field(default_factory=list)
    requires_human_review: bool = False
    reasoning: str = ""


class ComplianceValidator:
    """Validates pension guidance for FCA compliance.

    Uses LLM-as-judge to evaluate guidance against FCA requirements:
    1. Guidance vs Advice boundary
    2. Risk disclosure adequacy
    3. Clarity and not misleading
    4. Understanding verification
    5. Appropriate signposting

    Provides confidence scores to enable human review of borderline cases.
    """

    def __init__(self, model: Optional[str] = None, enable_prompt_caching: bool = True):
        """Initialize compliance validator.

        Args:
            model: LLM model to use for validation. Defaults to LITELLM_MODEL_ADVISOR.
            enable_prompt_caching: Whether to enable prompt caching for cost reduction.
        """
        self.model = model or os.getenv("LITELLM_MODEL_ADVISOR", "gpt-4-turbo-preview")
        self.enable_prompt_caching = enable_prompt_caching

        # Detect provider and capabilities
        self.provider = detect_provider(self.model)
        self.provider_info = get_provider_info(self.model)

    def validate(
        self,
        guidance: str,
        customer: CustomerProfile,
        reasoning: str = "",
    ) -> ValidationResult:
        """Validate guidance for FCA compliance.

        Args:
            guidance: The guidance text to validate
            customer: Customer profile for context
            reasoning: Chain-of-thought reasoning used to generate guidance

        Returns:
            ValidationResult with pass/fail, confidence, and issues
        """
        # Build validation prompt
        prompt = self._build_validation_prompt(guidance, customer, reasoning)

        # Get cache headers
        extra_headers = self._get_cache_headers()

        # Call LLM for validation
        response = completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,  # Deterministic for compliance checking
            extra_headers=extra_headers if extra_headers else None,
        )

        # Parse response
        validation_text = response.choices[0].message.content

        # Extract validation result
        result = self._parse_validation_response(validation_text)

        return result

    async def validate_async(
        self,
        guidance: str,
        customer: CustomerProfile,
        reasoning: str = "",
    ) -> ValidationResult:
        """Validate guidance for FCA compliance asynchronously.

        This method allows validation to run in parallel with streaming,
        so it doesn't block the user experience.

        Args:
            guidance: The guidance text to validate
            customer: Customer profile for context
            reasoning: Chain-of-thought reasoning used to generate guidance

        Returns:
            ValidationResult with pass/fail, confidence, and issues
        """
        # Build validation prompt
        prompt = self._build_validation_prompt(guidance, customer, reasoning)

        # Get cache headers
        extra_headers = self._get_cache_headers()

        # Call LLM for validation (synchronous LLM call in async context)
        response = completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,  # Deterministic for compliance checking
            extra_headers=extra_headers if extra_headers else None,
        )

        # Parse response
        validation_text = response.choices[0].message.content

        # Extract validation result
        result = self._parse_validation_response(validation_text)

        return result

    def _get_cache_headers(self) -> dict:
        """Get cache headers based on model provider.

        Returns:
            dict: Cache headers for the LLM API call
        """
        if not self.enable_prompt_caching:
            return {}

        if not self.provider_info["supports_caching"]:
            return {}

        return self.provider_info["cache_headers"]

    def _build_validation_prompt(
        self,
        guidance: str,
        customer: CustomerProfile,
        reasoning: str,
    ) -> str:
        """Build prompt for compliance validation.

        Args:
            guidance: The guidance text to validate
            customer: Customer profile
            reasoning: Reasoning behind the guidance

        Returns:
            Formatted validation prompt
        """
        return render_template(
            "compliance/validation.jinja",
            guidance=guidance,
            customer=customer,
            reasoning=reasoning,
        )

    def _parse_validation_response(self, response: str) -> ValidationResult:
        """Parse LLM validation response into ValidationResult.

        Args:
            response: Raw LLM response text

        Returns:
            Parsed ValidationResult
        """
        # Extract overall result
        overall_match = re.search(r"OVERALL:\s*(PASS|FAIL|UNCERTAIN)", response)
        overall = overall_match.group(1) if overall_match else "UNCERTAIN"

        # Extract confidence
        confidence_match = re.search(r"CONFIDENCE:\s*([0-9.]+)", response)
        confidence = float(confidence_match.group(1)) if confidence_match else 0.5

        # Extract issues
        issues_match = re.search(r"ISSUES:\s*(.+)", response)
        issues_text = issues_match.group(1).strip() if issues_match else ""

        # Parse individual checks to identify issue types
        issues = []

        # Check each compliance area
        if "Guidance vs Advice boundary: FAIL" in response:
            issues.append(
                ValidationIssue(
                    issue_type=IssueType.ADVICE_BOUNDARY,
                    severity=IssueSeverity.HIGH,
                    description="Guidance crossed into regulated advice territory",
                    suggestion="Rephrase to avoid specific recommendations. Use 'you could consider' instead of 'you should'.",
                )
            )

        if "Risk disclosure: FAIL" in response:
            # Check if it's DB-specific
            if "DB" in response or "defined benefit" in response.lower():
                issues.append(
                    ValidationIssue(
                        issue_type=IssueType.DB_WARNING,
                        severity=IssueSeverity.HIGH,
                        description="Missing DB transfer warning and risks",
                        suggestion="Include warning about giving up guaranteed income and requirement for FCA-regulated advice.",
                    )
                )
            else:
                issues.append(
                    ValidationIssue(
                        issue_type=IssueType.RISK_DISCLOSURE,
                        severity=IssueSeverity.HIGH,
                        description="Missing or inadequate risk disclosure",
                        suggestion="Clearly explain relevant risks and tax implications.",
                    )
                )

        if "Clear and not misleading: FAIL" in response:
            issues.append(
                ValidationIssue(
                    issue_type=IssueType.CLARITY,
                    severity=IssueSeverity.MEDIUM,
                    description="Guidance unclear or potentially misleading",
                    suggestion="Use simpler language appropriate for customer's literacy level.",
                )
            )

        if "Understanding verification: FAIL" in response:
            issues.append(
                ValidationIssue(
                    issue_type=IssueType.UNDERSTANDING_CHECK,
                    severity=IssueSeverity.MEDIUM,
                    description="No verification of customer understanding",
                    suggestion="Add questions to check customer comprehension before proceeding.",
                )
            )

        if "Signposting: FAIL" in response:
            issues.append(
                ValidationIssue(
                    issue_type=IssueType.SIGNPOSTING,
                    severity=IssueSeverity.HIGH,
                    description="Missing signposting to FCA-regulated advisor",
                    suggestion="Direct customer to seek regulated financial advice for this decision.",
                )
            )

        # Handle UNCERTAIN results
        if "UNCERTAIN" in response:
            # Extract uncertain areas
            if "Guidance vs Advice boundary: UNCERTAIN" in response:
                issues.append(
                    ValidationIssue(
                        issue_type=IssueType.ADVICE_BOUNDARY,
                        severity=IssueSeverity.MEDIUM,
                        description="Borderline case - guidance boundary unclear",
                        suggestion="Review and clarify to ensure clear guidance language.",
                    )
                )
            if "Clear and not misleading: UNCERTAIN" in response:
                issues.append(
                    ValidationIssue(
                        issue_type=IssueType.CLARITY,
                        severity=IssueSeverity.MEDIUM,
                        description="Clarity uncertain - could be improved",
                        suggestion="Simplify language and structure for better clarity.",
                    )
                )

        # Determine pass/fail
        passed = overall == "PASS"

        # Determine if human review is needed
        # Low confidence (<0.70) or UNCERTAIN always requires review
        # High-severity issues also require review
        requires_review = (
            confidence < 0.70
            or overall == "UNCERTAIN"
            or any(i.severity == IssueSeverity.HIGH for i in issues)
        )

        return ValidationResult(
            passed=passed,
            confidence=confidence,
            issues=issues,
            requires_human_review=requires_review,
            reasoning=response,
        )

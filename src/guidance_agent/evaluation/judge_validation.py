"""LLM-as-judge validation against expert human judgments.

This module validates the accuracy of LLM judges against expert-labeled
consultations, computing inter-rater reliability and error rates.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import math

from litellm import completion


@dataclass
class ValidationReport:
    """Report from LLM-as-judge validation study.

    Attributes:
        total_consultations: Number of consultations evaluated
        agreement_rate: Proportion of judgments matching expert labels
        cohens_kappa: Cohen's kappa inter-rater reliability coefficient
        false_negative_rate: Rate of missed compliance violations
        false_positive_rate: Rate of false alarms
        confidence_calibration: Analysis of confidence score calibration
    """

    total_consultations: int
    agreement_rate: float
    cohens_kappa: float
    false_negative_rate: float
    false_positive_rate: float
    confidence_calibration: Dict[str, float]


class LLMJudge:
    """LLM-based judge for evaluating consultation quality.

    Uses an LLM to evaluate whether a consultation was compliant
    and appropriate.
    """

    def __init__(self, model: str, prompt_version: str = "v1"):
        """Initialize LLM judge.

        Args:
            model: Model name (e.g., "gpt-4", "claude-3-5-sonnet")
            prompt_version: Version of evaluation prompt to use
        """
        self.model = model
        self.prompt_version = prompt_version

    def evaluate(
        self, transcript: str, customer_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Evaluate a consultation transcript.

        Args:
            transcript: Full consultation transcript
            customer_context: Optional customer context/background

        Returns:
            Dictionary with:
                - passed: bool (compliant or not)
                - confidence: float (0-1)
                - reasoning: str (explanation)

        Example:
            >>> judge = LLMJudge("gpt-4")
            >>> result = judge.evaluate(transcript)
            >>> if result["passed"]:
            ...     print("Compliant")
        """
        # Simplified evaluation for testing
        # In production, this would use sophisticated prompting
        prompt = f"""Evaluate if this pension guidance consultation was FCA-compliant.

Transcript:
{transcript}

Respond with:
- PASS or FAIL
- Confidence (0-1)
- Brief reasoning

Format: PASS|0.9|Reasoning here
"""

        try:
            response = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )

            # Parse response (simplified)
            content = response.choices[0].message.content.strip()

            # Default response for testing
            return {
                "passed": "PASS" in content.upper(),
                "confidence": 0.8,
                "reasoning": content,
            }
        except Exception as e:
            # Return conservative default on error
            return {
                "passed": False,
                "confidence": 0.5,
                "reasoning": f"Error: {str(e)}",
            }


def compute_consensus(judge_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute consensus across multiple judge evaluations.

    Uses majority voting for binary decision and averages confidence scores.

    Args:
        judge_results: List of judge evaluation results

    Returns:
        Dictionary with consensus decision and confidence

    Example:
        >>> results = [
        ...     {"passed": True, "confidence": 0.9},
        ...     {"passed": True, "confidence": 0.8},
        ...     {"passed": False, "confidence": 0.6},
        ... ]
        >>> consensus = compute_consensus(results)
        >>> consensus["passed"]  # True (2 out of 3)
        True
    """
    if not judge_results:
        return {"passed": False, "confidence": 0.0}

    # Majority vote for decision
    passed_count = sum(1 for r in judge_results if r["passed"])
    consensus_passed = passed_count > len(judge_results) / 2

    # Average confidence
    avg_confidence = sum(r["confidence"] for r in judge_results) / len(judge_results)

    return {
        "passed": consensus_passed,
        "confidence": avg_confidence,
    }


def calculate_cohens_kappa(results: List[Dict[str, Any]]) -> float:
    """Calculate Cohen's kappa inter-rater reliability coefficient.

    Args:
        results: List of validation results with expert_label and judge_consensus

    Returns:
        Cohen's kappa coefficient (-1 to 1, where 1 is perfect agreement)

    Example:
        >>> results = [
        ...     {"expert_label": True, "judge_consensus": True},
        ...     {"expert_label": False, "judge_consensus": False},
        ... ]
        >>> kappa = calculate_cohens_kappa(results)
    """
    if not results:
        return 0.0

    n = len(results)

    # Count agreements and disagreements
    both_true = sum(
        1 for r in results if r["expert_label"] and r["judge_consensus"]
    )
    both_false = sum(
        1 for r in results if not r["expert_label"] and not r["judge_consensus"]
    )

    # Observed agreement
    p_o = (both_true + both_false) / n

    # Expected agreement by chance
    expert_true = sum(1 for r in results if r["expert_label"])
    judge_true = sum(1 for r in results if r["judge_consensus"])

    p_expert_true = expert_true / n
    p_expert_false = 1 - p_expert_true
    p_judge_true = judge_true / n
    p_judge_false = 1 - p_judge_true

    p_e = (p_expert_true * p_judge_true) + (p_expert_false * p_judge_false)

    # Cohen's kappa
    if p_e == 1.0:
        return 0.0  # Avoid division by zero

    kappa = (p_o - p_e) / (1 - p_e)
    return kappa


def calculate_fn_rate(results: List[Dict[str, Any]]) -> float:
    """Calculate false negative rate.

    False negatives are cases where expert says compliant (True) but
    judge says non-compliant (False). These are the most critical errors.

    Args:
        results: List of validation results

    Returns:
        False negative rate (0 to 1)

    Example:
        >>> results = [
        ...     {"expert_label": True, "judge_consensus": False},  # FN
        ...     {"expert_label": True, "judge_consensus": True},   # TP
        ... ]
        >>> fn_rate = calculate_fn_rate(results)
        0.5
    """
    # Get all positive cases (expert says compliant)
    positives = [r for r in results if r["expert_label"]]

    if not positives:
        return 0.0

    # Count false negatives (expert True, judge False)
    false_negatives = sum(1 for r in positives if not r["judge_consensus"])

    return false_negatives / len(positives)


def calculate_fp_rate(results: List[Dict[str, Any]]) -> float:
    """Calculate false positive rate.

    False positives are cases where expert says non-compliant (False) but
    judge says compliant (True). These are false alarms.

    Args:
        results: List of validation results

    Returns:
        False positive rate (0 to 1)

    Example:
        >>> results = [
        ...     {"expert_label": False, "judge_consensus": True},   # FP
        ...     {"expert_label": False, "judge_consensus": False},  # TN
        ... ]
        >>> fp_rate = calculate_fp_rate(results)
        0.5
    """
    # Get all negative cases (expert says non-compliant)
    negatives = [r for r in results if not r["expert_label"]]

    if not negatives:
        return 0.0

    # Count false positives (expert False, judge True)
    false_positives = sum(1 for r in negatives if r["judge_consensus"])

    return false_positives / len(negatives)


def analyze_confidence_calibration(
    results: List[Dict[str, Any]]
) -> Dict[str, float]:
    """Analyze confidence score calibration.

    Compares expert confidence scores with judge confidence scores to
    assess calibration quality.

    Args:
        results: List of validation results with expert_confidence and judge_confidence

    Returns:
        Dictionary with calibration metrics:
            - mean_error: Mean absolute error between confidences
            - rmse: Root mean squared error

    Example:
        >>> results = [
        ...     {"expert_confidence": 0.9, "judge_confidence": 0.8},
        ...     {"expert_confidence": 0.7, "judge_confidence": 0.75},
        ... ]
        >>> calibration = analyze_confidence_calibration(results)
    """
    if not results:
        return {"mean_error": 0.0, "rmse": 0.0}

    errors = []
    squared_errors = []

    for r in results:
        expert_conf = r.get("expert_confidence", 0.5)
        judge_conf = r.get("judge_confidence", 0.5)

        error = abs(expert_conf - judge_conf)
        errors.append(error)
        squared_errors.append(error**2)

    mean_error = sum(errors) / len(errors)
    rmse = math.sqrt(sum(squared_errors) / len(squared_errors))

    return {
        "mean_error": mean_error,
        "rmse": rmse,
    }


def validate_llm_judges(
    expert_labeled_consultations: List[Any],
) -> ValidationReport:
    """Validate LLM judges against expert human judgments.

    Runs multiple LLM judges on expert-labeled consultations and computes
    comprehensive validation metrics including inter-rater reliability,
    false negative/positive rates, and confidence calibration.

    Args:
        expert_labeled_consultations: List of consultations with expert labels.
            Each should have attributes:
                - consultation_id: str
                - transcript: str
                - expert_label: bool (True = compliant, False = violation)
                - expert_confidence: float (0-1)
                - expert_reasoning: str

    Returns:
        ValidationReport with comprehensive validation metrics

    Example:
        >>> consultations = load_expert_labeled_consultations()
        >>> report = validate_llm_judges(consultations)
        >>> print(f"Agreement: {report.agreement_rate:.2%}")
        >>> print(f"Cohen's kappa: {report.cohens_kappa:.3f}")
        >>> print(f"FN rate: {report.false_negative_rate:.2%}")
        >>> print(f"FP rate: {report.false_positive_rate:.2%}")

    Success criteria for production:
        - Cohen's kappa > 0.85 (strong agreement)
        - False negative rate < 1% (few violations missed)
        - False positive rate < 10% (acceptable false alarms)
    """
    if not expert_labeled_consultations:
        return ValidationReport(
            total_consultations=0,
            agreement_rate=0.0,
            cohens_kappa=0.0,
            false_negative_rate=0.0,
            false_positive_rate=0.0,
            confidence_calibration={"mean_error": 0.0, "rmse": 0.0},
        )

    # Initialize judges
    judges = [
        LLMJudge("gpt-4"),
        LLMJudge("claude-3-5-sonnet"),
        LLMJudge("gpt-4", prompt_version="v2"),
    ]

    results = []

    for consultation in expert_labeled_consultations:
        # Get evaluations from all judges
        judge_results = []
        for judge in judges:
            result = judge.evaluate(consultation.transcript)
            judge_results.append(result)

        # Compute consensus
        consensus = compute_consensus(judge_results)

        # Compare to expert label
        agreement = consensus["passed"] == consultation.expert_label

        results.append({
            "consultation_id": consultation.consultation_id,
            "expert_label": consultation.expert_label,
            "expert_confidence": consultation.expert_confidence,
            "judge_consensus": consensus["passed"],
            "judge_confidence": consensus["confidence"],
            "agreement": agreement,
            "judge_details": judge_results,
        })

    # Calculate validation metrics
    total = len(results)
    agreement_rate = sum(1 for r in results if r["agreement"]) / total
    cohens_kappa = calculate_cohens_kappa(results)
    fn_rate = calculate_fn_rate(results)
    fp_rate = calculate_fp_rate(results)
    calibration = analyze_confidence_calibration(results)

    return ValidationReport(
        total_consultations=total,
        agreement_rate=agreement_rate,
        cohens_kappa=cohens_kappa,
        false_negative_rate=fn_rate,
        false_positive_rate=fp_rate,
        confidence_calibration=calibration,
    )

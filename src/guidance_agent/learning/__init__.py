"""Learning system for the guidance agent.

This module implements the learning mechanisms for the agent, including:
- Learning from successful consultations (case extraction)
- Learning from failures (reflection and rule generation)
- Rule validation and refinement
- Confidence adjustment based on outcomes
"""

from guidance_agent.learning.case_learning import (
    learn_from_successful_consultation,
    extract_case_from_consultation,
    classify_task_type,
    summarize_customer_situation,
)
from guidance_agent.learning.reflection import (
    learn_from_failure,
    reflect_on_failure,
    validate_principle,
    refine_principle,
    judge_rule_value,
)
from guidance_agent.learning.validation import (
    update_rule_confidence,
    track_rule_performance,
    adjust_confidence_on_success,
    adjust_confidence_on_failure,
    get_rule_performance_metrics,
)

__all__ = [
    # Case learning
    "learn_from_successful_consultation",
    "extract_case_from_consultation",
    "classify_task_type",
    "summarize_customer_situation",
    # Reflection learning
    "learn_from_failure",
    "reflect_on_failure",
    "validate_principle",
    "refine_principle",
    "judge_rule_value",
    # Validation and confidence adjustment
    "update_rule_confidence",
    "track_rule_performance",
    "adjust_confidence_on_success",
    "adjust_confidence_on_failure",
    "get_rule_performance_metrics",
]

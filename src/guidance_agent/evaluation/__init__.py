"""Evaluation and metrics for advisor performance.

This module provides comprehensive evaluation tools for measuring advisor
quality across multiple dimensions.
"""

from guidance_agent.evaluation.metrics import AdvisorMetrics, calculate_metrics
from guidance_agent.evaluation.evaluator import evaluate_advisor, run_consultation
from guidance_agent.evaluation.ablation import (
    AblationResults,
    run_ablation_study,
    compare_ablation_results,
)
from guidance_agent.evaluation.experiments import (
    run_training_experiment,
    store_experiment_outcomes,
    load_experiment_outcomes,
)
from guidance_agent.evaluation.judge_validation import (
    ValidationReport,
    validate_llm_judges,
    LLMJudge,
    calculate_cohens_kappa,
    calculate_fn_rate,
    calculate_fp_rate,
    analyze_confidence_calibration,
)

__all__ = [
    "AdvisorMetrics",
    "calculate_metrics",
    "evaluate_advisor",
    "run_consultation",
    "AblationResults",
    "run_ablation_study",
    "compare_ablation_results",
    "run_training_experiment",
    "store_experiment_outcomes",
    "load_experiment_outcomes",
    "ValidationReport",
    "validate_llm_judges",
    "LLMJudge",
    "calculate_cohens_kappa",
    "calculate_fn_rate",
    "calculate_fp_rate",
    "analyze_confidence_calibration",
]

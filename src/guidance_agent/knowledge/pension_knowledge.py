"""Pension knowledge module for UK pension system.

This module contains structured knowledge about UK pension types, regulations,
typical scenarios, and fee structures to support guidance conversations.
"""

from typing import Dict, Optional, Tuple


PENSION_KNOWLEDGE = {
    "pension_types": {
        "defined_contribution": {
            "description": "Pension pot built from contributions, value depends on investment growth",
            "typical_providers": ["NEST", "Aviva", "Royal London", "Standard Life"],
            "common_features": ["flexible_access", "investment_choice", "death_benefits"],
            "typical_fees": {"min": 0.003, "max": 0.015},
            "fca_considerations": "No guaranteed income, investment risk borne by member",
            "min_value_range": (100, 500000),
            "typical_by_age": {
                "25-35": (1000, 15000),
                "35-50": (10000, 100000),
                "50-retirement": (50000, 300000)
            }
        },
        "defined_benefit": {
            "description": "Guaranteed income based on salary and years of service",
            "calculation": "accrual_rate × years_service × final_salary",
            "typical_accrual_rates": [1/60, 1/80],
            "typical_sectors": ["public_sector", "large_employers_pre_2000", "local_government"],
            "fca_warning": "Valuable guarantees lost if transferred out - requires regulated advice if >£30k",
            "special_features": ["guaranteed_income", "inflation_protection", "survivor_benefits", "early_retirement_factors"],
            "transfer_value_multiple": {"min": 20, "max": 40}  # Typical CETV as multiple of annual income
        }
    },
    "regulations": {
        "auto_enrollment": {
            "started": 2012,
            "minimum_total_contribution": 0.08,
            "employer_minimum": 0.03,
            "employee_minimum": 0.05,
            "earnings_trigger": 10000,
            "age_range": (22, "state_pension_age")
        },
        "db_transfers": {
            "advice_threshold": 30000,
            "fca_requirement": "Regulated financial advice mandatory for transfers >£30k",
            "typical_outcome": "Most people worse off transferring from DB to DC",
            "tvas_requirement": "Transfer Value Analysis required",
            "appropriate_pension_transfer_analysis": "APTA required from FCA authorized adviser"
        },
        "small_pots": {
            "definition": "Pension pot worth less than £10,000",
            "limit_per_year": 3,
            "no_advice_needed": True,
            "common_scenario": "Consolidation of old workplace pensions"
        }
    },
    "typical_scenarios": {
        "young_worker_22_30": {
            "age_range": (22, 30),
            "pension_count_range": (1, 2),
            "total_value_range": (1000, 15000),
            "common_types": ["defined_contribution"],
            "common_goals": ["understand_basics", "check_on_track", "consolidate_old_pots"],
            "typical_providers": ["NEST", "NOW Pensions", "The People's Pension"]
        },
        "mid_career_35_50": {
            "age_range": (35, 50),
            "pension_count_range": (2, 5),
            "total_value_range": (20000, 150000),
            "common_types": ["defined_contribution", "small_db_from_early_career"],
            "common_goals": ["consolidation", "reduce_fees", "check_on_track", "boost_savings"],
            "typical_providers": ["Aviva", "Standard Life", "Royal London", "Prudential"]
        },
        "pre_retirement_55_67": {
            "age_range": (55, 67),
            "pension_count_range": (3, 8),
            "total_value_range": (50000, 400000),
            "common_types": ["defined_contribution", "defined_benefit", "personal_pensions"],
            "common_goals": ["consolidation", "access_planning", "understand_options", "maximize_income"],
            "special_considerations": ["protected_tax_free_cash", "guaranteed_annuity_rates", "db_safeguarded_benefits"]
        }
    },
    "fee_structures": {
        "workplace_dc": {
            "nest": 0.003,  # 0.3%
            "now_pensions": 0.003,
            "peoples_pension": 0.005,
            "provider_default": 0.01  # Typical 1%
        },
        "personal_pensions": {
            "platform_fee": (0.002, 0.0045),  # 0.2% - 0.45%
            "fund_fees": (0.001, 0.015),  # 0.1% - 1.5%
            "total_typical": 0.01  # 1% combined
        }
    }
}


def get_pension_type_info(pension_type: str) -> Optional[Dict]:
    """Get information about a specific pension type.

    Args:
        pension_type: The pension type to look up (e.g., "defined_contribution", "defined_benefit")

    Returns:
        Dictionary containing pension type information, or None if not found
    """
    return PENSION_KNOWLEDGE["pension_types"].get(pension_type)


def get_regulation_info(regulation_name: str) -> Optional[Dict]:
    """Get regulatory information.

    Args:
        regulation_name: The regulation to look up (e.g., "auto_enrollment", "db_transfers")

    Returns:
        Dictionary containing regulation information, or None if not found
    """
    return PENSION_KNOWLEDGE["regulations"].get(regulation_name)


def get_typical_scenario(scenario_name: str) -> Optional[Dict]:
    """Get typical customer scenario information.

    Args:
        scenario_name: The scenario to look up (e.g., "young_worker_22_30")

    Returns:
        Dictionary containing scenario information, or None if not found
    """
    return PENSION_KNOWLEDGE["typical_scenarios"].get(scenario_name)


def get_fee_structure(pension_category: str) -> Optional[Dict]:
    """Get typical fee structure for pension category.

    Args:
        pension_category: The category to look up (e.g., "workplace_dc", "personal_pensions")

    Returns:
        Dictionary containing fee structure information, or None if not found
    """
    return PENSION_KNOWLEDGE["fee_structures"].get(pension_category)


def parse_age_range(age_range_str: str) -> Tuple[int, int]:
    """Parse age range string into tuple of integers.

    Args:
        age_range_str: Age range string like "25-35" or "55-retirement"

    Returns:
        Tuple of (min_age, max_age). "retirement" is converted to 67 (UK state pension age)
    """
    parts = age_range_str.split('-')
    min_age = int(parts[0])
    max_age = int(parts[1]) if parts[1] != 'retirement' else 67
    return (min_age, max_age)


def validate_pension_value_for_age(age: int, total_value: float, pension_type: str) -> bool:
    """Validate if pension value is realistic for customer age.

    This function checks if a given pension value is within reasonable bounds
    for a person of the given age, based on typical pension values by age range.

    Args:
        age: Customer's age
        total_value: Total pension value in pounds
        pension_type: Type of pension (e.g., "defined_contribution")

    Returns:
        True if the value is realistic or if validation cannot be performed,
        False if the value is clearly unrealistic for the age
    """
    pension_info = get_pension_type_info(pension_type)
    if not pension_info or "typical_by_age" not in pension_info:
        return True  # Unknown type, skip validation

    # Find appropriate age range
    for age_range_key, (min_val, max_val) in pension_info["typical_by_age"].items():
        age_range = parse_age_range(age_range_key)
        if age_range[0] <= age <= age_range[1]:
            # Allow 2x typical max for edge cases (high earners, etc.)
            return min_val <= total_value <= max_val * 2

    return True  # Age outside known ranges, skip validation

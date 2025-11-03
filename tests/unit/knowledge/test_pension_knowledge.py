"""Tests for pension knowledge module."""

import pytest
from guidance_agent.knowledge.pension_knowledge import (
    PENSION_KNOWLEDGE,
    get_pension_type_info,
    get_regulation_info,
    get_typical_scenario,
    get_fee_structure,
    validate_pension_value_for_age,
    parse_age_range,
)


class TestPensionKnowledgeStructure:
    """Test the structure and completeness of pension knowledge."""

    def test_pension_knowledge_exists(self):
        """Test that PENSION_KNOWLEDGE dictionary exists."""
        assert PENSION_KNOWLEDGE is not None
        assert isinstance(PENSION_KNOWLEDGE, dict)

    def test_pension_types_exist(self):
        """Test that pension types are defined."""
        assert "pension_types" in PENSION_KNOWLEDGE
        assert isinstance(PENSION_KNOWLEDGE["pension_types"], dict)

    def test_defined_contribution_pension_type(self):
        """Test DC pension type has required fields."""
        dc = PENSION_KNOWLEDGE["pension_types"]["defined_contribution"]
        assert "description" in dc
        assert "typical_providers" in dc
        assert "common_features" in dc
        assert "typical_fees" in dc
        assert "fca_considerations" in dc
        assert isinstance(dc["typical_providers"], list)
        assert len(dc["typical_providers"]) > 0

    def test_defined_benefit_pension_type(self):
        """Test DB pension type has required fields."""
        db = PENSION_KNOWLEDGE["pension_types"]["defined_benefit"]
        assert "description" in db
        assert "calculation" in db
        assert "typical_accrual_rates" in db
        assert "fca_warning" in db
        assert "special_features" in db
        assert "transfer_value_multiple" in db

    def test_regulations_exist(self):
        """Test that regulations are defined."""
        assert "regulations" in PENSION_KNOWLEDGE
        regulations = PENSION_KNOWLEDGE["regulations"]
        assert "auto_enrollment" in regulations
        assert "db_transfers" in regulations
        assert "small_pots" in regulations

    def test_db_transfer_regulations(self):
        """Test DB transfer regulations have critical fields."""
        db_regs = PENSION_KNOWLEDGE["regulations"]["db_transfers"]
        assert db_regs["advice_threshold"] == 30000
        assert "fca_requirement" in db_regs
        assert "£30k" in db_regs["fca_requirement"] or "30k" in db_regs["fca_requirement"]

    def test_typical_scenarios_exist(self):
        """Test that typical scenarios are defined."""
        assert "typical_scenarios" in PENSION_KNOWLEDGE
        scenarios = PENSION_KNOWLEDGE["typical_scenarios"]
        assert "young_worker_22_30" in scenarios
        assert "mid_career_35_50" in scenarios
        assert "pre_retirement_55_67" in scenarios

    def test_fee_structures_exist(self):
        """Test that fee structures are defined."""
        assert "fee_structures" in PENSION_KNOWLEDGE
        fees = PENSION_KNOWLEDGE["fee_structures"]
        assert "workplace_dc" in fees
        assert "personal_pensions" in fees


class TestPensionKnowledgeAccessors:
    """Test accessor functions for pension knowledge."""

    def test_get_pension_type_info_dc(self):
        """Test getting DC pension info."""
        info = get_pension_type_info("defined_contribution")
        assert info is not None
        assert "description" in info
        assert "typical_providers" in info

    def test_get_pension_type_info_db(self):
        """Test getting DB pension info."""
        info = get_pension_type_info("defined_benefit")
        assert info is not None
        assert "fca_warning" in info
        assert "transfer_value_multiple" in info

    def test_get_pension_type_info_invalid(self):
        """Test getting info for invalid pension type."""
        info = get_pension_type_info("nonexistent_type")
        assert info is None

    def test_get_regulation_info_db_transfers(self):
        """Test getting DB transfer regulation info."""
        info = get_regulation_info("db_transfers")
        assert info is not None
        assert info["advice_threshold"] == 30000

    def test_get_regulation_info_auto_enrollment(self):
        """Test getting auto-enrollment regulation info."""
        info = get_regulation_info("auto_enrollment")
        assert info is not None
        assert "started" in info
        assert "minimum_total_contribution" in info

    def test_get_typical_scenario_young_worker(self):
        """Test getting young worker scenario."""
        scenario = get_typical_scenario("young_worker_22_30")
        assert scenario is not None
        assert "age_range" in scenario
        assert "pension_count_range" in scenario
        assert "total_value_range" in scenario
        assert "common_goals" in scenario

    def test_get_typical_scenario_pre_retirement(self):
        """Test getting pre-retirement scenario."""
        scenario = get_typical_scenario("pre_retirement_55_67")
        assert scenario is not None
        assert "special_considerations" in scenario

    def test_get_fee_structure_workplace(self):
        """Test getting workplace DC fees."""
        fees = get_fee_structure("workplace_dc")
        assert fees is not None
        assert "nest" in fees
        assert fees["nest"] == 0.003  # 0.3%

    def test_get_fee_structure_personal(self):
        """Test getting personal pension fees."""
        fees = get_fee_structure("personal_pensions")
        assert fees is not None
        assert "platform_fee" in fees
        assert "fund_fees" in fees


class TestParseAgeRange:
    """Test age range parsing."""

    def test_parse_simple_range(self):
        """Test parsing simple age range."""
        min_age, max_age = parse_age_range("25-35")
        assert min_age == 25
        assert max_age == 35

    def test_parse_range_with_retirement(self):
        """Test parsing range ending in 'retirement'."""
        min_age, max_age = parse_age_range("55-retirement")
        assert min_age == 55
        assert max_age == 67  # Default retirement age

    def test_parse_single_digit_ages(self):
        """Test parsing single digit ages."""
        min_age, max_age = parse_age_range("5-9")
        assert min_age == 5
        assert max_age == 9


class TestValidatePensionValue:
    """Test pension value validation for age."""

    def test_validate_young_worker_valid_value(self):
        """Test validation passes for realistic young worker pension value."""
        # Young worker (25) with £5,000 should be valid
        is_valid = validate_pension_value_for_age(25, 5000, "defined_contribution")
        assert is_valid is True

    def test_validate_mid_career_valid_value(self):
        """Test validation passes for realistic mid-career pension value."""
        # Mid-career (40) with £50,000 should be valid
        is_valid = validate_pension_value_for_age(40, 50000, "defined_contribution")
        assert is_valid is True

    def test_validate_pre_retirement_valid_value(self):
        """Test validation passes for realistic pre-retirement pension value."""
        # Pre-retirement (60) with £200,000 should be valid
        is_valid = validate_pension_value_for_age(60, 200000, "defined_contribution")
        assert is_valid is True

    def test_validate_unrealistic_value_for_age(self):
        """Test validation fails for unrealistic pension value."""
        # 25-year-old with £1,000,000 should be invalid
        is_valid = validate_pension_value_for_age(25, 1000000, "defined_contribution")
        assert is_valid is False

    def test_validate_unknown_pension_type(self):
        """Test validation passes for unknown pension type (skip validation)."""
        is_valid = validate_pension_value_for_age(30, 50000, "unknown_type")
        assert is_valid is True


class TestPensionKnowledgeConsistency:
    """Test consistency and data quality of pension knowledge."""

    def test_all_scenarios_have_age_ranges(self):
        """Test all scenarios define age ranges."""
        scenarios = PENSION_KNOWLEDGE["typical_scenarios"]
        for name, scenario in scenarios.items():
            assert "age_range" in scenario, f"{name} missing age_range"
            age_range = scenario["age_range"]
            assert isinstance(age_range, tuple), f"{name} age_range not a tuple"
            assert len(age_range) == 2, f"{name} age_range should have 2 values"

    def test_all_scenarios_have_value_ranges(self):
        """Test all scenarios define value ranges."""
        scenarios = PENSION_KNOWLEDGE["typical_scenarios"]
        for name, scenario in scenarios.items():
            assert "total_value_range" in scenario, f"{name} missing total_value_range"
            value_range = scenario["total_value_range"]
            assert isinstance(value_range, tuple), f"{name} value_range not a tuple"
            assert value_range[0] < value_range[1], f"{name} value range invalid"

    def test_fee_ranges_are_valid(self):
        """Test fee structures have valid percentage values."""
        fees = PENSION_KNOWLEDGE["fee_structures"]
        for category, fee_info in fees.items():
            if isinstance(fee_info, dict):
                for key, value in fee_info.items():
                    if isinstance(value, (int, float)):
                        assert 0 <= value <= 0.05, f"{category}.{key} fee {value} seems unrealistic"
                    elif isinstance(value, tuple):
                        assert value[0] < value[1], f"{category}.{key} range invalid"

    def test_db_transfer_threshold_consistency(self):
        """Test DB transfer threshold is consistent."""
        threshold = PENSION_KNOWLEDGE["regulations"]["db_transfers"]["advice_threshold"]
        assert threshold == 30000, "DB transfer threshold should be £30,000"

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
        },
        "sipp": {
            "description": "Self-Invested Personal Pension - offers wider investment choice than standard pensions",
            "typical_providers": ["Hargreaves Lansdown", "AJ Bell", "Interactive Investor", "Fidelity"],
            "common_features": ["wide_investment_choice", "commercial_property", "individual_shares", "etfs", "funds"],
            "typical_fees": {
                "platform_fee": (0.0025, 0.0045),  # 0.25% - 0.45%
                "dealing_charges": (5, 12),  # Per trade
                "annual_fee_cap": (0, 200)  # Some providers cap fees
            },
            "fca_considerations": "Greater investment freedom requires understanding of investment risks",
            "min_value_range": (1000, 10000000),
            "suitable_for": ["experienced_investors", "high_value_pensions", "business_owners"],
            "restrictions": ["no_residential_property", "arm_length_transactions", "prohibited_assets"]
        },
        "stakeholder": {
            "description": "Low-cost pension with capped charges, introduced 2001 to encourage pension saving",
            "max_annual_charge": 0.015,  # 1.5% maximum
            "min_contribution": 20,
            "common_features": ["low_fees", "flexible_contributions", "default_investment", "no_penalties"],
            "typical_providers": ["NEST", "Aviva", "Standard Life", "Legal & General"],
            "fca_considerations": "Designed as accessible, affordable option with consumer protections",
            "status": "Less common since auto-enrollment introduction, replaced by workplace schemes"
        },
        "group_personal_pension": {
            "description": "Personal pensions arranged by employer, each member has individual contract",
            "typical_providers": ["Aviva", "Scottish Widows", "Legal & General", "Aegon"],
            "common_features": ["employer_contributions", "group_negotiated_fees", "individual_ownership", "portability"],
            "typical_fees": {"min": 0.005, "max": 0.01},
            "fca_considerations": "Individual contracts mean pension stays with member if they leave employer",
            "vs_master_trust": "GPP = individual contracts, Master Trust = single trust-based scheme"
        },
        "ssas": {
            "description": "Small Self-Administered Scheme - occupational pension for company directors and key employees",
            "max_members": 11,
            "typical_users": ["company_directors", "family_businesses", "senior_executives"],
            "common_features": ["commercial_property_purchase", "loan_to_employer", "wider_investments", "trustee_control"],
            "typical_setup_costs": (2000, 5000),
            "typical_annual_costs": (1500, 3000),
            "fca_considerations": "Requires professional trustees, complex administration, suitable for sophisticated users only",
            "investment_limits": {
                "employer_loan": 0.50,  # Max 50% of fund
                "commercial_property": "No limit if arm's length transaction"
            }
        },
        "master_trust": {
            "description": "Trust-based multi-employer workplace pension scheme",
            "typical_providers": ["NEST", "The People's Pension", "NOW: Pensions", "Smart Pension"],
            "governance": "Independent trustees oversee scheme",
            "common_features": ["auto_enrollment_compliant", "low_cost", "default_investment", "scale_benefits"],
            "typical_fees": {"min": 0.003, "max": 0.008},
            "fca_considerations": "TPR authorized, subject to additional regulatory oversight",
            "member_protections": ["trustee_oversight", "tpr_authorization", "governance_requirements"]
        },
        "executive_pension_plan": {
            "description": "Pension arrangement for senior employees with employer funding above standard contributions",
            "typical_contribution": (0.15, 0.30),  # 15-30% of salary
            "common_features": ["high_employer_contributions", "flexible_benefits", "death_in_service", "income_protection"],
            "typical_users": ["directors", "senior_management", "key_employees"],
            "fca_considerations": "Often includes additional benefits beyond pension savings",
            "tax_treatment": "Subject to annual allowance, may trigger tapered AA for high earners"
        }
    },
    "regulations": {
        "auto_enrollment": {
            "started": 2012,
            "phased_rollout": "2012-2018, largest to smallest employers",
            "minimum_total_contribution": 0.08,  # 8% total
            "employer_minimum": 0.03,  # 3% minimum from employer
            "employee_minimum": 0.05,  # 5% minimum from employee
            "earnings_trigger_2024_25": 10000,  # Annual earnings threshold
            "lower_qualifying_earnings": 6240,  # Lower limit for qualifying earnings
            "upper_qualifying_earnings": 50270,  # Upper limit for qualifying earnings
            "age_range": (22, "state_pension_age"),
            "eligible_jobholders": "Automatically enrolled",
            "non_eligible_jobholders": "Can opt in, no employer obligation",
            "entitled_workers": "Can opt in, no employer contribution required",
            "opt_out_period": "1 month from enrollment",
            "re_enrollment": "Every 3 years for those who opted out",
            "postponement": "Up to 3 months allowed for employers",
            "penalties": {
                "non_compliance": (400, 10000),  # Daily penalties possible
                "enforcement": "The Pensions Regulator can issue compliance notices"
            }
        },
        "db_transfers": {
            "advice_threshold": 30000,
            "fca_requirement": "Regulated financial advice mandatory for transfers over £30,000",
            "typical_outcome": "FCA presumption that DB transfer not in client's best interest",
            "tvas_requirement": "Transfer Value Analysis System required for DB transfers",
            "appropriate_pension_transfer_analysis": "APTA required from FCA authorized adviser with pension transfer permissions",
            "critical_yield": "Investment return needed to match DB benefits",
            "scheme_consent": "DB scheme trustees may refuse transfer in some circumstances",
            "statutory_discharge": "Trustees discharged of liability once CETV paid",
            "safeguarded_benefits": "DB schemes, GARs, protected TFC all require advice",
            "transfer_restrictions": {
                "public_sector": "Many public sector schemes restrict transfers",
                "unfunded_schemes": "Some unfunded schemes cannot transfer",
                "in_payment": "Pensions already in payment generally cannot transfer"
            },
            "advice_costs": (1500, 5000),  # Typical cost for DB transfer advice
            "fca_high_risk": "DB transfers are high risk - most people better staying in DB"
        },
        "small_pots": {
            "definition": "Pension pot worth less than £10,000",
            "limit_per_year": 3,  # Maximum 3 small pots can be taken per year
            "no_advice_needed": True,
            "common_scenario": "Consolidation of old workplace pensions from multiple jobs",
            "tax_treatment": "25% tax-free, 75% taxed as income",
            "not_trigger_mpaa": "Small pots rule does not trigger MPAA",
            "beneficiary_small_pots": {
                "limit": 30000,  # Higher limit for inherited pensions
                "max_allowed": 2  # Maximum 2 inherited small pots
            },
            "process": "Scheme can pay out without member needing to take other benefits"
        },
        "pension_freedoms_2015": {
            "introduced": "April 2015",
            "key_changes": [
                "Removed requirement to buy annuity",
                "Introduced flexi-access drawdown",
                "UFPLS introduced",
                "Removed 55% death tax",
                "Pension Wise guidance introduced"
            ],
            "age_restriction": 55,  # Minimum age for accessing benefits
            "future_change": "Minimum age rising to 57 from April 2028"
        },
        "pension_scams_regulations": {
            "cold_calling_ban": "Introduced 2019, illegal to cold call about pensions",
            "early_access_warning": "Any offer to access pension before 55 is likely a scam",
            "transfer_restrictions": "Restrictions on transferring to unregulated schemes",
            "scamsmart_campaign": "FCA campaign warning of pension scams",
            "red_flags": [
                "Unsolicited contact",
                "Time pressure",
                "Unusual investments",
                "Upfront fees",
                "Overseas transfers",
                "Promise of guaranteed returns"
            ]
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
            "common_goals": ["consolidation", "access_planning", "understand_options", "maximise_income"],
            "special_considerations": ["protected_tax_free_cash", "guaranteed_annuity_rates", "db_safeguarded_benefits"]
        },
        "divorce_pension_sharing": {
            "typical_age_range": (35, 55),
            "mechanism": "Pension sharing order or pension attachment order",
            "pension_sharing_order": {
                "description": "Clean break - creates new pension for ex-spouse",
                "typical_split": (0.30, 0.50),  # 30-50% common
                "implementation": "Creates separate pension rights"
            },
            "pension_attachment": {
                "description": "Ex-spouse receives share when benefits taken",
                "ongoing_dependency": "Continues link between parties",
                "less_common": "Generally less favoured than sharing orders"
            },
            "considerations": ["cetv_valuation", "offsetting_vs_sharing", "tax_implications", "remarriage_impact"]
        },
        "redundancy": {
            "typical_age": (45, 60),
            "pension_implications": [
                "Loss of employer contributions",
                "Possible early access if over 55",
                "Consideration of consolidation during transition",
                "Impact on retirement planning"
            ],
            "options": {
                "continue_contributions": "Via personal pension if new job",
                "pause_contributions": "No requirement to contribute when not working",
                "early_access": "If over 55, can access existing pensions",
                "consolidation": "Good time to review and consolidate"
            },
            "tax_relief_loss": "Loss of tax relief on employer contributions"
        },
        "ill_health_early_retirement": {
            "minimum_age": None,  # No minimum age for ill health
            "criteria": "Serious ill health preventing work",
            "scheme_specific": "Each pension scheme has own rules",
            "types": {
                "serious_ill_health_lump_sum": {
                    "criteria": "Life expectancy less than 12 months",
                    "tax_treatment": "100% tax free if under 75",
                    "lump_sum_allowance": "Tested against LSDBA (£1,073,100)"
                },
                "ill_health_early_retirement": {
                    "criteria": "Unable to work in own occupation",
                    "db_schemes": "Often enhanced benefits",
                    "dc_schemes": "Normal benefits but earlier access"
                }
            },
            "medical_evidence": "Requires medical certification"
        },
        "career_break": {
            "scenarios": ["parenting", "education", "caring", "sabbatical", "unemployment"],
            "pension_impact": {
                "contribution_gap": "Period without pension contributions",
                "state_pension_credits": "May qualify for NI credits",
                "employer_contributions_lost": "Loss of employer matching"
            },
            "options": {
                "maintain_personal_contributions": "Continue paying into personal pension if affordable",
                "ni_credits": "Claim child benefit for NI credits, caring credits available",
                "return_to_work": "Catch up with carry forward annual allowance"
            }
        },
        "overseas_worker": {
            "scenarios": ["expat", "returning_to_uk", "short_term_overseas", "retiring_abroad"],
            "uk_pensions_overseas": {
                "access_rights": "UK pensions can be accessed from overseas",
                "tax_treatment": "UK tax may apply, plus overseas tax",
                "state_pension_frozen": "State pension frozen in some countries (not EU/EEA)"
            },
            "qrops": {
                "description": "Qualifying Recognised Overseas Pension Scheme",
                "tax_charge": "25% overseas transfer charge unless exceptions apply",
                "exceptions": [
                    "Moving to same country as QROPS",
                    "Remaining UK tax resident for 5 full tax years",
                    "QROPS in EEA country"
                ],
                "fca_warning": "High risk of scams, regulated advice essential"
            },
            "double_taxation": "May be covered by double taxation treaties"
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
        },
        "sipp_fees": {
            "hargreaves_lansdown": {
                "platform_fee": 0.0045,  # 0.45%, capped at £200
                "dealing_charge": 11.95,
                "annual_cap": 200
            },
            "aj_bell": {
                "platform_fee_up_to_250k": 0.0025,  # 0.25%
                "platform_fee_over_250k": 0.002,  # 0.20%
                "dealing_charge": 9.95
            },
            "interactive_investor": {
                "monthly_fee": 12.99,
                "dealing_charge": 5.99,
                "percentage_fee": 0  # Flat fee model
            },
            "fidelity": {
                "platform_fee": 0.0035,  # 0.35%
                "dealing_charge": 10,
                "no_account_fee": True
            }
        },
        "exit_penalties": {
            "market_value_reduction": {
                "description": "MVR applied if withdrawing from with-profits fund in poor conditions",
                "typical_impact": (0, 0.20),  # Can be 0-20%
                "when_applies": "Typically not applied at retirement age"
            },
            "early_exit_charges": {
                "legacy_pensions": "Pre-2001 pensions may have exit charges",
                "post_2001": "Charges capped at 1% if over 55",
                "typical_range": (0, 0.05)  # 0-5%
            },
            "guaranteed_annuity_rate": {
                "description": "Valuable guarantee lost if transfer out",
                "typical_value": "Can be worth tens of thousands",
                "fca_warning": "Requires regulated advice, high risk to transfer"
            }
        },
        "ongoing_costs": {
            "annual_management_charge": (0.003, 0.015),  # 0.3% - 1.5%
            "transaction_costs": (0.001, 0.01),  # 0.1% - 1%
            "fund_specific_costs": "OCF (Ongoing Charges Figure) includes AMC plus other costs",
            "total_cost_range": (0.005, 0.025)  # 0.5% - 2.5% typical total
        },
        "advice_costs": {
            "initial_advice": (500, 3000),
            "db_transfer_advice": (1500, 5000),
            "ongoing_percentage": (0.005, 0.01),  # 0.5% - 1% annual
            "hourly_rate": (150, 300)
        }
    },
    "pension_access_options": {
        "minimum_pension_age": {
            "current": 55,
            "from_april_2028": 57,
            "protected_ages": "Some individuals have protected pension age below 55",
            "ill_health": "No minimum age for serious ill health",
            "exceptions": [
                "Professional sportspeople may have lower age",
                "Those with protected rights from before 2006",
                "Serious ill health at any age"
            ]
        },
        "flexi_access_drawdown": {
            "description": "Take income directly from pension pot while remaining invested",
            "tax_free_cash": "Usually take 25% PCLS first",
            "ongoing_income": "Flexible amounts, taxed as income",
            "mpaa_trigger": "Taking income triggers MPAA (£10k limit on future contributions)",
            "sustainability": {
                "rule_of_thumb": "4% withdrawal rate often suggested",
                "risk": "Pot can run out if withdrawals too high or poor investment returns",
                "flexibility": "Can increase, decrease or stop withdrawals"
            },
            "death_benefits": {
                "before_75": "Beneficiaries receive tax-free",
                "after_75": "Beneficiaries pay tax at their marginal rate"
            },
            "investment_risk": "Remains invested - can go up or down",
            "fca_considerations": "Need to understand investment risk and sustainability"
        },
        "ufpls": {
            "description": "Uncrystallised Funds Pension Lump Sum - take lump sums as needed",
            "tax_treatment": "Each payment: 25% tax-free, 75% taxed as income",
            "mpaa_trigger": "Taking UFPLS triggers MPAA",
            "emergency_tax_risk": "Often emergency taxed on first payment - can reclaim",
            "flexibility": "Don't need to commit to drawdown, take ad-hoc amounts",
            "suitable_for": "One-off needs, testing pension access, small pots",
            "not_suitable_for": "Regular income (drawdown better for tax efficiency)"
        },
        "annuities": {
            "description": "Exchange pension pot for guaranteed income for life",
            "types": {
                "level_annuity": {
                    "description": "Fixed income, no increases",
                    "highest_income": "Provides highest starting income",
                    "inflation_risk": "Income eroded by inflation over time"
                },
                "escalating_annuity": {
                    "description": "Income increases each year",
                    "increase_types": ["fixed_percentage", "rpi_linked", "cpi_linked"],
                    "lower_starting_income": "Starts lower than level annuity"
                },
                "enhanced_annuity": {
                    "description": "Higher income for health conditions or lifestyle factors",
                    "factors": ["smoking", "high_bmi", "medical_conditions", "postcode"],
                    "typical_enhancement": (0.10, 0.50)  # 10-50% higher income
                },
                "joint_life_annuity": {
                    "description": "Continues paying to spouse/partner after death",
                    "spouse_percentage": (0.50, 1.0),  # 50-100% of original
                    "cost": "Lower starting income than single life"
                },
                "value_protected_annuity": {
                    "description": "Guarantees minimum payments (return of capital)",
                    "guarantee_periods": [5, 10],  # Years
                    "lump_sum_on_death": "If die before pot exhausted, balance paid to beneficiaries"
                }
            },
            "rates_context": "Annuity rates vary with interest rates - higher interest rates = higher annuity income",
            "irreversible": "Cannot be undone once purchased",
            "open_market_option": "Can shop around for best rates, not restricted to existing provider",
            "typical_rates_2024": {
                "age_60_male": 0.055,  # £5,500 per year per £100k
                "age_65_male": 0.065,  # £6,500 per year per £100k
                "age_70_male": 0.078   # £7,800 per year per £100k
            }
        },
        "phased_retirement": {
            "description": "Crystallise pension in stages over time",
            "benefits": [
                "Spread tax-free cash over multiple years",
                "Manage income tax liability",
                "Remain invested longer",
                "Flexibility to adjust to circumstances"
            ],
            "tax_efficiency": "Can keep income below higher rate threshold",
            "mpaa_considerations": "Need to avoid triggering MPAA if want to continue high contributions",
            "suitable_for": "Those reducing work hours gradually, phased retirement"
        },
        "tax_free_cash": {
            "also_known_as": "PCLS - Pension Commencement Lump Sum",
            "standard_amount": 0.25,  # 25% of crystallised fund
            "maximum_2024_25": 268275,  # Lump Sum Allowance
            "protected_amounts": "Some individuals have protected higher amounts from before 2024",
            "how_taken": "When crystallise benefits, can take up to 25% as tax-free lump sum",
            "remainder": "Remaining 75% must provide taxable income",
            "no_obligation": "Can take less than 25% or nothing if prefer",
            "one_off_or_staged": "Can take in stages if crystallise pension in phases"
        },
        "capped_drawdown": {
            "status": "Legacy option - no new capped drawdown since April 2015",
            "description": "Pre-2015 drawdown with income capped at 150% of GAD rate",
            "can_convert": "Can convert to flexi-access drawdown",
            "benefits_if_stay": "Doesn't trigger MPAA - can keep contributing full annual allowance",
            "reviews": "Income cap recalculated every 3 years (or annually if over 75)"
        }
    },
    "tax_rules": {
        "annual_allowance": {
            "standard_2024_25": 60000,
            "includes": "All pension contributions (employee + employer + tax relief)",
            "carry_forward": {
                "description": "Can use unused allowance from previous 3 tax years",
                "conditions": "Must have been UK tax resident and member of pension scheme",
                "order": "Use current year first, then previous years oldest first"
            },
            "excess_charge": "Contributions over allowance taxed at marginal rate",
            "claiming_relief": "Tax charge claimed via self-assessment"
        },
        "tapered_annual_allowance": {
            "threshold_income_2024_25": 260000,
            "adjusted_income_2024_25": 360000,
            "reduction_rate": "£1 reduction for every £2 over threshold",
            "minimum_allowance": 10000,
            "calculation": {
                "threshold_income": "Income excluding employer pension contributions",
                "adjusted_income": "Income including employer pension contributions",
                "both_must_exceed": "Both thresholds must be exceeded for taper to apply"
            },
            "affects": "High earners - doctors, lawyers, executives commonly affected"
        },
        "mpaa": {
            "full_name": "Money Purchase Annual Allowance",
            "amount_2024_25": 10000,
            "triggered_by": [
                "Taking flexi-access drawdown income",
                "Taking UFPLS",
                "Taking capped drawdown over cap",
                "Taking scheme pension from small pension"
            ],
            "not_triggered_by": [
                "Taking tax-free cash only",
                "Buying annuity",
                "Taking small pots",
                "Serious ill health lump sum",
                "DB scheme pensions"
            ],
            "irreversible": "Once triggered, applies for rest of life",
            "affects": "Future money purchase (DC) contributions only, not DB",
            "excess_charge": "Contributions over £10k subject to tax charge"
        },
        "lifetime_allowance": {
            "status": "Abolished from April 2024",
            "historical_context": "Previously £1,073,100 limit on total pension savings",
            "replaced_by": "Lump sum allowances (LSA and LSDBA)",
            "protections_remain": "LTA protections still relevant for lump sum allowances"
        },
        "lump_sum_allowances": {
            "lsa": {
                "full_name": "Lump Sum Allowance",
                "amount_2024_25": 268275,  # 25% of old LTA
                "covers": "Tax-free cash (PCLS) and some other tax-free lump sums",
                "excess": "Amounts over LSA taxed at marginal rate"
            },
            "lsdba": {
                "full_name": "Lump Sum and Death Benefit Allowance",
                "amount_2024_25": 1073100,  # Old LTA amount
                "covers": "All lump sums including death benefits paid as lump sums",
                "excess": "Amounts over LSDBA taxed at marginal rate"
            }
        },
        "emergency_tax": {
            "description": "HMRC taxes first pension withdrawal on Month 1 basis assuming repeated monthly",
            "affects": "UFPLS, first drawdown payments, one-off large withdrawals",
            "codes": {
                "month_1_basis": "Assumes income repeated every month",
                "br_code": "Basic rate (20%) deducted from everything",
                "0t_code": "No personal allowance applied"
            },
            "reclaim": {
                "automatic": "Usually corrected by year end through PAYE coding",
                "manual": "Can reclaim immediately using P55, P50Z or P53Z forms",
                "timeframe": "Manual reclaims take 4-8 weeks"
            },
            "how_to_avoid": "Difficult to avoid on first withdrawal, inform provider of tax code if possible"
        },
        "income_tax_on_pensions": {
            "treatment": "Pension income taxed as earned income",
            "personal_allowance_2024_25": 12570,
            "rates_england_wales_ni": {
                "basic_rate": {"rate": 0.20, "bands": (12571, 50270)},
                "higher_rate": {"rate": 0.40, "bands": (50271, 125140)},
                "additional_rate": {"rate": 0.45, "bands": (125141, None)}
            },
            "rates_scotland": {
                "starter_rate": {"rate": 0.19, "bands": (12571, 14876)},
                "basic_rate": {"rate": 0.20, "bands": (14877, 26561)},
                "intermediate_rate": {"rate": 0.21, "bands": (26562, 43662)},
                "higher_rate": {"rate": 0.42, "bands": (43663, 75000)},
                "advanced_rate": {"rate": 0.45, "bands": (75001, 125140)},
                "top_rate": {"rate": 0.48, "bands": (125141, None)}
            },
            "state_pension_interaction": "State pension counts as income, uses up personal allowance"
        },
        "inheritance_tax": {
            "general_treatment": "Pensions normally outside estate for IHT",
            "discretionary_benefit": "Trustees have discretion over beneficiaries - helps avoid IHT",
            "expression_of_wish": "Guides trustees but not binding",
            "exceptions": {
                "death_after_75": "No IHT but income tax on beneficiary withdrawals",
                "deliberate_deprivation": "If pension used to avoid IHT, HMRC may challenge"
            },
            "planning_benefit": "Pensions are IHT-efficient way to pass wealth"
        }
    },
    "state_pension": {
        "new_state_pension": {
            "started": "6 April 2016",
            "eligible": "Men born on or after 6 April 1951, women born on or after 6 April 1953",
            "full_amount_2024_25": 221.20,  # Per week
            "annual_amount": 11502.40,  # 52 weeks
            "qualifying_years_needed": 35,
            "minimum_qualifying_years": 10,
            "triple_lock": "Increases by highest of earnings growth, inflation (CPI), or 2.5%",
            "calculation": "Based on NI record, not previous earnings"
        },
        "old_state_pension": {
            "applies_to": "Those who reached state pension age before 6 April 2016",
            "basic_state_pension_2024_25": 169.50,  # Per week
            "additional_pension": "SERPS or State Second Pension (S2P) on top",
            "graduated_retirement_benefit": "Small additional amount for NI paid 1961-1975"
        },
        "ni_qualifying_years": {
            "how_to_qualify": [
                "Working and paying NI contributions",
                "Receiving NI credits (unemployment, sickness, caring)",
                "Paying voluntary Class 2 or Class 3 contributions"
            ],
            "credits_available": {
                "child_benefit": "For parent claiming child benefit",
                "caring": "Carer's allowance or caring 20+ hours per week",
                "unemployment": "Claiming JSA or UC",
                "sickness": "First 28 weeks of ESA"
            },
            "check_record": "Use 'Check your State Pension' online service",
            "gaps": "Can have gaps filled by voluntary contributions if recent enough"
        },
        "state_pension_age": {
            "current_2024": 66,  # For both men and women
            "rising_to_67": "Between 2026 and 2028",
            "rising_to_68": "Proposed for 2044-2046",
            "check_yours": "Use State Pension age calculator on gov.uk",
            "gender_equalisation": "Completed in 2018, both now the same"
        },
        "deferral": {
            "can_defer": "Don't have to claim State Pension at state pension age",
            "increase_rate": "5.8% for every 52 weeks deferred",
            "no_lump_sum": "Option for lump sum removed from April 2016",
            "when_claimed": "Can claim at any point after deferring",
            "inherited": "Spouse may inherit some of the increase"
        },
        "contracting_out": {
            "ended": "April 2016",
            "what_it_was": "Paid lower NI in exchange for giving up part of additional state pension",
            "gmp": {
                "full_name": "Guaranteed Minimum Pension",
                "description": "Minimum pension that contracted-out scheme must pay",
                "affects": "Reduces state pension entitlement but should be matched by occupational pension"
            },
            "impact_on_entitlement": "Reduces starting amount for new state pension calculation"
        },
        "protected_payments": {
            "description": "Extra amount if entitled to more under old rules than new rules",
            "who_gets": "Those with over 35 qualifying years under old system",
            "how_paid": "Added on top of new state pension flat rate",
            "not_increased": "Protected payment not increased by triple lock"
        },
        "voluntary_contributions": {
            "class_2": {
                "who_for": "Self-employed with profits under small profits threshold",
                "cost_2024_25": 3.45,  # Per week
                "benefit": "Builds qualifying year for state pension"
            },
            "class_3": {
                "who_for": "Filling gaps in NI record",
                "cost_2024_25": 17.45,  # Per week
                "time_limit": "Usually can go back 6 years, sometimes more",
                "worth_checking": "Not always worth it - check with DWP or use online checker"
            },
            "deadline": "Usually 6 years to fill gaps, but check extensions for specific years"
        }
    },
    "transfer_mechanics": {
        "cetv": {
            "full_name": "Cash Equivalent Transfer Value",
            "description": "Lump sum offered by DB scheme in exchange for giving up benefits",
            "validity": "Usually 3 months from quote date",
            "calculation": "Based on actuarial assumptions about future benefits",
            "typical_multiples": {
                "range": (20, 40),  # Times annual pension
                "high_multiples": "High multiples may indicate generous transfer, but still may not be appropriate"
            },
            "factors_affecting": [
                "Age",
                "Years to retirement",
                "Gilt yields",
                "Scheme funding level",
                "Inflation assumptions"
            ],
            "guarantee_period": "Must be guaranteed for at least 3 months"
        },
        "tvas": {
            "full_name": "Transfer Value Analysis System",
            "description": "Compares DB benefits with potential DC outcomes",
            "critical_yield": {
                "description": "Investment return needed to match DB benefits",
                "interpretation": "High critical yield = hard to match DB benefits"
            },
            "discount_rate": "Rate used to value DB benefits in present terms",
            "required_for": "All DB transfers over £30k",
            "limitations": "Based on assumptions - actual outcomes may differ"
        },
        "apta": {
            "full_name": "Appropriate Pension Transfer Analysis",
            "required_for": "DB transfers over £30k",
            "who_can_provide": "FCA authorised advisers with pension transfer permissions",
            "cost": (1500, 5000),
            "fca_presumption": "Presumption that DB transfer not in client's best interest",
            "must_cover": [
                "Comparison of benefits",
                "Risk analysis",
                "Critical yield",
                "Death benefits comparison",
                "Sustainability of income"
            ],
            "insistent_client": "If client insists on transfer against advice, special procedures apply"
        },
        "transfer_timeline": {
            "quote_request": "1-2 weeks for DB CETV quote",
            "advice_process": "2-6 weeks for adviser to complete APTA",
            "implementation": "4-8 weeks for transfer to complete once approved",
            "total_typical": "8-16 weeks from start to finish",
            "delays_possible": "Can be longer if scheme delays or queries arise"
        },
        "exit_penalties": {
            "market_value_reduction": {
                "description": "MVR applied to with-profits funds in poor conditions",
                "when_applied": "More likely in poor market conditions, less likely at retirement age"
            },
            "early_exit_charges": {
                "pre_2001_pensions": "May have substantial exit charges",
                "post_2001_over_55": "Capped at 1% for those over 55",
                "check_required": "Always check for exit penalties before transferring"
            },
            "loss_of_guarantees": "Often most significant 'penalty' is loss of valuable guarantees"
        },
        "loss_of_guarantees": {
            "types": [
                "DB guaranteed income",
                "Guaranteed annuity rates (GAR)",
                "Protected tax-free cash",
                "Inflation protection",
                "Spouse's benefits"
            ],
            "irreversible": "Cannot get guarantees back once transferred",
            "valuation_difficulty": "Hard to put monetary value on guarantees",
            "fca_position": "Guarantees usually more valuable than they appear"
        },
        "pension_scams": {
            "warning_signs": [
                "Unsolicited contact about pension",
                "Pressure to transfer quickly",
                "Offers of 'free pension review'",
                "Access to pension before 55",
                "Overseas investments",
                "Upfront fees",
                "Promises of high guaranteed returns"
            ],
            "common_scam_types": {
                "pension_liberation": "Accessing pension before 55 - leads to 55% tax charge",
                "high_risk_investments": "Pension transferred to SIPP then into high-risk/worthless assets",
                "overseas_scams": "Transfer to overseas scheme, assets disappear"
            },
            "protection": {
                "scamsmart": "FCA ScamSmart campaign provides information",
                "cold_calling_ban": "Cold calling about pensions is illegal since 2019",
                "check_authorisation": "Always check FCA register for adviser authorisation",
                "take_time": "Never rush - legitimate offers won't expire in days"
            },
            "if_scammed": "Report to Action Fraud and FCA, seek legal advice"
        }
    },
    "death_benefits": {
        "dc_before_75": {
            "lump_sum": "Tax-free if paid within 2 years of scheme being notified",
            "drawdown": "Beneficiary can take income tax-free",
            "annuity": "Can be purchased tax-free for beneficiary",
            "leave_invested": "Beneficiary can leave invested and take later tax-free",
            "two_year_rule": "Must be designated within 2 years of scheme informed of death"
        },
        "dc_after_75": {
            "lump_sum": "Taxed at beneficiary's marginal income tax rate",
            "drawdown": "Income taxed at beneficiary's marginal rate",
            "annuity": "Annuity income taxed at beneficiary's marginal rate",
            "no_iht": "Usually no inheritance tax, but income tax applies"
        },
        "db_death_benefits": {
            "death_before_retirement": {
                "lump_sum": "Multiple of salary, e.g. 2-4 times",
                "spouse_pension": "Often 50-66% of member's prospective pension",
                "dependent_children": "May receive pension until adulthood"
            },
            "death_after_retirement": {
                "spouse_pension": "Typically 50-66% of member's pension",
                "guarantee_period": "Some schemes guarantee payments for 5 years",
                "lump_sum": "May be balance of guarantee period"
            }
        },
        "expression_of_wish": {
            "purpose": "Indicates to trustees who should receive benefits",
            "not_binding": "Trustees have discretion - helps keep benefits outside estate",
            "should_update": "Update after major life events (marriage, divorce, children)",
            "iht_benefit": "Non-binding nature helps avoid IHT",
            "nomination_vs_expression": "Nomination may be binding (less common), expression is guidance"
        },
        "beneficiary_options": {
            "lump_sum": "Take entire amount as lump sum",
            "drawdown": "Move into beneficiary's drawdown to take income flexibly",
            "annuity": "Use to purchase annuity for guaranteed income",
            "leave_invested": "Keep invested in original pension wrapper",
            "tax_considerations": "Choice affects tax timing and amount"
        },
        "iht_treatment": {
            "generally_exempt": "Pensions usually outside estate for IHT",
            "scheme_discretion": "Must be under scheme discretion, not member's estate",
            "expression_of_wish_helps": "Non-binding expression helps maintain exemption",
            "hmrc_challenge": "HMRC may challenge if pension clearly used to avoid IHT",
            "age_75_difference": "No IHT but different income tax treatment"
        },
        "small_pots_beneficiary": {
            "limit": 30000,
            "max_payments": 2,
            "tax_treatment": "As per normal death benefit rules based on age",
            "separate_from_member_small_pots": "Different rule from member's 3x £10k small pots"
        }
    },
    "contribution_rules": {
        "tax_relief_mechanisms": {
            "relief_at_source": {
                "description": "Scheme claims basic rate relief, added to pension pot",
                "member_pays": "Net of basic rate",
                "higher_rate_relief": "Higher rate taxpayers claim extra via self-assessment",
                "example": "Pay £80, gets topped up to £100 in pension"
            },
            "net_pay": {
                "description": "Contributions taken before tax calculated",
                "member_pays": "Gross amount minus tax saving",
                "automatic": "Get full relief automatically",
                "low_earners_lose_out": "Those earning under personal allowance get no relief"
            },
            "maximum_relievable": "100% of UK earnings or £3,600 if not earning"
        },
        "salary_sacrifice": {
            "description": "Exchange salary for employer pension contribution",
            "benefits": {
                "employee": "Saves NI as well as income tax",
                "employer": "Saves employer NI (13.8%)",
                "typical_saving": (0.12, 0.15)  # 12-15% for basic rate taxpayer
            },
            "affects": [
                "Salary-based benefits (life insurance, mortgage applications)",
                "Statutory benefits (SMP, SSP)",
                "Income-based benefit claims"
            ],
            "restrictions": "Must not take below National Minimum Wage",
            "reversibility": "Usually can opt out but check scheme rules"
        },
        "employer_contributions": {
            "auto_enrollment_minimum": 0.03,  # 3% of qualifying earnings
            "do_not_count_towards_40k": False,  # They DO count
            "triggers_tapered_aa": "Included in adjusted income calculation",
            "no_earnings_limit": "Employer can contribute even if member has no earnings"
        },
        "contribution_limits": {
            "annual_allowance": 60000,
            "tapered_aa_minimum": 10000,
            "mpaa": 10000,
            "no_lifetime_limit": "LTA abolished April 2024"
        },
        "opt_out_rules": {
            "notice_period": "1 month from enrollment",
            "refund": "If opt out in first month, get contributions refunded",
            "after_first_month": "Can still opt out but contributions stay in pension",
            "re_enrollment": "Employer must re-enroll every 3 years"
        }
    },
    "investment_concepts": {
        "default_funds": {
            "description": "Pre-selected investment option for those who don't choose",
            "typical_structure": "Lifestyle or target date fund",
            "regulation": "Must be appropriate for typical member",
            "majority_use": "80%+ of members stay in default",
            "charge_cap": "0.75% for default funds in auto-enrollment schemes"
        },
        "risk_grading": {
            "typical_scale": (1, 10),  # 1 = lowest risk, 10 = highest risk
            "factors": ["asset_allocation", "volatility", "expected_returns"],
            "lower_risk": "More bonds, cash - lower returns, lower volatility",
            "higher_risk": "More equities - higher potential returns, higher volatility",
            "time_horizon": "Longer time = can take more risk"
        },
        "asset_classes": {
            "cash": {
                "description": "Money market funds, cash deposits",
                "risk": "Very low",
                "returns": "Low - typically below inflation",
                "suitable_for": "Short-term, capital preservation"
            },
            "bonds_gilts": {
                "description": "Government and corporate bonds",
                "risk": "Low to medium",
                "returns": "Modest - above cash, below equities long-term",
                "types": ["government_gilts", "corporate_bonds", "index_linked"]
            },
            "equities": {
                "description": "Shares in companies",
                "risk": "Medium to high",
                "returns": "Higher long-term, volatile short-term",
                "types": ["uk", "global", "emerging_markets"]
            },
            "property": {
                "description": "Commercial property funds",
                "risk": "Medium",
                "returns": "Moderate with income element",
                "liquidity_risk": "Can suspend trading in market stress"
            },
            "alternatives": {
                "description": "Hedge funds, private equity, infrastructure",
                "risk": "Varies - often high",
                "access": "Mainly in larger schemes or SIPPs"
            }
        },
        "lifestyling": {
            "description": "Automatically switches to lower risk as approach retirement",
            "typical_switching": "Starts 5-15 years before retirement",
            "target": "Move from equities to bonds/cash",
            "purpose": "Reduce risk of market crash close to retirement",
            "limitations": "Assumes taking cash/annuity - may not suit drawdown",
            "modern_approach": "Some target different retirement outcomes (drawdown vs annuity)"
        },
        "fund_types": {
            "active_funds": {
                "description": "Fund manager selects investments trying to beat market",
                "higher_fees": (0.005, 0.015),  # 0.5% - 1.5%
                "risk": "May underperform or outperform market"
            },
            "passive_tracker": {
                "description": "Tracks market index (e.g. FTSE 100)",
                "lower_fees": (0.001, 0.005),  # 0.1% - 0.5%
                "return": "Market return minus small fee"
            }
        },
        "passive_vs_active": {
            "passive_benefits": "Lower fees, consistent market returns, transparency",
            "active_benefits": "Potential to beat market, active risk management",
            "evidence": "Most active funds underperform after fees over long term",
            "trend": "Growing shift to passive in workplace pensions"
        }
    },
    "consolidation": {
        "benefits": {
            "easier_management": "One pot easier to track than many",
            "potentially_lower_fees": "Modern schemes often cheaper than old pensions",
            "simpler_death_benefits": "Easier for beneficiaries",
            "better_investment_choice": "May get better options in new scheme"
        },
        "risks": {
            "loss_of_guarantees": "GAR, protected TFC, enhanced transfer values",
            "exit_penalties": "Some old pensions have exit charges",
            "loss_of_death_benefits": "Some old pensions have valuable death benefits",
            "employer_contributions": "Can't consolidate current workplace pension while still contributing"
        },
        "when_not_to": {
            "guaranteed_annuity_rates": "GAR extremely valuable - rarely worth giving up",
            "protected_retirement_age": "Below age 55 - very valuable",
            "db_pensions": "Almost never consolidate DB pensions",
            "with_profits_funds": "May have MVR penalties",
            "final_salary_schemes": "Keep DB schemes separate"
        },
        "process": {
            "steps": [
                "Gather information on all pensions",
                "Check for valuable features/penalties",
                "Compare fees old vs new",
                "Request transfer pack from old scheme",
                "Complete transfer forms",
                "Transfer typically takes 4-8 weeks"
            ],
            "pension_finding_service": "Use govt service to find lost pensions"
        },
        "partial_consolidation": {
            "description": "Consolidate some pensions but keep others",
            "example": "Consolidate old workplace DC pensions, keep DB schemes separate",
            "pragmatic": "Balance benefits of consolidation with risks"
        }
    },
    "provider_landscape": {
        "platforms": {
            "description": "Online investment platforms offering SIPPs and personal pensions",
            "examples": ["Hargreaves Lansdown", "AJ Bell", "Interactive Investor", "Fidelity"],
            "typical_fees": (0.0025, 0.0045),  # 0.25% - 0.45%
            "benefits": "Wide investment choice, online access, consolidated view",
            "suitable_for": "Those comfortable with investment decisions"
        },
        "insurance_companies": {
            "description": "Traditional insurers offering pensions",
            "examples": ["Aviva", "Standard Life", "Legal & General", "Scottish Widows"],
            "typical_fees": (0.005, 0.01),  # 0.5% - 1%
            "products": ["Workplace pensions", "Personal pensions", "Stakeholder"],
            "suitable_for": "Workplace schemes, those wanting guided options"
        },
        "master_trusts": {
            "description": "Multi-employer trust-based schemes",
            "examples": ["NEST", "The People's Pension", "NOW: Pensions", "Smart Pension"],
            "typical_fees": (0.003, 0.008),  # 0.3% - 0.8%
            "governance": "Independent trustees oversee scheme",
            "suitable_for": "Auto-enrollment, small employers",
            "tpr_authorization": "Must be authorized by The Pensions Regulator"
        },
        "workplace_schemes": {
            "types": ["Master trust", "Group personal pension", "Occupational scheme"],
            "choice": "Employer chooses, employee enrolled",
            "portability": "GPP moves with member, trust schemes don't"
        },
        "fee_comparison": {
            "master_trusts_lowest": (0.003, 0.008),
            "insurance_company": (0.005, 0.01),
            "platforms": (0.0025, 0.0045),  # Plus fund fees
            "impact_over_time": "1% extra fee = ~25% less pot over 40 years"
        }
    },
    "regulatory_timeline": {
        "a_day_2006": {
            "date": "6 April 2006",
            "changes": [
                "Simplified pension regime introduced",
                "Lifetime allowance introduced (£1.5m initially)",
                "Annual allowance introduced (£215k initially)",
                "Most restrictions on contributions removed",
                "Protected rights abolished"
            ]
        },
        "auto_enrollment_2012": {
            "date": "October 2012 onwards",
            "changes": [
                "Auto-enrollment phased in largest employers first",
                "Minimum contributions initially 2%, rising to 8% by 2019",
                "NEST launched",
                "Transformed pension coverage - millions enrolled"
            ]
        },
        "pension_freedoms_2015": {
            "date": "6 April 2015",
            "changes": [
                "Removed requirement to buy annuity",
                "Introduced flexi-access drawdown",
                "UFPLS introduced",
                "Pension Wise guidance service launched",
                "55% death tax removed"
            ]
        },
        "pension_dashboard_2025": {
            "date": "Expected 2025",
            "description": "Online service to see all pensions in one place",
            "status": "Delayed multiple times, staging from 2024-2026",
            "benefits": "Find lost pensions, consolidated view, better planning"
        },
        "lta_abolition_2024": {
            "date": "6 April 2024",
            "changes": [
                "Lifetime allowance abolished",
                "Lump sum allowances introduced (LSA £268,275, LSDBA £1,073,100)",
                "No limit on pension pots",
                "Protections still relevant for lump sums"
            ]
        }
    },
    "special_circumstances": {
        "divorce": {
            "pension_sharing_order": {
                "description": "Court orders pension split between spouses",
                "clean_break": "Creates separate pension for ex-spouse",
                "typical_percentage": (0.30, 0.50),
                "implementation": "Each pension valued, percentage applied"
            },
            "pension_attachment_order": {
                "description": "Ex-spouse receives portion when benefits taken",
                "ongoing_link": "Maintains connection between parties",
                "less_common": "Courts prefer sharing orders"
            },
            "offsetting": {
                "description": "Keep pension, give up other assets",
                "example": "Keep pension, ex-spouse keeps more of house",
                "valuation_issues": "Comparing pension to property value difficult"
            }
        },
        "redundancy": {
            "pension_access": "Can access pension if over 55, even if redundant earlier",
            "continuing_contributions": "Stop employer contributions, consider personal contributions",
            "consolidation_opportunity": "Good time to review and consolidate",
            "early_retirement": "Some DB schemes offer early retirement on redundancy"
        },
        "ill_health": {
            "serious_ill_health": {
                "criteria": "Life expectancy less than 12 months",
                "benefit": "100% tax-free lump sum if under 75",
                "no_age_limit": "Can access at any age"
            },
            "ill_health_early_retirement": {
                "criteria": "Unable to work in own occupation",
                "db_schemes": "Often enhanced benefits",
                "dc_schemes": "Normal benefits but can access before 55",
                "medical_evidence": "Requires medical certification"
            }
        },
        "overseas": {
            "uk_pensions_accessible": "Can access UK pensions while living overseas",
            "tax_implications": "May be taxed in UK and overseas",
            "state_pension_frozen": "Frozen in some countries (not EU/EEA)",
            "qrops": {
                "description": "Qualifying Recognised Overseas Pension Scheme",
                "transfer_charge": "25% unless exceptions apply",
                "scam_risk": "High risk area, regulated advice essential"
            }
        },
        "career_breaks": {
            "state_pension_credits": "May qualify for NI credits",
            "contribution_gap": "Period without pension contributions",
            "catch_up": "Use carry forward when return to work"
        },
        "multiple_employment": {
            "multiple_pensions": "Can have pension from each employer",
            "annual_allowance": "All contributions count towards single allowance",
            "consolidation": "May want to consolidate when change jobs"
        }
    },
    "protections": {
        "ppf": {
            "full_name": "Pension Protection Fund",
            "protects": "DB pension schemes if employer becomes insolvent",
            "coverage": {
                "not_yet_retired": "90% of expected pension, capped",
                "already_retired": "100% of pension in payment, capped",
                "cap_2024_25": 41461  # Annual cap for 65 year old
            },
            "funding": "Levy on all eligible DB schemes",
            "does_not_cover": "DC schemes"
        },
        "fscs": {
            "full_name": "Financial Services Compensation Scheme",
            "protects": "If pension provider goes bust",
            "coverage": {
                "investments": "Up to £85,000 per person per firm for deposits",
                "pensions": "100% of value if provider fails",
                "advice": "May compensate for bad advice"
            }
        },
        "fos": {
            "full_name": "Financial Ombudsman Service",
            "purpose": "Free dispute resolution for financial complaints",
            "covers": "Complaints about pension providers and advisers",
            "process": "Must complain to provider first, then can escalate to FOS",
            "awards": "Can award up to £430,000",
            "time_limit": "Usually must complain within 6 years"
        },
        "pension_regulator": {
            "role": "Regulates workplace pension schemes",
            "powers": [
                "Auto-enrollment compliance",
                "DB scheme funding",
                "Master trust authorization",
                "Pension scam prevention"
            ],
            "whistleblowing": "Can report employer non-compliance",
            "enforcement": "Can issue penalties for non-compliance"
        }
    },
    "pension_wise": {
        "description": "Free, impartial government pension guidance",
        "eligibility": "Anyone over 50 with DC pension",
        "cost": "Free",
        "format": ["Phone appointment", "Face to face appointment", "Online guidance"],
        "covers": {
            "topics": [
                "Pension options at retirement",
                "Tax implications",
                "Pension scams",
                "Next steps"
            ],
            "what_it_is_not": "Not personal recommendation - guidance only"
        },
        "vs_regulated_advice": {
            "pension_wise": "Free, impartial guidance, no personal recommendation",
            "regulated_advice": "Paid, personal recommendation, FCA regulated"
        },
        "moneyhelper_integration": {
            "description": "Pension Wise now part of MoneyHelper service",
            "booking": "Book through moneyhelper.org.uk",
            "other_services": "MoneyHelper also offers debt, money and pension guidance"
        },
        "duty_to_refer": "Providers must refer members considering drawdown/annuity to Pension Wise"
    },
    "glossary": {
        "crystallisation": "Converting uncrystallised pension funds to provide benefits - triggers ability to take tax-free cash and income",
        "uncrystallised": "Pension savings not yet accessed - still in accumulation phase",
        "gmp": "Guaranteed Minimum Pension from contracting out - minimum pension contracted-out scheme must pay",
        "pcls": "Pension Commencement Lump Sum - the tax-free cash taken when crystallise benefits (usually 25%)",
        "ufpls": "Uncrystallised Funds Pension Lump Sum - taking ad-hoc lump sums, each 25% tax-free, 75% taxed",
        "mpaa": "Money Purchase Annual Allowance - £10k limit on DC contributions after flexible access",
        "cetv": "Cash Equivalent Transfer Value - lump sum offered by DB scheme to transfer out",
        "tvas": "Transfer Value Analysis System - compares DB benefits with potential DC outcomes",
        "apta": "Appropriate Pension Transfer Analysis - required for DB transfers over £30k",
        "care": "Career Average Revalued Earnings - DB scheme based on average salary over career, not final salary",
        "gar": "Guaranteed Annuity Rate - protected rate for buying annuity, often valuable",
        "ppf": "Pension Protection Fund - protects DB pensions if employer becomes insolvent",
        "fscs": "Financial Services Compensation Scheme - protects if provider goes bust",
        "fos": "Financial Ombudsman Service - free dispute resolution",
        "tpr": "The Pensions Regulator - regulates workplace pensions",
        "nest": "National Employment Savings Trust - master trust for auto-enrollment",
        "sipp": "Self-Invested Personal Pension - pension with wide investment choice",
        "ssas": "Small Self-Administered Scheme - occupational pension for directors, max 11 members",
        "gpp": "Group Personal Pension - personal pensions arranged by employer",
        "ocf": "Ongoing Charges Figure - total annual costs of fund including AMC",
        "amc": "Annual Management Charge - fee for managing investments",
        "drawdown": "Taking income directly from pension while remaining invested",
        "annuity": "Insurance product providing guaranteed income for life in exchange for pension pot",
        "lsa": "Lump Sum Allowance - £268,275 limit on tax-free cash from April 2024",
        "lsdba": "Lump Sum and Death Benefit Allowance - £1,073,100 limit on all lump sums from April 2024",
        "lta": "Lifetime Allowance - abolished April 2024, previously £1,073,100 limit on total pension savings",
        "aa": "Annual Allowance - £60k limit on tax-relieved contributions",
        "tapered_aa": "Reduced annual allowance for high earners - minimum £10k",
        "qrops": "Qualifying Recognised Overseas Pension Scheme - overseas pension that can receive UK transfers",
        "ni": "National Insurance - contributions that build State Pension entitlement",
        "serps": "State Earnings Related Pension Scheme - additional state pension 1978-2002",
        "s2p": "State Second Pension - replaced SERPS 2002-2016",
        "spa": "State Pension Age - age can claim State Pension (currently 66)",
        "mvr": "Market Value Reduction - penalty applied when exit with-profits fund in poor conditions",
        "protected_rights": "Rights from contracting out - restrictions abolished 2006"
    },
    "common_questions": {
        "when_can_access": {
            "question": "When can I access my pension?",
            "answer": "Usually age 55 (rising to 57 from April 2028). Exceptions: serious ill health at any age, protected pension age below 55 for some individuals."
        },
        "how_much_tax_free": {
            "question": "How much tax-free cash can I take?",
            "answer": "Usually 25% of pension pot, maximum £268,275 (Lump Sum Allowance). Some people have protected higher amounts."
        },
        "state_pension_amount": {
            "question": "How much is the State Pension?",
            "answer": "Full new State Pension is £221.20/week (£11,502.40/year) for 2024/25. Need 35 qualifying years for full amount, minimum 10 years for any payment."
        },
        "do_i_have_to_buy_annuity": {
            "question": "Do I have to buy an annuity?",
            "answer": "No. Since 2015 pension freedoms, can choose drawdown, UFPLS, annuity, or combination. Annuity provides guaranteed income but irreversible."
        },
        "should_i_consolidate": {
            "question": "Should I consolidate my pensions?",
            "answer": "Often beneficial (easier management, potentially lower fees) but check for valuable features: guaranteed annuity rates, protected tax-free cash, exit penalties. Never consolidate DB pensions without advice."
        },
        "what_happens_when_i_die": {
            "question": "What happens to my pension when I die?",
            "answer": "DC pension: tax-free to beneficiaries if you die before 75, taxed at their rate if after 75. DB pension: depends on scheme, typically spouse's pension. Usually outside estate for inheritance tax."
        },
        "can_i_access_before_55": {
            "question": "Can I access my pension before 55?",
            "answer": "Only for serious ill health (life expectancy under 12 months). Any other offer to access before 55 is likely a scam. 55% unauthorised payment tax charge applies."
        },
        "how_much_should_i_save": {
            "question": "How much should I save into my pension?",
            "answer": "Common rule: half your age as percentage when start saving. E.g., start at 30, save 15%. Depends on circumstances, existing pensions, state pension, retirement plans."
        },
        "what_fees_do_i_pay": {
            "question": "What fees do I pay on my pension?",
            "answer": "Typically: platform/provider fee (0.3-1%), fund management fee (0.1-1.5%), plus transaction costs. Total often 0.5-2.5%. Check annual statement for exact costs."
        },
        "can_i_still_contribute_when_not_working": {
            "question": "Can I still contribute to a pension when not working?",
            "answer": "Yes. Can contribute up to £3,600 gross per year (£2,880 net) and receive tax relief even with no earnings. May qualify for NI credits for State Pension."
        },
        "should_i_transfer_db_pension": {
            "question": "Should I transfer my DB pension?",
            "answer": "Usually no. FCA presumes DB transfer not in best interest. Guarantees usually very valuable. Must have regulated advice if over £30k. Only consider if exceptional circumstances."
        },
        "what_is_mpaa": {
            "question": "What is MPAA and how do I trigger it?",
            "answer": "Money Purchase Annual Allowance - reduces contribution limit to £10k after flexible access. Triggered by taking drawdown income or UFPLS. NOT triggered by tax-free cash only, annuities, or DB pensions."
        },
        "how_much_income_can_i_take": {
            "question": "How much income can I take in retirement?",
            "answer": "Drawdown: take any amount but risk running out. Rule of thumb: 4% per year sustainable. Depends on pot size, other income, state pension, life expectancy, investment returns."
        },
        "what_is_emergency_tax": {
            "question": "What is emergency tax and can I avoid it?",
            "answer": "HMRC taxes first pension withdrawal assuming repeated monthly - often over-taxes. Usually corrected by year end or reclaim using P55/P50Z/P53Z forms (4-8 weeks). Hard to avoid."
        },
        "can_i_claim_state_pension_overseas": {
            "question": "Can I claim State Pension if I move abroad?",
            "answer": "Yes, can claim UK State Pension overseas. However, frozen (no annual increases) in many countries. Still increases in EU/EEA, Gibraltar, Switzerland, countries with agreements."
        },
        "what_is_pension_wise": {
            "question": "What is Pension Wise?",
            "answer": "Free impartial government guidance for over-50s with DC pensions. Covers options, tax, scams. Guidance only, not personal advice. Book via MoneyHelper."
        },
        "do_pensions_count_for_inheritance_tax": {
            "question": "Do pensions count for inheritance tax?",
            "answer": "Usually no - pensions normally outside estate if trustees have discretion. Expression of wish guides but doesn't bind trustees. Helps avoid IHT but income tax may apply to beneficiaries."
        },
        "can_i_opt_out_of_workplace_pension": {
            "question": "Can I opt out of workplace pension?",
            "answer": "Yes. If opt out within 1 month, get contributions refunded. After 1 month, contributions stay in pension. Lose employer contributions and tax relief. Re-enrolled every 3 years."
        },
        "what_is_carry_forward": {
            "question": "What is pension carry forward?",
            "answer": "Can use unused annual allowance from previous 3 tax years. Must have been UK tax resident and pension scheme member. Use current year first, then previous years oldest first."
        },
        "how_do_i_find_lost_pensions": {
            "question": "How do I find lost pensions?",
            "answer": "Use government's Pension Tracing Service (free). Searches database of pension schemes. Need employer name and rough dates. Can also check old payslips, P60s, letters."
        },
        "what_is_db_vs_dc": {
            "question": "What is the difference between DB and DC pensions?",
            "answer": "DB (Defined Benefit): guaranteed income based on salary and service. DC (Defined Contribution): pot built from contributions, value depends on investments. DB generally more valuable but rare for new pensions."
        },
        "can_i_take_small_pensions": {
            "question": "Can I take small pension pots as cash?",
            "answer": "Yes. Pensions under £10k can use small pots rule - take up to 3 per year, 25% tax-free, 75% taxed. Doesn't trigger MPAA. Useful for consolidating old pots."
        },
        "what_is_tapered_annual_allowance": {
            "question": "What is tapered annual allowance?",
            "answer": "Reduced annual allowance for high earners. Threshold income over £260k and adjusted income over £360k. Reduces by £1 for every £2, minimum £10k. Affects doctors, lawyers, executives."
        },
        "how_pension_tax_relief_works": {
            "question": "How does pension tax relief work?",
            "answer": "Get tax relief at highest rate you pay. Basic rate: £80 contribution becomes £100. Higher rate: claim extra 20% via self-assessment. Additional rate: claim extra 25%. Relief at source or net pay arrangements."
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

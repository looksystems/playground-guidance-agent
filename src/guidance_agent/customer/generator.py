"""Customer profile generation for virtual training.

This module generates diverse, realistic customer profiles for pension guidance
simulations, following the LLM + Knowledge Base coupling approach from Agent Hospital.
"""

import os
import json
import random
from typing import Optional, Tuple, Dict, List
from litellm import completion

from guidance_agent.core.types import (
    CustomerProfile,
    CustomerDemographics,
    FinancialSituation,
    PensionPot,
)


def generate_demographics(
    age_range: Optional[Tuple[int, int]] = None,
    literacy: Optional[str] = None,
) -> CustomerDemographics:
    """Generate realistic customer demographics.

    Args:
        age_range: Optional age range constraint (min, max)
        literacy: Optional literacy level constraint

    Returns:
        CustomerDemographics with realistic UK demographics
    """
    # Determine age
    if age_range:
        age = random.randint(age_range[0], age_range[1])
    else:
        # Sample from realistic UK age distribution
        age_buckets = [
            (22, 30, 0.20),
            (31, 45, 0.30),
            (46, 55, 0.25),
            (56, 67, 0.20),
            (68, 80, 0.05),
        ]
        bucket = random.choices(age_buckets, weights=[b[2] for b in age_buckets])[0]
        age = random.randint(bucket[0], bucket[1])

    # Generate using LLM for realism
    model = os.getenv("LITELLM_MODEL_CUSTOMER", "gpt-4o-mini")

    prompt = f"""Generate realistic UK customer demographics for pension guidance simulation.

Age: {age}
Financial literacy: {literacy if literacy else 'varied'}

Generate JSON with:
- gender: "M" | "F" | "Other"
- location: UK city/region
- employment_status: "employed" | "self-employed" | "unemployed" | "retired"
- occupation: realistic for age (teacher, nurse, engineer, retail worker, etc.)
- financial_literacy: "low" | "medium" | "high"

Ensure:
- Occupation realistic for age and location
- Employment status realistic for age (retired if 65+)
- Diverse occupations and backgrounds
- Financial literacy appropriate to occupation

Return only valid JSON, no explanation."""

    try:
        response = completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
        )

        data = json.loads(response.choices[0].message.content)

        # Override literacy if specified
        if literacy:
            data["financial_literacy"] = literacy

        return CustomerDemographics(
            age=age,
            gender=data.get("gender", "M"),
            location=data.get("location", "London"),
            employment_status=data.get("employment_status", "employed"),
            financial_literacy=data.get("financial_literacy", "medium"),
        )

    except Exception as e:
        # Fallback to simple generation
        return CustomerDemographics(
            age=age,
            gender=random.choice(["M", "F"]),
            location=random.choice(["London", "Manchester", "Birmingham", "Leeds", "Glasgow"]),
            employment_status="employed" if age < 65 else "retired",
            financial_literacy=literacy if literacy else random.choice(["low", "medium", "high"]),
        )


def generate_financial_situation(demographics: CustomerDemographics) -> FinancialSituation:
    """Generate realistic financial situation based on demographics.

    Args:
        demographics: Customer demographics

    Returns:
        FinancialSituation with realistic values for demographics
    """
    model = os.getenv("LITELLM_MODEL_CUSTOMER", "gpt-4o-mini")

    prompt = f"""Generate realistic financial situation for UK pension guidance simulation.

Customer: Age {demographics.age}, {demographics.employment_status}
Location: {demographics.location}

Based on UK statistics:
- Age {demographics.age}
- Employment: {demographics.employment_status}

Generate JSON with:
- annual_income: realistic for age/status (£20k-£80k typically)
- total_assets: pension + savings (age-appropriate)
- total_debt: realistic (mortgage, loans, credit cards)
- dependents: number of dependents (age-appropriate)
- risk_tolerance: "low" | "medium" | "high"

Guidelines:
- Younger: Lower income/assets, possibly higher debt
- Mid-career: Moderate income/assets, family debt
- Near retirement: Higher assets, lower debt
- Retired: Lower income (pension), higher assets
- Unemployed: Minimal income, rely on savings

Return only valid JSON, no explanation."""

    try:
        response = completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        data = json.loads(response.choices[0].message.content)

        return FinancialSituation(
            annual_income=float(data.get("annual_income", 35000)),
            total_assets=float(data.get("total_assets", 50000)),
            total_debt=float(data.get("total_debt", 5000)),
            dependents=int(data.get("dependents", 0)),
            risk_tolerance=data.get("risk_tolerance", "medium"),
        )

    except Exception as e:
        # Fallback based on age
        base_income = 25000 if demographics.age < 30 else 45000 if demographics.age < 50 else 35000
        if demographics.employment_status == "retired":
            base_income = 20000
        elif demographics.employment_status == "unemployed":
            base_income = 10000

        return FinancialSituation(
            annual_income=base_income,
            total_assets=base_income * (demographics.age - 20) / 10,
            total_debt=max(0, base_income * 0.2 if demographics.age < 60 else 0),
            dependents=1 if 30 <= demographics.age <= 55 else 0,
            risk_tolerance="medium",
        )


def generate_pension_pots(
    demographics: CustomerDemographics,
    financial: FinancialSituation,
    num_pots: Optional[int] = None,
) -> List[PensionPot]:
    """Generate realistic pension pots.

    Args:
        demographics: Customer demographics
        financial: Financial situation
        num_pots: Optional number of pots (else determined by age)

    Returns:
        List of PensionPot objects
    """
    # Determine number of pots based on age if not specified
    if num_pots is None:
        if demographics.age < 30:
            num_pots = random.randint(1, 2)
        elif demographics.age < 45:
            num_pots = random.randint(2, 4)
        elif demographics.age < 60:
            num_pots = random.randint(3, 6)
        else:
            num_pots = random.randint(2, 5)

    pots = []
    model = os.getenv("LITELLM_MODEL_CUSTOMER", "gpt-4o-mini")

    for i in range(num_pots):
        # Determine pension type (DB rare for young private sector workers)
        can_have_db = demographics.age > 45 or demographics.employment_status == "retired"
        pot_type = "defined_benefit" if can_have_db and random.random() < 0.15 else "defined_contribution"

        prompt = f"""Generate realistic pension pot details for UK pension guidance simulation.

Customer: Age {demographics.age}, {demographics.employment_status}
Pension pot {i+1} of {num_pots}
Type: {pot_type}

Generate JSON with:
- pot_id: unique identifier (e.g., "pot{i+1}")
- provider: realistic UK provider (NEST, Aviva, Royal London, Standard Life, etc.)
- pot_type: "{pot_type}"
- current_value: realistic for age and career stage (£0-£200k typically)
- projected_value: future value (typically 1.2-1.5x current for DC)
- age_accessible: typically 55 or 58
- is_db_scheme: {str(pot_type == "defined_benefit").lower()}
- db_guaranteed_amount: annual amount if DB, else null

Ensure:
- Values consistent with age {demographics.age}
- DC pensions have current_value > 0
- DB pensions have db_guaranteed_amount > 0
- Realistic providers for pot age
- Older pots may have legacy providers

Return only valid JSON, no explanation."""

        try:
            response = completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )

            data = json.loads(response.choices[0].message.content)

            pot = PensionPot(
                pot_id=data.get("pot_id", f"pot{i+1}"),
                provider=data.get("provider", "NEST"),
                pot_type=data.get("pot_type", "defined_contribution"),
                current_value=float(data.get("current_value", 10000)),
                projected_value=float(data.get("projected_value", 15000)),
                age_accessible=int(data.get("age_accessible", 55)),
                is_db_scheme=bool(data.get("is_db_scheme", False)),
                db_guaranteed_amount=float(data["db_guaranteed_amount"]) if data.get("db_guaranteed_amount") else None,
            )
            pots.append(pot)

        except Exception as e:
            # Fallback generation
            is_db = pot_type == "defined_benefit"
            pot = PensionPot(
                pot_id=f"pot{i+1}",
                provider=random.choice(["NEST", "Aviva", "Royal London", "Standard Life"]),
                pot_type=pot_type,
                current_value=0 if is_db else random.randint(5000, 50000),
                projected_value=0 if is_db else random.randint(8000, 75000),
                age_accessible=55,
                is_db_scheme=is_db,
                db_guaranteed_amount=random.randint(8000, 20000) if is_db else None,
            )
            pots.append(pot)

    return pots


def generate_goals_and_inquiry(
    demographics: CustomerDemographics,
    financial: FinancialSituation,
    pots: List[PensionPot],
) -> Dict[str, str]:
    """Generate customer goals and presenting question.

    Args:
        demographics: Customer demographics
        financial: Financial situation
        pots: Pension pots

    Returns:
        Dict with 'goals' and 'presenting_question'
    """
    model = os.getenv("LITELLM_MODEL_CUSTOMER", "gpt-4o-mini")

    prompt = f"""Generate realistic customer goals and inquiry for pension guidance simulation.

Customer: Age {demographics.age}, {demographics.employment_status}
Financial literacy: {demographics.financial_literacy}
Number of pensions: {len(pots)}
Total pension value: £{sum(p.current_value for p in pots):,.0f}

Generate JSON with:
- goals: customer's main objectives (1-2 sentences)
- presenting_question: what they ask first (natural, conversational, 1-3 sentences)

Ensure:
- Question appropriate for literacy level ("{demographics.financial_literacy}")
- Goals realistic for age {demographics.age}
- Natural conversational tone
- Not overly sophisticated (most aren't pension experts)
- Reflects genuine confusion or need for guidance

Common goals by age:
- 20s-30s: "Understand basics", "Check I'm saving enough"
- 40s: "Consolidate pensions", "Reduce fees", "Plan for retirement"
- 50s-60s: "Maximize retirement income", "Access options", "Tax planning"
- 65+: "Make pension last", "Understand drawdown"

Return only valid JSON, no explanation."""

    try:
        response = completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
        )

        data = json.loads(response.choices[0].message.content)

        return {
            "goals": data.get("goals", "Understand my pensions"),
            "presenting_question": data.get("presenting_question", "Can you help me understand my pension options?"),
        }

    except Exception as e:
        # Fallback based on age
        if demographics.age < 35:
            return {
                "goals": "Understand my pensions and check if I'm saving enough",
                "presenting_question": "I have a few pensions from different jobs. Can you help me understand what I have?",
            }
        elif demographics.age < 55:
            return {
                "goals": "Consolidate my pensions and reduce fees",
                "presenting_question": "Should I combine my pensions into one? I'm not sure what's best.",
            }
        else:
            return {
                "goals": "Plan my retirement and understand my options",
                "presenting_question": "I'm thinking of retiring soon. What are my options for accessing my pension?",
            }


def generate_customer_profile(
    age_range: Optional[Tuple[int, int]] = None,
    complexity: Optional[str] = None,
    literacy: Optional[str] = None,
) -> CustomerProfile:
    """Generate a complete customer profile.

    Args:
        age_range: Optional age range constraint
        complexity: Optional complexity level (simple/moderate/complex)
        literacy: Optional literacy level (low/medium/high)

    Returns:
        Complete CustomerProfile
    """
    # Generate components
    demographics = generate_demographics(age_range=age_range, literacy=literacy)
    financial = generate_financial_situation(demographics)

    # Determine number of pots based on complexity
    if complexity == "simple":
        num_pots = random.randint(1, 2)
    elif complexity == "complex":
        num_pots = random.randint(5, 8)
    else:
        num_pots = None  # Let age determine it

    pots = generate_pension_pots(demographics, financial, num_pots=num_pots)
    goals_inquiry = generate_goals_and_inquiry(demographics, financial, pots)

    # Create profile
    profile = CustomerProfile(
        demographics=demographics,
        financial=financial,
        pensions=pots,
        goals=goals_inquiry["goals"],
        presenting_question=goals_inquiry["presenting_question"],
    )

    return profile


def validate_profile(profile: CustomerProfile) -> Dict[str, any]:
    """Validate customer profile for realism and consistency.

    Args:
        profile: Customer profile to validate

    Returns:
        Dict with 'valid' boolean and 'issues' list
    """
    issues = []

    # Check required fields
    if profile.demographics is None:
        issues.append("Missing demographics")
    if profile.financial is None:
        issues.append("Missing financial situation")
    if not profile.pensions:
        issues.append("No pension pots")
    if not profile.goals:
        issues.append("Missing goals")
    if not profile.presenting_question:
        issues.append("Missing presenting question")

    # Return early if basic validation fails
    if issues:
        return {"valid": False, "issues": issues}

    # Check demographic consistency
    if profile.demographics.age < 22 or profile.demographics.age > 80:
        issues.append(f"Age {profile.demographics.age} outside expected range 22-80")

    if profile.demographics.age >= 68 and profile.demographics.employment_status == "employed":
        issues.append("Unlikely to be employed at age 68+")

    # Check financial realism
    if profile.financial.annual_income < 0:
        issues.append("Negative income")
    if profile.financial.total_assets < 0:
        issues.append("Negative assets")
    if profile.financial.total_debt < 0:
        issues.append("Negative debt")

    # Check pension consistency
    total_pension_value = sum(p.current_value for p in profile.pensions)

    # Young person shouldn't have massive pension value
    if profile.demographics.age < 30 and total_pension_value > 100000:
        issues.append(f"Unrealistically high pension value £{total_pension_value:,.0f} for age {profile.demographics.age}")

    # Check DB pension realism
    db_pensions = [p for p in profile.pensions if p.is_db_scheme]
    if db_pensions and profile.demographics.age < 40:
        issues.append("Unlikely to have DB pension for someone under 40 in private sector")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
    }
